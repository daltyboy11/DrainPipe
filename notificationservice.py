from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

class Notifier:
    def notify(self, messages):
        pass

class TextNotifier(Notifier):
    def __init__(self, api_config, phone_number, silent):
        self.twilio_client = Client(api_config["twilio_sid"], api_config["twilio_auth_token"])
        self.twilio_number = api_config["twilio_phone_number"]
        self.phone_number = phone_number
        self.sentAt = None
        self.silent = silent

    def minutes_between(self, d1, d2):
        return (d2 - d1).total_seconds() / 60
    
    def notify(self, messages):

        print("Sending text notification to {}!".format(self.phone_number))
        if self.silent:
            return None

        # Don't send a notif more than once every 5 min
        if self.sentAt is not None and self.minutes_between(self.sentAt, datetime.now()) < 5:
            print("Skipping... text already sent")
            return 

        try:
            message = self.twilio_client.messages.create(
                to=self.phone_number,
                from_=self.twilio_number,
                body="Hello World!"
            )
            self.sentAt = datetime.now()
            print("Text notification sent")
            print(message)
        except TwilioRestException as err:
            print(err)



class NotificationService:

    """
    Set silent=True to stop the annoying texts for debug
    """
    def __init__(self, api_config: dict, config: dict, silent: bool=False):
        notifiers = []
        if config["channels"]["sms"]["enable"]:
            phone_number = config["channels"]["sms"]["phone_number"]
            text_notifier = TextNotifier(api_config, phone_number, silent=silent)
            notifiers.append(text_notifier)

        self.notifiers = notifiers

    def notify(self, messages):
        for notifier in self.notifiers:
            notifier.notify(messages)
