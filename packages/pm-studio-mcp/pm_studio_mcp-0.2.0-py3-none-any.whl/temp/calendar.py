from utils.auth import AuthUtils
from datetime import datetime, timedelta
import requests

class CalendarUtils:
    @staticmethod
    def get_my_calendar_events(parameter: dict[str,str]):
        """
        Retrieve the latest calendar events using Microsoft Graph API.
        
        Args:
            parameter: dictionary of parameters for Microsoft Graph API request.
            it contains the following
            - $top: number of events to retrieve
            - $orderby: order of events
            - $filter: filter for events
            - $select: fields to select
            
        Returns:
            list: List of calendar events
        """

        print(f"Retrieving latest calendar events with parameter: {parameter}", flush=True)
        try:
    
            access_token = AuthUtils.login();
            
            if access_token:
                print(f"\nAuthentication successful. Token obtained (length: {len(access_token)})", flush=True)
            
            # Set up headers with the access token
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Make request to Microsoft Graph API
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me/events',
                headers=headers,
                params=parameter
            )

            print(response.status_code, flush=True)
            
            # Check if request was successful
            if response.status_code == 200:
                events = response.json().get('value', [])
                return events
            else:
                print(f"Error retrieving calendar events: {response.status_code}", flush=True)
                print(response.text, flush=True)
                return []
                
        except Exception as e:
            print(f"Error retrieving calendar events: {str(e)}")
            return []

    def format_events(events):
        """Format events for display"""
        if not events:
            return "No upcoming events found."
        
        formatted = "Upcoming Calendar Events:\n"
        for event in events:
            start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            formatted += f"\n• {event['subject']}\n"
            formatted += f"  When: {start_time.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
            if event.get('location', {}).get('displayName'):
                formatted += f"  Where: {event['location']['displayName']}\n"
        
        return formatted