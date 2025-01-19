import requests
import smartsheet
import logging
import os
#test

SMART_ACCESS_TOKEN = os.environ['SMART_ACCESS_TOKEN']
GITHUB_ACCESS_TOKEN = os.environ['GH_ACCESS_TOKEN']
# Start with the initial ISSUE_NUM from the environment
current_issue_num = int(os.environ['ISSUE_NUM'])  # Convert to integer

# Initialize Smartsheet client
smart = smartsheet.Smartsheet(SMART_ACCESS_TOKEN)
smart.errors_as_exceptions(True)

# Log all API calls
logging.basicConfig(filename='rwsheet.log', level=logging.INFO)

while True:  # Loop until a valid issue is successfully processed
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
        current_issue_num += 1  # Increment the local counter to skip PR
        continue

    # Process the valid issue
    print(f"Processing valid issue #{current_issue_num}")
    assignee_data = data.get('assignee')
    if assignee_data is not None:
        assignee = assignee_data.get('login', 'Missing assignee')
    else:
        assignee = 'Missing assignee'

    title = data.get('title', 'No Title')
    repo_url = data.get('repository_url', 'No Repo URL')
    index = data.get('number', 'No Index')

    # POST request to Smartsheet API
    smartsheet_response = requests.post(
        'https://api.smartsheet.com/2.0/sheets/2342839996338052/rows',
        headers={'Authorization': f'Bearer {SMART_ACCESS_TOKEN}', 'Content-Type': 'application/json'},
        json={
            'toTop': True,
            'cells': [
                {
                    'columnId': 5558737690382212,  # "Primary Column"
                    'value': title
                },
                {
                    'columnId': 3306937876696964,  # "Column2"
                    'value': repo_url[45:]
                },
                {
                    'columnId': 7810537504067460,  # "Column3"
                    'value': assignee
                },
                {
                    'columnId': 2181037969854340,  # "Column4"
                    'value': index
                }
            ]
        }
    )

    if smartsheet_response.status_code == 200:
        print(f"Issue #{current_issue_num} successfully sent to Smartsheet.")
        exit(0)  # Gracefully exit after successful processing
    else:
        print(f"Failed to send issue #{current_issue_num} to Smartsheet: {smartsheet_response.json()}")
        exit(1)
