import requests
import smartsheet
import logging
import os

SMART_ACCESS_TOKEN = os.environ['SMART_ACCESS_TOKEN']
GITHUB_ACCESS_TOKEN = os.environ['GH_ACCESS_TOKEN']
current_issue_num = int(os.environ['ISSUE_NUM'])  # Start from the last processed issue
triggered_issue_num = int(os.environ['CURRENT_ISSUE_NUM'])  # Current issue number from event

# Initialize Smartsheet client
smart = smartsheet.Smartsheet(SMART_ACCESS_TOKEN)
smart.errors_as_exceptions(True)

# Log all API calls
logging.basicConfig(filename='rwsheet.log', level=logging.INFO)

while current_issue_num <= triggered_issue_num:
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
        current_issue_num += 1  # Skip to next
        continue

    data = response.json()

    # Check if the item is a PR
    if 'pull_request' in data:
        print(f"Skipping PR #{current_issue_num}. Incrementing to the next number...")
        current_issue_num += 1
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
    else:
        print(f"Failed to send issue #{current_issue_num} to Smartsheet: {smartsheet_response.json()}")

    current_issue_num += 1  # Move to the next issue

# Update the GitHub Actions environment variable
with open(os.environ['GITHUB_ENV'], 'a') as github_env:
    github_env.write(f"ISSUE_NUM={triggered_issue_num}\n")

print(f"Updated ISSUE_NUM to {triggered_issue_num} in GitHub Actions environment.")