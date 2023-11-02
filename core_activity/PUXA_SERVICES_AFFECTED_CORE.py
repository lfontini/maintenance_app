
import json
import requests

headers = {
    'QB-Realm-Hostname': 'ignetworks.quickbase.com',
    'User-Agent': '{User-Agent}',
    'Authorization': 'QB-USER-TOKEN b77d3x_w4i_0_b5vmciccskkpez3b6bnwbum2vpz'
}
body = {"from": "bmniuvke2", "select": [], "where": "{10.CT.'2000'}"}
r = requests.post(
    'https://api.quickbase.com/v1/records/query',
    headers=headers,
    json=body
)

print(json.dumps(r.json(), indent=4))
