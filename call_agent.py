from google import auth as google_auth
from google.auth.transport import requests as google_requests
import requests
import json
import os
from github import Github, Auth
from google.cloud import secretmanager

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
pr_number = 2                        # Pull request number
comment_text = "Reviewed requirements.txt: dependencies for gcp-cluster, data engineering, ncu, and others are well organized."
github_token = get_github_pat_secret("github_pat", "vodaf-hack25dus-903")

def get_identity_token():
    credentials, _ = google_auth.default()
    auth_request = google_requests.Request()
    credentials.refresh(auth_request)
    return credentials.token

def comment_on_pr(repo_name, pr_number, comment_text, github_token, filename):
    # Authenticate to GitHub
    auth = Auth.Token(github_token)
    g = Github(auth=auth)    
    print(repo_name)
    repo = g.get_repo(repo_name)
    print(pr_number)
    pr = repo.get_pull(pr_number)
    print("Add Comment")
    pr.create_issue_comment(f"Style check on file {filename}: {comment_text}")

    
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
                comment_on_pr(repo_name, pr_number, data["output"]["output"], github_token, filename)
                

process_sql_files('sql')

