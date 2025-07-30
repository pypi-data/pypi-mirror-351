# Report Test Results as Jira Task and Notify Slack - mainly for automated tests
This repository contains utility scripts for
- reporting automated test results Jira
- sending a slack notification with proper stats and jira url that shows failed tests in the current test run id (trid)
specifically designed for use in CI/CD pipelines such as Bitbucket Pipelines.

## Prerequisites
- **Python**: Version 3.12 or higher.
- **Jira Access**: A Jira instance with API token authentication.
- **Slack Webhook**: A Slack webhook URL for sending notifications.
- **Configuration File**: A `_env_configs/third-party.conf` file with Jira and Slack settings.

## Installation
```pip install jira-test-reporting```

## Configuration
In the caller projetct, create a `_env_configs/third-party.conf` file with the following structure:

```ini
[DEFAULT]
jira_host_url = https://your-jira-instance.atlassian.net
jira_username = your-email@example.com
jira_password = your-jira-api-token
jira_project_key = TMGT
slack_dev_channel_webhook = https://hooks.slack.com/services/your/dev/webhook
slack_prod_channel_webhook = https://hooks.slack.com/services/your/prod/webhook
slack_test_webhook = https://hooks.slack.com/services/your/test/webhook
```

- `jira_host_url`: Your Jira instance URL.
- `jira_username`: Your Jira account email.
- `jira_password`: Your Jira API token (generate from Jira > Account Settings > Security > Create API token).
- `jira_project_key`: The Jira project key (e.g., `TMGT`).
- `slack_*_webhook`: Slack webhook URLs for different channels or test runs.

## Create new Jira project and configure issue type "Task" with following fields
The script uses the following custom fields in Jira tasks:
- `customfield_10208`: Test Environment (Dropdown, e.g., `Dev`, `Prod`) - Pre-populate the values per your choice
- `customfield_10236`: Test Area (Dropdown, e.g., `Dashboard`) - Pre-populate the values per your choice
- `customfield_10301`: Test Type (Labels, e.g., `Rest APIs`)
- `customfield_10205`: Test Run (Short Text, e.g., `Release-X`)
- `customfield_10202`: Test Tags (Labels, e.g., `['tag1', 'tag2']`)
- `customfield_10235`: Test Status (Dropdown, e.g., `Passed`, `Failed`, `Skipped`) - Pre-populate the values per your choice
- `customfield_10269`: TRID (Short Text, unique test run ID)

The script uses the following default fields in Jira tasks:
- `project` - reflects `jira_project_key`
- `summary` - test_name
- `description` - failure or passing description
- `status` - reflects test_status as in `customfield_10235`

The values for the fields above will be fetched directly from the json_report

## Slack Notification Format

The Slack message includes:

- Header: `API Test Results`
- Test Run and Environment
- Failed test count
- Total, passed, executed, and skipped test counts
- Link to Jira report filtered by TRID
- Execution date
- User mentions for follow-up

Example:
```
API Test Results
──────────────
🚀 *Test Run:* Release-X
🌎 *Environment:* Dev
❌ *Failed:* 2
──────────────
🧪 *Total Tests:* 109
✅ *Passed:* 0
🔄 *Executed:* 109
⏸️ *Skipped:* 107
📈 Click to open Test Report in Jira
📡 FYA: @User1 @User2
Execution Date: May-23-2025
```

## Usage
### Stand-alone
Run the script with command-line arguments to process a pytest report:
```bash
python -m jira_test_reporting.test_results_processor --test-env=Dev --test-run=Release-X
```
### CI-CD hooked example (this copies required files into your test_automation directory)
configure bitbucket-pipeline to run a shell file as follows
```bash
#!/bin/bash
# -----------------------------------------------------------------------------------------
# # Test Execution
# -----------------------------------------------------------------------------------------
.. test execution code here
..
# -----------------------------------------------------------------------------------------
# Report test results to Jira
# -----------------------------------------------------------------------------------------

echo "Reporting test results into Jira and notifying slack"
if [ -n "$TEST_RUN_NAME" ]; then
    python -m jira_test_reporting.test_results_processor --test-env="$TEST_ENV" --test-run="$TEST_RUN_NAME"
else
    python -m jira_test_reporting.test_results_processor --test-env="$TEST_ENV"
fi
```


### Arguments

- `--test-env`: Test environment (default: `Dev`). Example: `Dev`, `Prod`.
- `--test-run`: Test run identifier (default: `Daily Run`). Example: `Release-X`, `Regression-Test`.

## Troubleshooting

- **Jira Connection Errors**:
  - Verify `jira_host_url`, `jira_username`, and `jira_password` in `_env_configs/third-party.conf`.
  - Ensure the API token is valid and has “Create Issues” and “Edit Issues” permissions.
- **Slack Notification Failure**:
  - Check the webhook URL in the config file.
  - Ensure the Slack app is configured to allow incoming webhooks.
- **Pytest Report Issues**:
  - Confirm `test-reports/pytest_report.json` exists and contains valid JSON.
- **Custom Field Errors**:
  - Validate field IDs and allowed values in Jira Admin > Issues > Custom Fields.

## Contributing

To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/new-feature`).
3. Commit changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See `LICENSE` for details.