# Builtin
import time
import json
import sys
from pathlib import Path
from dataclasses import dataclass


# 3rd party
import yaml
from pydantic import BaseModel
  
# Custom
from datamodels import APIConfig
from duneservice import *
from notificationservice import NotificationService


def get_user_config(config_path: Path):

    """This should be the yaml file writter by the server code
    named with the contract address"""
    return yaml.safe_load(config_path.open(mode='r'))


def main():
    assert len(sys.argv) == 2, "Incorrect number of arguments"

    silent = False
    f = open('api_keys.json')
    api_config = APIConfig(**json.load(f))
    f.close()

    # Load user info and configure services
    user_config = get_user_config(Path(sys.argv[1]))
    dune_service = DuneService(api_config, user_config)
    notify_service = NotificationService(api_config, user_config, silent=silent)

    while True:
        print("Running dune query")        
        response = dune_service.run_query_loop()
        print(response)
        if (response == "failed"):
            continue
        
        print(json.dumps(response, indent=2))

        print("Sending notifications async")
        notify_service.notify(response)

        print("Query loop done, sleeping 10s")
        time.sleep(10)

main()
