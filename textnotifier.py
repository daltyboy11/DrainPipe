from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from notifier import Notifier

class TextNotifier(Notifier):
    def __init__(self, api_config, phone_number, collection_address, collection_name, silent):
        self.twilio_client = Client(api_config["twilio_sid"], api_config["twilio_auth_token"])
        self.twilio_number = api_config["twilio_phone_number"]
        self.phone_number = phone_number
        self.collection_address = collection_address
        self.collection_name = collection_name
        self.sentAt = None
        self.silent = silent

    def minutes_between(self, d1, d2):
        """Get the minutes between two datetime objects"""
        return (d2 - d1).total_seconds() / 60

    def get_text_msg_body(self, raw_data):
        min_block = float('inf')
        max_block = float('-inf')
        for block in raw_data['blocks']:
            min_block = min(min_block, block['block_num'])
            max_block = max(min_block, block['block_num'])

        etherscan_link = 'https://etherscan.io/address/{}'.format(raw_data['wallet'])

        collection = self.collection_name if self.collection_name is not None else self.collection_address

        if min_block == max_block:
            return """
            Hey! We noticed {} transfer(s) for collection {} from your wallet recently (block {}). You may want to investigate for potential suspicious activity: {}
            """.format(raw_data['total_transfers'], collection, min_block, etherscan_link)
        else:
            return """
            Hey! We noticed {} transfer(s) for collection {} from your wallet recently (from block {} to {}). You may want to investigate for potential suspicious activity: {}
            """.format(raw_data['total_transfers'], collection, min_block, max_block, etherscan_link)
        
    def notify(self, raw_data):
        print("Sending text notification to {}!".format(self.phone_number))
        print("Msg to send is {}".format(self.get_text_msg_body(raw_data)))

        if self.silent:
            return

        if self.sentAt is not None and self.minutes_between(self.sentAt, datetime.now()) < 5:
            print("Skipping... text already sent")
            return 

        try:
            message = self.twilio_client.messages.create(
                to=self.phone_number,
                from_=self.twilio_number,
                body=self.get_text_msg_body(raw_data)
            )
            self.sentAt = datetime.now()
            print("Text notification sent")
            print(message)
        except TwilioRestException as err:
            print(err)
