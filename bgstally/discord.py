from datetime import datetime

import requests

from bgstally.activity import Activity
from bgstally.debug import Debug

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S (in-game time)"

class Discord:
    """
    Handle Discord integration
    """
    def __init__(self, bgstally):
        self.bgstally = bgstally


    def post_to_discord(self, Discord, activity: Activity):
        """
        Get all text from the Discord field and post it to the webhook
        """
        if not self.is_webhook_valid(): return

        discord_text = Discord.get('1.0', 'end-1c').strip()
        utc_time_now = datetime.utcnow().strftime(DATETIME_FORMAT)

        if activity.discord_messageid == '' or activity.discord_messageid == None:
            # No previous post
            if discord_text != '':
                discord_text += f"```md\n# Posted at: {utc_time_now}```" # Blue text instead of gray
                url = self.bgstally.state.DiscordWebhook.get()
                response = requests.post(url=url, params={'wait': 'true'}, data={'content': discord_text, 'username': self.bgstally.state.DiscordUsername.get()})
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
                url = f"{self.bgstally.state.DiscordWebhook.get()}/messages/{activity.discord_messageid}"
                response = requests.patch(url=url, data={'content': discord_text, 'username': self.bgstally.state.DiscordUsername.get()})
                if not response.ok:
                    activity.discord_messageid = ''
                    Debug.logger.error(f"Unable to update previous discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")

                    # Try to post new message instead
                    url = self.bgstally.state.DiscordWebhook.get()
                    response = requests.post(url=url, params={'wait': 'true'}, data={'content': discord_text, 'username': self.bgstally.state.DiscordUsername.get()})
                    if response.ok:
                        # Store the Message ID
                        response_json = response.json()
                        activity.discord_messageid = response_json['id']
                    else:
                        Debug.logger.error(f"Unable to create new discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")
            else:
                url = f"{self.bgstally.state.DiscordWebhook.get()}/messages/{activity.discord_messageid}"
                response = requests.delete(url=url)
                if response.ok:
                    # Clear the Message ID
                    activity.discord_messageid = ''
                else:
                    Debug.logger.error(f"Unable to delete previous discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")


    def is_webhook_valid(self):
        """
        Do a basic check on the user specified Discord webhook
        """
        webhook = self.bgstally.state.DiscordWebhook.get()
        return webhook.startswith('https://discordapp.com/api/webhooks/') \
                or webhook.startswith('https://discord.com/api/webhooks/') \
                or webhook.startswith('https://ptb.discord.com/api/webhooks/') \
                or webhook.startswith('https://canary.discord.com/api/webhooks/')
