#!/usr/bin/env python3
"""
Netskope URL List Manager
A script to connect to Netskope tenant via API to manage URL lists.
"""

import requests
import getpass
import re
import sys
from tabulate import tabulate
from urllib.parse import urlparse


class NetskopeAPIClient:
    def __init__(self, tenant_fqdn, bearer_token):
        self.tenant_fqdn = tenant_fqdn.rstrip('/')
        self.bearer_token = bearer_token
        self.base_url = f"https://{self.tenant_fqdn}"
        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }
    
    def test_connection(self):
        """Test the API connection and authentication."""
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/policy/urllist",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 401:
                raise ValueError("Authentication failed. Please check your bearer token.")
            elif response.status_code == 403:
                raise ValueError("Access forbidden. Check your permissions.")
            elif response.status_code != 200:
                raise ValueError(f"API request failed with status code: {response.status_code}")
            
            return True
            
        except requests.exceptions.ConnectionError:
            raise ValueError("Network connection error. Please check your internet connection and tenant URL.")
        except requests.exceptions.Timeout:
            raise ValueError("Request timeout. The server may be unavailable.")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Request error: {str(e)}")
    
    def get_url_lists(self):
        """Retrieve all URL lists from the tenant."""
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/policy/urllist",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 401:
                raise ValueError("Authentication failed during URL list retrieval.")
            elif response.status_code != 200:
                raise ValueError(f"Failed to retrieve URL lists. Status code: {response.status_code}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error retrieving URL lists: {str(e)}")
    
    def get_url_list_content(self, list_id):
        """Retrieve content of a specific URL list by ID."""
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/policy/urllist/{list_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 404:
                raise ValueError(f"URL list with ID {list_id} not found.")
            elif response.status_code == 401:
                raise ValueError("Authentication failed during URL list content retrieval.")
            elif response.status_code != 200:
                raise ValueError(f"Failed to retrieve URL list content. Status code: {response.status_code}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error retrieving URL list content: {str(e)}")


def validate_tenant_fqdn(fqdn):
    """Validate the tenant FQDN format."""
    # Remove protocol if present
    if fqdn.startswith(('http://', 'https://')):
        parsed = urlparse(fqdn)
        fqdn = parsed.netloc
    
    # Basic FQDN validation
    fqdn_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    
    if not re.match(fqdn_pattern, fqdn):
        raise ValueError("Invalid tenant FQDN format. Please enter a valid domain name (e.g., tenant.goskope.com)")
    
    return fqdn


def get_user_credentials():
    """Get tenant FQDN and bearer token from user input."""
    print("=== Netskope URL List Manager ===\n")
    
    # Get tenant FQDN
    while True:
        tenant_fqdn = input("Enter tenant FQDN (e.g., tenant.goskope.com): ").strip()
        try:
            validated_fqdn = validate_tenant_fqdn(tenant_fqdn)
            break
        except ValueError as e:
            print(f"Error: {e}")
            continue
    
    # Get bearer token (hidden input)
    bearer_token = getpass.getpass("Enter bearer token: ").strip()
    
    if not bearer_token:
        raise ValueError("Bearer token cannot be empty.")
    
    return validated_fqdn, bearer_token


def display_url_lists_table(url_lists):
    """Display URL lists in a table format."""
    if not url_lists:
        print("No URL lists found.")
        return []
    
    # Prepare table data
    table_data = []
    for i, url_list in enumerate(url_lists, 1):
        table_data.append([
            i,  # Index for selection
            url_list.get('id', 'N/A'),
            url_list.get('name', 'N/A'),
            url_list.get('modify_by', 'N/A'),
            url_list.get('modify_time', 'N/A')
        ])
    
    # Display table
    headers = ['#', 'ID', 'Name', 'Modified By', 'Modified Time']
    print("\n=== Available URL Lists ===")
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    return url_lists


def get_user_selection(url_lists):
    """Get user selection for URL list."""
    if not url_lists:
        return None
    
    print(f"\nSelect a URL list (enter number 1-{len(url_lists)} or list name):")
    
    while True:
        selection = input("Your choice: ").strip()
        
        if not selection:
            print("Please enter a valid selection.")
            continue
        
        # Try to parse as number
        if selection.isdigit():
            index = int(selection) - 1
            if 0 <= index < len(url_lists):
                return url_lists[index]
            else:
                print(f"Please enter a number between 1 and {len(url_lists)}.")
                continue
        
        # Try to match by name
        matching_lists = [ul for ul in url_lists if ul.get('name', '').lower() == selection.lower()]
        
        if len(matching_lists) == 1:
            return matching_lists[0]
        elif len(matching_lists) > 1:
            print(f"Multiple URL lists found with name '{selection}'. Please use the number instead.")
            continue
        else:
            print(f"No URL list found with name '{selection}'. Please try again.")
            continue


def display_url_list_content(url_list_data):
    """Display the content of a selected URL list."""
    print(f"\n=== URL List Content: {url_list_data.get('name', 'Unknown')} ===")
    print(f"ID: {url_list_data.get('id', 'N/A')}")
    print(f"Type: {url_list_data.get('data', {}).get('type', 'N/A')}")
    print(f"Modified by: {url_list_data.get('modify_by', 'N/A')}")
    print(f"Modified time: {url_list_data.get('modify_time', 'N/A')}")
    print(f"Pending: {url_list_data.get('pending', 'N/A')}")
    
    urls = url_list_data.get('data', {}).get('urls', [])
    if urls:
        print(f"\nURLs ({len(urls)} total):")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")
    else:
        print("\nNo URLs found in this list.")


def show_main_menu():
    """Display the main menu and get user choice."""
    print("\n=== Main Menu ===")
    print("1. View another URL list")
    print("2. Refresh URL lists")
    print("3. Exit program")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice in ['1', '2', '3']:
            return choice
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def main():
    """Main function to orchestrate the script."""
    try:
        # Get user credentials (only once at startup)
        tenant_fqdn, bearer_token = get_user_credentials()
        
        # Initialize API client
        client = NetskopeAPIClient(tenant_fqdn, bearer_token)
        
        # Test connection (only once at startup)
        print("\nTesting connection...")
        client.test_connection()
        print("✓ Connection successful!")
        
        # Main program loop
        url_lists = None
        
        while True:
            try:
                # Get URL lists (initially or when refreshing)
                if url_lists is None:
                    print("\nRetrieving URL lists...")
                    url_lists_response = client.get_url_lists()
                    
                    # Extract the list from response (handle different response formats)
                    if isinstance(url_lists_response, list):
                        url_lists = url_lists_response
                    elif isinstance(url_lists_response, dict) and 'data' in url_lists_response:
                        url_lists = url_lists_response['data']
                    else:
                        raise ValueError("Unexpected response format from URL lists API")
                
                # Display URL lists table
                displayed_lists = display_url_lists_table(url_lists)
                
                if not displayed_lists:
                    print("No URL lists available.")
                    break
                
                # Get user selection for URL list
                selected_list = get_user_selection(displayed_lists)
                
                if selected_list:
                    print(f"\nRetrieving content for '{selected_list.get('name', 'Unknown')}'...")
                    
                    # Get detailed content
                    list_content = client.get_url_list_content(selected_list['id'])
                    
                    # Display content
                    display_url_list_content(list_content)
                    
                    # Show main menu and handle choice
                    menu_choice = show_main_menu()
                    
                    if menu_choice == '1':
                        # View another URL list - continue with current lists
                        continue
                    elif menu_choice == '2':
                        # Refresh URL lists - set to None to trigger refresh
                        url_lists = None
                        continue
                    elif menu_choice == '3':
                        # Exit program
                        print("\n=== Thank you for using Netskope URL List Manager! ===")
                        break
                else:
                    # No selection made, show menu
                    menu_choice = show_main_menu()
                    
                    if menu_choice == '1':
                        # Try again with current lists
                        continue
                    elif menu_choice == '2':
                        # Refresh URL lists
                        url_lists = None
                        continue
                    elif menu_choice == '3':
                        # Exit program
                        print("\n=== Thank you for using Netskope URL List Manager! ===")
                        break
                        
            except ValueError as e:
                print(f"\nError: {e}")
                
                # Ask user if they want to continue or exit
                print("\nWhat would you like to do?")
                print("1. Try again")
                print("2. Refresh URL lists")
                print("3. Exit program")
                
                while True:
                    choice = input("\nEnter your choice (1-3): ").strip()
                    if choice == '1':
                        break  # Continue with current loop
                    elif choice == '2':
                        url_lists = None  # Force refresh
                        break
                    elif choice == '3':
                        print("\n=== Thank you for using Netskope URL List Manager! ===")
                        return
                    else:
                        print("Invalid choice. Please enter 1, 2, or 3.")
        
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
        print("=== Thank you for using Netskope URL List Manager! ===")
        sys.exit(0)
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
