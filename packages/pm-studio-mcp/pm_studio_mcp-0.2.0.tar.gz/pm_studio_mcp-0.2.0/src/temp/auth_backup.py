import os
import msal
from msal import PublicClientApplication
import sys

class AuthUtils:

    client_id = os.environ['CLIENT_ID']
    authority = "https://login.microsoftonline.com/" + os.environ['TENANT_ID']
    scopes = ["https://graph.microsoft.com/.default"]  # Adjust scopes as needed
    
    app = PublicClientApplication(
        client_id=client_id,
        authority=authority,
        # enable_broker_on_mac=True if sys.platform == "darwin" else False, #needed for broker-based flow
        # enable_broker_on_windows=True if sys.platform == "win32" else False, #needed for broker-based flow
    )

    def is_authenticated():
        """
        Check if the user is already authenticated.

        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            # Check if there are any cached accounts
            accounts = AuthUtils.app.get_accounts()
            
            if accounts:
                print ("Found cached account: ", flush=True)
                for account in accounts:
                    print(f"  {account['username']}", flush=True)
                # Try to get token silently from cache
                result = AuthUtils.app.acquire_token_silent(AuthUtils.scopes, account=accounts[0])
                if result:
                    print("Retrieved token from cache")
                    return True
            else:
                print("No cached accounts found.", flush=True)
                return False

        except Exception as e:
            print(f"Error checking authentication: {str(e)}")
            return False

    def login():
        """
        Authenticate with MSAL and return the access token.

        Returns:
            str: The access token
        """
        try:
            print("Authenticating...")

            # Try to get token silently from cache first
            accounts = AuthUtils.app.get_accounts()
            if accounts:
                print ("Found cached account: ")
                for account in accounts:
                    print(f"  {account['username']}")
                result = AuthUtils.app.acquire_token_silent(AuthUtils.scopes, account=accounts[0])
                if result:
                    print("Retrieved token from cache", flush=True)
                    print(result['access_token'],flush=True)
                    return result['access_token']

            # If no cached token, do interactive authentication
            result = AuthUtils.app.acquire_token_interactive(
                AuthUtils.scopes
                # port=0,  # Specify the port if needed
                # parent_window_handle=msal.PublicClientApplication.CONSOLE_WINDOW_HANDLE #needed for broker-based flow
            )

            if "access_token" not in result:
                print(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
                sys.exit(1)

            print("Authentication successful!", flush=True)
            print(result["access_token"],flush=True)

            return result["access_token"]

        except Exception as e:
            print(f"Authentication error: {str(e)}")
            sys.exit(1)