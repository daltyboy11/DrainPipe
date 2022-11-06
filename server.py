import yaml
from pathlib import Path
from subprocess import Popen
import pdb

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

class RequesterData(BaseModel):
    contract_address: str
    channels : dict

@app.get("/")
def hello():
    print('shit is poppin')

@app.post("/initservice")
def initservice(data : RequesterData):

    try:

        # verify/check data
        # write info to config/yaml
        config_path = Path(f'config/{data.contract_address}.yaml')
        config_path.parent.mkdir(parents=True, exist_ok=True)
        yaml.dump(data.dict(), config_path.open(mode='w'))

        # call out to main.py to start
        cmd = ['python', 'main.py', f'{str(config_path)}']
        print(f'Starting process: {" ".join(cmd)}')
        res = Popen(cmd, close_fds=True)
        print(f"Started process with PID {res.pid}")

        # return status
        return {
            "status" : "SUCCESS",
            "data" : data,
            "server_PID": res.pid
        }

    except Exception as err:
        return {
            "status": "FAILED",
            "python_error": err
        }