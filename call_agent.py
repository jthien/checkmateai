from google import auth as google_auth
from google.auth.transport import requests as google_requests
import requests
import json
import os

def get_identity_token():
    credentials, _ = google_auth.default()
    auth_request = google_requests.Request()
    credentials.refresh(auth_request)
    return credentials.token

def check_sql_rule_agent(sql_file):
    with open(sql_file, 'r') as f:
        content = f.read()
        
    response = requests.post(
        f"https://us-central1-aiplatform.googleapis.com/v1/projects/vodaf-hack25dus-903/locations/us-central1/reasoningEngines/7261706953460547584:query",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {get_identity_token()}",
        },
        data=json.dumps({
            "class_method": "query",
            "input": {
                "input": f"SQL Stype check for: {content}"
            }
        })
    )
    
    return response


def process_sql_files(root_folder):
    for foldername, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.sql'):
                print (f"Style check for {filename}")
                file_path = os.path.join(foldername, filename)
                
                response = check_sql_rule_agent(file_path)
                data = json.loads(response.text)

                # Print output.output
                print(data["output"]["output"])
                

process_sql_files('sql')

