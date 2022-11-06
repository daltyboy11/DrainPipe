from datetime import datetime
import requests

from notifier import Notifier
from datamodels import APIConfig

class DiscordNotifier(Notifier):
    def __init__(self, api_config: APIConfig, user_config, silent=False):

        self.webhook_url = api_config.discord_webhook_url
        self.server_name = user_config['channels']['discord']['server_name']
        self.collection_address = user_config['contract_address']
        self.collection_name = user_config['collection_name']
        self.sentAt = None
        self.silent = silent

    def minutes_between(self, d1, d2):
        """Get the minutes between two datetime objects"""
        return (d2 - d1).total_seconds() / 60

    def get_msg_body(self, raw_data):
        min_block = float('inf')
        max_block = float('-inf')
        for block in raw_data['blocks']:
            min_block = min(min_block, block['block_num'])
            max_block = max(min_block, block['block_num'])

        wallet_address = raw_data['wallet']
        etherscan_link = f"https://etherscan.io/address/{wallet_address}"

        collection = self.collection_name if self.collection_name is not None else self.collection_address

        if min_block == max_block:
            return f"""
            @everyone Drainpipe detected {raw_data['total_transfers']} transfer(s) for collection {collection} from wallet {wallet_address} recently (block {min_block}). 
            You may want to investigate for potential suspicious activity: {etherscan_link}
            """
        else:
            return f"""
            @everyone Drainpipe detected {raw_data['total_transfers']} transfer(s) for collection {collection} from wallet {wallet_address} recently (from block {min_block}:{max_block}). 
            You may want to investigate for potential suspicious activity: {etherscan_link}
            """            
        
    def notify(self, raw_data):

        message = self.get_msg_body(raw_data)
        print(f"Sending discord notification to {self.webhook_url} | {self.server_name}")
        print(f"Msg to send is {message}")

        if self.silent:
            return

        if self.sentAt is not None and self.minutes_between(self.sentAt, datetime.now()) < 5:
            print("Skipping... text already sent")
            return 

        try:
            json_message = {
                "content": message
            }
            requests.post(url=self.webhook_url, json=json_message)
            self.sentAt = datetime.now()
            print("Discord notification sent")

        except Exception as err:
            print(err)
