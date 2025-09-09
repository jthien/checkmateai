from google import auth as google_auth
from google.auth.transport import requests as google_requests
import requests

def get_identity_token():
    credentials, _ = google_auth.default()
    auth_request = google_requests.Request()
    credentials.refresh(auth_request)
    return credentials.token

response = requests.post(
    f"https://us-central1-aiplatform.googleapis.com/v1/projects/vodaf-hack25dus-903/locations/us-central1/reasoningEngines/7261706953460547584:query",
    headers={
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {get_identity_token()}",
    },
    data=json.dumps({
        "class_method": "query",
        "input": {
            "input": "What is the exchange rate from US dollars to Swedish Krona today?"
        }
    })
)

