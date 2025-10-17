# Netskope URL List Manager

A Python script to interact with Netskope tenant API for managing URL lists.

## Features

- Connect to Netskope tenant using FQDN and bearer token
- List all URL lists in a formatted table
- Select URL lists by number or name
- View detailed content of selected URL lists
- Interactive menu system to continue working or exit
- Refresh URL lists without restarting the program
- Comprehensive error handling for network, authentication, and API issues
- Secure token input (hidden when typing)

## Requirements

- Python 3.6+
- Internet connection
- Valid Netskope tenant access
- Bearer token with appropriate permissions

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests tabulate
```

## Usage

1. Run the script:
```bash
python netskope_urllist_manager.py
```

2. Enter your tenant FQDN when prompted:
   - Example: `tenant.goskope.com`
   - Do not include `https://` prefix

3. Enter your bearer token (input will be hidden)

4. The script will:
   - Test the connection
   - Retrieve and display all URL lists in a table
   - Allow you to select a URL list by number or name
   - Display the URLs in the selected list
   - Show a menu with options to continue, refresh, or exit

5. Menu options after viewing a URL list:
   - **View another URL list**: Return to the URL list table to select another list
   - **Refresh URL lists**: Reload the URL lists from the server (in case of updates)
   - **Exit program**: Close the application

## API Endpoints Used

- `GET /api/v2/policy/urllist` - Retrieve all URL lists
- `GET /api/v2/policy/urllist/{id}` - Get specific URL list content

## Error Handling

The script handles:
- Invalid tenant FQDN format
- Authentication failures (401)
- Access permission issues (403)
- Network connectivity problems
- Non-existent URL list IDs (404)
- Request timeouts
- Invalid user selections

## Example Output

```
=== Netskope URL List Manager ===

Enter tenant FQDN (e.g., tenant.goskope.com): mytenant.goskope.com
Enter bearer token: [hidden input]

Testing connection...
✓ Connection successful!

Retrieving URL lists...

=== Available URL Lists ===
+---+----+------------------+---------------+---------------------+
| # | ID | Name             | Modified By   | Modified Time       |
+===+====+==================+===============+=====================+
| 1 | 1  | Social Media     | admin         | 2024-01-15 10:30:00 |
| 2 | 2  | News Sites       | john.doe      | 2024-01-10 14:22:00 |
| 3 | 3  | Development URLs | Netskope API  | 2024-01-12 09:15:00 |
+---+----+------------------+---------------+---------------------+

Select a URL list (enter number 1-3 or list name):
Your choice: 1

Retrieving content for 'Social Media'...

=== URL List Content: Social Media ===
ID: 1
Type: exact
Modified by: admin
Modified time: 2024-01-15 10:30:00
Pending: 0

URLs (3 total):
  1. facebook.com
  2. twitter.com
  3. instagram.com

=== Main Menu ===
1. View another URL list
2. Refresh URL lists
3. Exit program

Enter your choice (1-3): 1

=== Available URL Lists ===
+---+----+------------------+---------------+---------------------+
| # | ID | Name             | Modified By   | Modified Time       |
+===+====+==================+===============+=====================+
| 1 | 1  | Social Media     | admin         | 2024-01-15 10:30:00 |
| 2 | 2  | News Sites       | john.doe      | 2024-01-10 14:22:00 |
| 3 | 3  | Development URLs | Netskope API  | 2024-01-12 09:15:00 |
+---+----+------------------+---------------+---------------------+

Select a URL list (enter number 1-3 or list name):
Your choice: 3

Enter your choice (1-3): 3

=== Thank you for using Netskope URL List Manager! ===
```

## Security Notes

- Bearer tokens are entered securely (hidden input)
- Always use HTTPS for API communications
- Keep your bearer tokens confidential
- Ensure proper network security when running the script

## Troubleshooting

### Common Issues:

1. **"Invalid tenant FQDN format"**
   - Ensure you enter only the domain name (e.g., `tenant.goskope.com`)
   - Don't include `http://` or `https://`

2. **"Authentication failed"**
   - Check your bearer token
   - Verify token permissions
   - Ensure token hasn't expired

3. **"Network connection error"**
   - Check internet connectivity
   - Verify tenant URL is correct
   - Check for firewall restrictions

4. **"Access forbidden"**
   - Your token may not have sufficient permissions
   - Contact your Netskope administrator

5. **"URL list with ID X not found"**
   - The URL list may have been deleted
   - Refresh the list and try again
