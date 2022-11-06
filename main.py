
import time
import json
import sys
from pathlib import Path
import yaml

from duneservice import *
from notificationservice import NotificationService

def get_notif_config(config_path: Path):

    """This should be the yaml file writter by the server code
    named with the contract address"""
    return yaml.safe_load(config_path.open(mode='r'))


def main():
    assert len(sys.argv) == 2, "Incorrect number of arguments"

    silent = True
    f = open('api_keys.json')
    api_config = json.load(f)
    f.close()

    # Load user info
    user_config = get_notif_config(Path(sys.argv[1]))


    ###########
    # FIX ME
    dune_service = DuneService(api_config)
    ns = NotificationService(api_config, user_config, silent=silent)

    while True:
        print("Running dune query")
        response = dune_service.run_query_loop()
        if (response == "failed"):
            continue
        
        print(json.dumps(response, indent=2))

        print("Sending notifications async")
        ns.notify(response)

        print("Query loop done, sleeping 10s")
        time.sleep(10)

main()
