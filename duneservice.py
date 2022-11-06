from requests import get, post
from web3 import Web3
import time

BASE_URL = "https://api.dune.com/api/v1/"

QUERIES = {
    "nft-transfers-grouped-by-block": "1531241"
}


class DuneService:
    def __init__(self, config):
        self.api_key = config['dune_api_key']
        self.w3 = Web3(Web3.HTTPProvider(config['alchemy_polygon_url']))

    def get_headers(self):
        return {"x-dune-api-key" : self.api_key}
    
    def gen_query_params(self):
        # end_block = get_latest_block_num()
        # start_block = end_block - 10000
        # end_block = 15575300
        # start_block = 13276755
        params={
            "contract": "0xa9348471D0c803f0f05fB04E94ae737e1A36F248",
            "start_block": "0",
            "end_block": "99999999",
            "min_transfers": "0",
        }
        return params

    def get_latest_block_num(self):
        return self.w3.eth.block_number

    def make_api_url(self, module, action, ID):
        """
        We shall use this function to generate a URL to call the API.
        """
        url = BASE_URL + module + "/" + ID + "/" + action
        return url

    def execute_query(self, query_id, params=None):
        """
        Takes in the query ID.
        Calls the API to execute the query.
        Returns the execution ID of the instance which is executing the query.
        """

        url = self.make_api_url("query", "execute", query_id)
        headers = self.get_headers()
        if params is None:
            response = post(url, headers=headers)
        else:
            response = post(url, headers=headers, json={"query_parameters": params})

        if 'execution_id' in response.json():
            return response.json()['execution_id']
        else:
            raise response.json()['error']


    def get_query_status(self, execution_id):
        """
        Takes in an execution ID.
        Fetches the status of query execution using the API
        Returns the status response object
        """

        url = self.make_api_url("execution", "status", execution_id)
        response = get(url, headers=self.get_headers())

        return response

    def get_query_results(self, execution_id):
        """
        Takes in an execution ID.
        Fetches the results returned from the query using the API
        Returns the results response object
        """

        url = self.make_api_url("execution", "results", execution_id)
        response = get(url, headers=self.get_headers())

        return response

    def cancel_query_execution(self, execution_id):
        """
        Takes in an execution ID.
        Cancels the ongoing execution of the query.
        Returns the response object.
        """

        url = self.make_api_url("execution", "cancel", execution_id)
        response = get(url, headers=HEADER)

        return response

    def post_process_query_result(self, response):
        result = response['result']
        rows = result['rows']
        grouped_by_from = {}
        for row in rows:
            addr = row['from']
            block_data = {
                'block_num': row['block_number'],
                'num_transfers': row['num_transfers']
            }
            if addr in grouped_by_from:
                grouped_by_from[addr]['total_transfers'] += row['num_transfers']
                grouped_by_from[addr]['blocks'].append(block_data)
            else:
                grouped_by_from[addr] = {
                    'total_transfers': row['num_transfers'],
                    'blocks': [block_data]
                }
        return grouped_by_from

    def run_query_loop(self):
        query_id = QUERIES["nft-transfers-grouped-by-block"]
        execution_id = self.execute_query(query_id, params=self.gen_query_params())
        response = self.get_query_status(execution_id).json()

        while response['state'] != 'QUERY_STATE_COMPLETED' and response['state'] != 'QUERY_STATE_FAILED':
            print('query {}, sleeping 5s...'.format(response['state']))
            time.sleep(5.0)
            response = self.get_query_status(execution_id).json()

        response = self.get_query_results(execution_id).json()

        if (response['state'] == 'QUERY_STATE_FAILED'):
            print("Dune query failed!")
            print(response)
            return "failed"
        else:
            return self.post_process_query_result(response)
