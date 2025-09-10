from google import auth as google_auth
from google.auth.transport import requests as google_requests
import requests
import json
import os
from github import Github, Auth
from google.cloud import secretmanager
import argparse

def get_github_pat_secret(secret_id, project_id):
    """
    Reads the GitHub PAT secret from Google Cloud Secret Manager.

    Args:
        secret_id (str): The secret name (e.g., "github_pat").
        project_id (str): Your GCP project ID.

    Returns:
        str: The secret value.
    """
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": secret_name})
    secret_value = response.payload.data.decode("UTF-8")
    return secret_value


# Example usage:
repo_name = "jthien/checkmateai"  # e.g. "joerg-thienenkamp/utilities"
comment_text = "Reviewed requirements.txt: dependencies for gcp-cluster, data engineering, ncu, and others are well organized."
github_token = get_github_pat_secret("github_pat", "vodaf-hack25dus-903")

parser = argparse.ArgumentParser(description='To parse command line arguments passed by the user.')
parser.add_argument('-p', "--pull_request",type=int,help="Enter PR Number", default=None, required=True)
args = parser.parse_args()

#pr_number = 2                        # Pull request number
pr_number=args.pull_request
print(f"Get PR {pr_number}")


def get_identity_token():
    credentials, _ = google_auth.default()
    auth_request = google_requests.Request()
    credentials.refresh(auth_request)
    return credentials.token

def comment_on_pr(pr_number, comment_text, filename):
    # Authenticate to GitHub
    auth = Auth.Token(github_token)
    g = Github(auth=auth)    
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    pr.create_issue_comment(f"CheckMateAI Style check result for file {filename}: {comment_text}")

def get_pr_files(pr_number):
    # Authenticate to GitHub
    auth = Auth.Token(github_token)
    g = Github(auth=auth)    
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    result_list = []    
    for file in pr.get_files():
        result_list.append(file.filename)
            
    return result_list

    
def check_sql_rule_agent(sql_file):
    with open(sql_file, 'r') as f:
        content = f.read()
        
    response = requests.post(
        # Nicolai
        f"https://us-central1-aiplatform.googleapis.com/v1/projects/vodaf-hack25dus-903/locations/us-central1/reasoningEngines/7261706953460547584:query",
        # Dhirain - not working
        #f"https://us-central1-aiplatform.googleapis.com/v1/projects/vodaf-hack25dus-903/locations/us-central1/reasoningEngines/6463162444532416512:query",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {get_identity_token()}",
        },
        data=json.dumps({
            "class_method": "query",
            "input": {
                "input": f"Your are a database expert and have review the formatting of SQLs. Suggest enhancements for SQL: {content}"
            }
        })
    
    )
    
    return response


# To check all sql file in sql folder
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
                comment_on_pr(pr_number, data["output"]["output"], filename)
                
def process_pr_files(root_folder):
    for filename in get_pr_files(pr_number):
        if filename.endswith('.sql'):
            print (f"Style check for {filename}")
            #file_path = os.path.join(foldername, filename)

            response = check_sql_rule_agent(filename)
            print(response.text)
            data = json.loads(response.text)

            # Print output.output
            #print(data["output"]["output"])
            comment_on_pr(pr_number, data["output"]["output"], filename)

#process_sql_files('sql')
process_pr_files('sql')

