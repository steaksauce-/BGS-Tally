from datetime import datetime
from typing import Dict, List

import requests

from bgstally.debug import Debug

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S (in-game time)"
URL_CLOCK_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Fxemoji_u1F556.svg/240px-Fxemoji_u1F556.svg.png"

class Discord:
    """
    Handle Discord integration
    """
    def __init__(self, bgstally):
        self.bgstally = bgstally


    def post_to_discord_plaintext(self, discord_text: str, previous_messageid: str):
        """
        Post plain text to Discord
        """
        if not self.is_webhook_valid(): return

        utc_time_now = datetime.utcnow().strftime(DATETIME_FORMAT)
        new_messageid = previous_messageid

        if previous_messageid == "" or previous_messageid == None:
            # No previous post
            if discord_text != "":
                discord_text += f"```md\n# Posted at: {utc_time_now}```" # Blue text instead of gray
                url = self.bgstally.state.DiscordWebhook.get()
                response = requests.post(url=url, params={'wait': 'true'}, data={'content': discord_text, 'username': self.bgstally.state.DiscordUsername.get()})
                if response.ok:
                    # Store the Message ID
                    response_json = response.json()
                    new_messageid = response_json['id']
                else:
                    Debug.logger.error(f"Unable to create new discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")

        else:
            # Previous post, amend or delete it
            if discord_text != '':
                discord_text += f"```diff\n+ Updated at: {utc_time_now}```"
                url = f"{self.bgstally.state.DiscordWebhook.get()}/messages/{previous_messageid}"
                response = requests.patch(url=url, data={'content': discord_text, 'username': self.bgstally.state.DiscordUsername.get()})
                if not response.ok:
                    new_messageid = ""
                    Debug.logger.error(f"Unable to update previous discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")

                    # Try to post new message instead
                    url = self.bgstally.state.DiscordWebhook.get()
                    response = requests.post(url=url, params={'wait': 'true'}, data={'content': discord_text, 'username': self.bgstally.state.DiscordUsername.get()})
                    if response.ok:
                        # Store the Message ID
                        response_json = response.json()
                        new_messageid = response_json['id']
                    else:
                        Debug.logger.error(f"Unable to create new discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")
            else:
                url = f"{self.bgstally.state.DiscordWebhook.get()}/messages/{previous_messageid}"
                response = requests.delete(url=url)
                if response.ok:
                    # Clear the Message ID
                    new_messageid = ""
                else:
                    Debug.logger.error(f"Unable to delete previous discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")

        return new_messageid


    def post_to_discord_embed(self, title: str, description: str, fields: List, previous_messageid: str):
        """
        Post an embed to Discord
        """
        if not self.is_webhook_valid(): return

        new_messageid = previous_messageid

        if previous_messageid == "" or previous_messageid == None:
            # No previous post
            embed = self._get_embed(title, description, fields, False)
            url = self.bgstally.state.DiscordWebhook.get()
            response = requests.post(url=url, params={'wait': 'true'}, json={'username': self.bgstally.state.DiscordUsername.get(), 'embeds': [embed]})
            if response.ok:
                # Store the Message ID
                response_json = response.json()
                new_messageid = response_json['id']
            else:
                Debug.logger.error(f"Unable to create new discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")

        else:
            # Previous post, amend or delete it
            embed = self._get_embed(title, description, fields, True)
            url = f"{self.bgstally.state.DiscordWebhook.get()}/messages/{previous_messageid}"
            response = requests.patch(url=url, json={'username': self.bgstally.state.DiscordUsername.get(), 'embeds': [embed]})
            if not response.ok:
                new_messageid = ""
                Debug.logger.error(f"Unable to update previous discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")

                # Try to post new message instead
                url = self.bgstally.state.DiscordWebhook.get()
                response = requests.post(url=url, params={'wait': 'true'}, json={'username': self.bgstally.state.DiscordUsername.get(), 'embeds': [embed]})
                if response.ok:
                    # Store the Message ID
                    response_json = response.json()
                    new_messageid = response_json['id']
                else:
                    Debug.logger.error(f"Unable to create new discord post. Reason: '{response.reason}' Content: '{response.content}' URL: '{url}'")

        return new_messageid


    def _get_embed(self, title: str, description: str, fields: List, update: bool):
        """
        Create a Discord embed JSON structure. If supplied, `fields` should be a List of Dicts, with each Dict containing 'name' (the field title) and
        'value' (the field contents)
        """
        if not self.is_webhook_valid(): return
        footer_timestamp = f"Updated at {datetime.utcnow().strftime(DATETIME_FORMAT)}" if update else f"Posted at {datetime.utcnow().strftime(DATETIME_FORMAT)}"
        footer_version = f"{self.bgstally.plugin_name} v{self.bgstally.version}"
        footer_pad = 111 - len(footer_version)

        embed:Dict = {
            "color": 10682531,
            "footer": {
                "text": f"{footer_timestamp: <{footer_pad}}{footer_version}",
                "icon_url": URL_CLOCK_IMAGE
            }}

        if title: embed['title'] = title
        if description: embed['description'] = description
        if fields: embed['fields'] = fields

        return embed


    def is_webhook_valid(self):
        """
        Do a basic check on the user specified Discord webhook
        """
        webhook = self.bgstally.state.DiscordWebhook.get()
        return webhook.startswith('https://discordapp.com/api/webhooks/') \
                or webhook.startswith('https://discord.com/api/webhooks/') \
                or webhook.startswith('https://ptb.discord.com/api/webhooks/') \
                or webhook.startswith('https://canary.discord.com/api/webhooks/')
