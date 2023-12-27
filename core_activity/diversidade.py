
import json
import requests

headers = {
    'QB-Realm-Hostname': 'ignetworks.quickbase.com',
    'User-Agent': '{User-Agent}',
    'Authorization': 'QB-USER-TOKEN b77d3x_w4i_0_b5vmciccskkpez3b6bnwbum2vpz'
}
body = {"from": "bfwgbisz4", "select": [
    511, 700], "where": "{7.CT.'OES.571.A001'}"}
r = requests.post(
    'https://api.quickbase.com/v1/records/query',
    headers=headers,
    json=body
)

print(json.dumps(r.json(), indent=4))
