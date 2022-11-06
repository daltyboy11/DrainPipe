from pydantic import BaseModel

class APIConfig(BaseModel):
    twilio_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    dune_api_key: str
    alchemy_polygon_url: str
    discord_webhook_url: str
    
class RequesterData(BaseModel):
    # min_transfers: int
    contract_address: str
    collection_name: str
    channels : dict