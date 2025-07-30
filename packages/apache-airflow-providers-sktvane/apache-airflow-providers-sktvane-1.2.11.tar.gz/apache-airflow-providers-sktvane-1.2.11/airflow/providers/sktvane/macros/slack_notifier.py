from functools import cached_property

import pendulum
from airflow.notifications.basenotifier import BaseNotifier
from airflow.providers.slack.hooks.slack import SlackHook
from airflow.utils.context import Context
from slack_sdk.errors import SlackApiError

from ..macros.vault import get_secrets


class SlackNotifier(BaseNotifier):
    template_fields = (
        "slack_channel",
        "slack_username",
        "slack_email",
    )

    def __init__(self, slack_channel, slack_username, slack_email):
        super().__init__()
        self.slack_channel = slack_channel
        self.slack_username = slack_username
        self.slack_email = slack_email

    @cached_property
    def slack_hook(self) -> SlackHook:
        return SlackHook(
            proxy=get_secrets(path="proxy")["proxy"],
        )

    def _get_user_id_by_email(self) -> str:
        try:
            response = self.slack_hook.client.users_lookupByEmail(
                email=self.slack_email
            )
            user_id = response.get("user")["id"]
            return f"<@{user_id}>"
        except SlackApiError:
            return "UNREGISTERED"

    @staticmethod
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

    def notify(self, context):
        user_id = self._get_user_id_by_email()
        self.slack_hook.client.chat_postMessage(
            channel=self.slack_channel,
            username=self.slack_username,
            blocks=self._generate_fail_alert_blocks(
                context=context,
                user_id=user_id,
            ),
        )
