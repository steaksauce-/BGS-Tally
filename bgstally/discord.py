from datetime import datetime

import requests

from bgstally.activity import Activity
from bgstally.debug import Debug
from bgstally.state import State

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S (in-game time)"

class Discord:
    """
    Handle Discord integration
    """
    def __init__(self, state: State):
        self.state = state


    def post_to_bgs_discord(self, Discord, activity: Activity):
        """
        Get all text from the Discord field and post it to the webhook
        """
        if not self.is_bgs_webhook_valid(): return

        discord_text = Discord.get('1.0', 'end-1c').strip()
        utc_time_now = datetime.utcnow().strftime(DATETIME_FORMAT)

        if activity.discord_messageid == '' or activity.discord_messageid == None:
            # No previous post
            if discord_text != '':
                discord_text += f"```md\n# Posted at: {utc_time_now}```" # Blue text instead of gray
                url = self.state.DiscordWebhook.get()
                response = requests.post(url=url, params={'wait': 'true'}, data={'content': discord_text, 'username': self.state.DiscordUsername.get()})
                if response.ok:
                    # Store the Message ID
                    response_json = response.json()
                    activity.discord_messageid = response_json['id']
                else:
                    Debug.logger.error(f"Unable to create new discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")

        else:
            # Previous post, amend or delete it
            if discord_text != '':
                discord_text += f"```diff\n+ Updated at: {utc_time_now}```"
                url = f"{self.state.DiscordWebhook.get()}/messages/{activity.discord_messageid}"
                response = requests.patch(url=url, data={'content': discord_text, 'username': self.state.DiscordUsername.get()})
                if not response.ok:
                    activity.discord_messageid = ''
                    Debug.logger.error(f"Unable to update previous discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")

                    # Try to post new message instead
                    url = self.state.DiscordWebhook.get()
                    response = requests.post(url=url, params={'wait': 'true'}, data={'content': discord_text, 'username': self.state.DiscordUsername.get()})
                    if response.ok:
                        # Store the Message ID
                        response_json = response.json()
                        activity.discord_messageid = response_json['id']
                    else:
                        Debug.logger.error(f"Unable to create new discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")
            else:
                url = f"{self.state.DiscordWebhook.get()}/messages/{activity.discord_messageid}"
                response = requests.delete(url=url)
                if response.ok:
                    # Clear the Message ID
                    activity.discord_messageid = ''
                else:
                    Debug.logger.error(f"Unable to delete previous discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")


    def post_to_fcjump_discord(self, discord_text:str):
        """
        Get all text from the Discord field and post it to the webhook
        """
        if not self.is_fcjump_webhook_valid(): return

        Debug.logger.info(discord_text)

        # Try to post new message instead
        url = self.state.DiscordFCJumpWebhook.get()
        response = requests.post(url=url, params={'wait': 'true'}, data={'content': discord_text, 'username': self.state.DiscordUsername.get()})
        if not response.ok:
            Debug.logger.error(f"Unable to create new discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")


    def is_bgs_webhook_valid(self):
        """
        Do a basic check on the user specified BGS Discord webhook
        """

        return self._is_webhook_valid(self.state.DiscordBGSWebhook.get())


    def is_fcjump_webhook_valid(self):
        """
        Do a basic check on the user specified Fleet Carrier Discord webhook
        """
        return self._is_webhook_valid(self.state.DiscordFCJumpWebhook.get())


    def _is_webhook_valid(self, webhook:str):
        """
        Do a basic check on a Discord webhook
        """
        return webhook.startswith('https://discordapp.com/api/webhooks/') \
                or webhook.startswith('https://discord.com/api/webhooks/') \
                or webhook.startswith('https://ptb.discord.com/api/webhooks/') \
                or webhook.startswith('https://canary.discord.com/api/webhooks/')