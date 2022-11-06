from textnotifier import TextNotifier
from discordnotifier import DiscordNotifier

from datamodels import APIConfig

class NotificationService:

    """
    Set silent=True to stop the annoying texts for debug
    """
    def __init__(self, api_config: APIConfig, user_config: dict, silent: bool):
        notifiers = []
        if user_config["channels"]["sms"]["enable"]:
            phone_number = user_config["channels"]["sms"]["phone_number"]
            text_notifier = TextNotifier(
                api_config,
                phone_number,
                user_config["contract_address"],
                user_config["collection_name"] if "collection_name" in user_config else None,
                silent=silent
            )
            notifiers.append(text_notifier)

        if user_config["channels"]["discord"]["enable"]:
            discord_notifier = DiscordNotifier(
                api_config,
                user_config
            )
            notifiers.append(discord_notifier)

        self.notifiers = notifiers

    def notify(self, raw_data):
        for notifier in self.notifiers:
            notifier.notify(raw_data)
