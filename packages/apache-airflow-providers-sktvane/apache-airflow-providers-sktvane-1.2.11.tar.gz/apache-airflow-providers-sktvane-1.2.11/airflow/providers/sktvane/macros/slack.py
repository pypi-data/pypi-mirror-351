import pendulum
from airflow.providers.slack.hooks.slack import SlackHook
from airflow.utils.context import Context
from slack_sdk.errors import SlackApiError

from ..macros.vault import get_secrets

slack_hook = SlackHook(
    token=get_secrets(path="airflow_k8s/slack/slack_alarmbot_token")["token"],
    proxy=get_secrets(path="proxy")["proxy"],
)


def send_fail_message(
    slack_channel: str,
    slack_username: str,
    slack_email: str,
):
    def _get_user_id_by_email() -> str:
        try:
            response = slack_hook.client.users_lookupByEmail(email=slack_email)
            user_id = response.get("user")["id"]
            return f"<@{user_id}>"
        except SlackApiError:
            return "UNREGISTERED"

    def _generate_fail_alert_blocks(context: Context, user_id: str) -> list:
        ti = context["ti"]
        logical_date = (
            pendulum.parse(context["ts"]).in_tz("UTC").strftime("%Y-%m-%d %H:%M:%S %Z")
        )
        kst_run = (
            pendulum.timezone("Asia/Seoul")
            .convert(context["data_interval_end"])
            .strftime("%Y-%m-%d %H:%M:%S %Z")
        )
        block = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": ":alert: DAG TASK FAIL ALERT :alert:",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Dag*: `{ti.dag_id}`\n*Task*: `{ti.task_id}`\n*Logical Date(UTC)*: `{logical_date}`\n"
                    f"*Run Date(KST)*: `{kst_run}`\n*Task Duration*: `{ti.duration} seconds`",
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": ":red_circle: Fail Log"},
                    "style": "danger",
                    "url": ti.log_url,
                },
                "fields": [
                    {"type": "mrkdwn", "text": f"*Dag Owner*: {user_id}"},
                ],
            },
            {"type": "divider"},
        ]
        return block

    def callback(context: Context) -> None:
        user_id = _get_user_id_by_email()
        slack_hook.client.chat_postMessage(
            channel=slack_channel,
            username=slack_username,
            blocks=_generate_fail_alert_blocks(
                context=context,
                user_id=user_id,
            ),
        )

    return callback
