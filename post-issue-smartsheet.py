import requests
import smartsheet
import logging
import os
import time

SMART_ACCESS_TOKEN = os.environ['SMART_ACCESS_TOKEN']
GITHUB_ACCESS_TOKEN = os.environ['GH_ACCESS_TOKEN']
# Start with the initial ISSUE_NUM from the environment
current_issue_num = int(os.environ['ISSUE_NUM'])  # Convert to integer

# Initialize Smartsheet client
smart = smartsheet.Smartsheet(SMART_ACCESS_TOKEN)
smart.errors_as_exceptions(True)

# Log all API calls
logging.basicConfig(filename='rwsheet.log', level=logging.INFO)

# Retry settings
MAX_RETRIES = 10  # Limit the number of attempts to prevent infinite loops
retry_count = 0

while retry_count < MAX_RETRIES:
    print(f"Attempting to process ISSUE_NUM: {current_issue_num}")

    # Fetch issue or PR details
    response = requests.get(
        f'https://api.github.com/repos/JesseCaddell/smartsheets_solution_dummy_repo/issues/{current_issue_num}',
        headers={
            'Authorization': f'Bearer {GITHUB_ACCESS_TOKEN}',
            'Content-Type': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
    )

    if response.status_code != 200:
        print(f"Error fetching issue #{current_issue_num}: {response.json()}")
        exit(1)  # Exit if the API fails

    data = response.json()

    # Check if the item is a PR
    if 'pull_request' in data:
        print(f"Skipping PR #{current_issue_num}. Incrementing to the next number...")
        current_issue_num += 1  # Increment the local counter
        retry_count += 1
        time.sleep(1)  # Add a short delay to avoid rapid API calls
        continue

    # Process the valid issue
    assignee = data.get('assignee', {}).get('login', 'Missing assignee')
    title = data.get('title', 'No Title')
    repo_url = data.get('repository_url', 'No Repo URL')
    index = data.get('number', 'No Index')

    # POST request to Smartsheet API
    smartsheet_response = requests.post(
        'https://api.smartsheet.com/2.0/sheets/5425857896075140/rows',
        headers={'Authorization': f'Bearer {SMART_ACCESS_TOKEN}', 'Content-Type': 'application/json'},
        json={
            'sheetId': 2342839996338052,
            'accessLevel': 'OWNER',
            'createdBy': {
                'name': 'automation'
            },
            'cells': [
                {
                'columnId': 5558737690382212,
                'displayValue': 'title',
                'value': title
                },
                {
                'columnId': 3306937876696964,
                'displayValue': 'repo url',
                'value': repo_url[45:]
                },
                {
                'columnId': 7810537504067460,
                'displayValue': 'assignee',
                'value': assignee
                },
                {
                'columnId': 2181037969854340,
                'displayValue': 'index',
                'value': index
                }
            ]
            })