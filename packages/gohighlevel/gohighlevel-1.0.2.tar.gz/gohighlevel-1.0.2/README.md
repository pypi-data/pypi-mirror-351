# Go High Level Python

Go Highlevel Python ease of use library implementation to their API


![Static Badge](https://img.shields.io/badge/m2kdevelopments-purple?style=plastic&logo=github&logoColor=purple&label=developer&link=https%3A%2F%2Fgithub.com%2Fm2kdevelopments)
![Static Badge](https://img.shields.io/badge/MIT-green?style=plastic&logo=license&logoColor=green&label=license)
![Static Badge](https://img.shields.io/badge/buy_me_a_coffee-yellow?style=plastic&logo=buymeacoffee&logoColor=yellow&label=support&link=https%3A%2F%2Fwww.buymeacoffee.com%2Fm2kdevelopments)
![Static Badge](https://img.shields.io/badge/paypal-blue?style=plastic&logo=paypal&logoColor=blue&label=support&link=https%3A%2F%2Fpaypal.me%2Fm2kdevelopment)
 
<br/>
<img src="./ghl.jpg" alt="Highlevel" width="420">
<br/>


Go Highlevel ease of use library implementation to their API. Make sure you've create a Go Highlevel App in the <a href="https://marketplace.gohighlevel.com/" target="_blank">Market Place</a>



## Brief Overview of the Library
We recommend that you glance over the official <a href="https://highlevel.stoplight.io/docs/integrations/0443d7d1a4bd0-overview" target="_blank">Go Highlevel Documentation</a>. We have tried to make the library have a corresponding function for each endpoint. Enjoy the intellisense!




## Initialization
```python
from gohighlevel import GoHighLevel
from gohighlevel.classes.auth.credentials import Credentials

credentials=Credentials(api_key="***")
ghl = GoHighLevel(credentials=credentials)
```

### OAuth URL
```python
from gohighlevel import GoHighLevel
from gohighlevel.classes.auth.credentials import Credentials


# Initialize with your client ID and secret
credentials=Credentials(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize with your client ID and secret
ghl = GoHighLevel(credentials=credentials)

# Get OAuth URL
oauth_url = ghl.get_oauth_url(
    redirect_uri="your_redirect_uri",
    scope=["contacts.readonly", "calendars.write"]
)
print(oauth_url)
```

### OAuth Callback
```python
from gohighlevel import GoHighLevel
from gohighlevel.classes.auth.credentials import Credentials


# Initialize with your client ID and secret
credentials=Credentials(
    client_id="your_client_id",
    client_secret="your_client_secret"
)
ghl = GoHighLevel(credentials=credentials)

# Exchange code for tokens
tokens = ghl.exchange_code(
    code="auth_code_from_callback",
    redirect_uri="your_redirect_uri"
)
print(tokens)  # Contains access_token, refresh_token, etc.
```

### Calendar Management Examples
```python
# Get all calendars for a location
calendars = ghl.calendar.get_all(location_id="your_location_id")

# Create a new calendar
new_calendar = ghl.calendar.add({
    "name": "Team Meetings",
    "description": "Calendar for team meetings",
    "locationId": "your_location_id"
})

# Get calendar events
events = ghl.calendar.events.get_all(
    location_id="your_location_id",
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-01-31T23:59:59Z"
)

# Create an appointment
appointment = ghl.calendar.events.add_appointment(
    location_id="your_location_id",
    contact_id="contact_id",
    start_time="2024-01-15T10:00:00Z",
    calendar={
        "title": "Project Review",
        "duration": 60,
        "calendarId": "calendar_id"
    }
)

# Manage calendar groups
groups = ghl.calendar.groups.get_all()

new_group = ghl.calendar.groups.add({
    "name": "Sales Team",
    "description": "Calendar group for sales team",
    "locationId": "your_location_id"
})

# Manage calendar resources
rooms = ghl.calendar.resources.get_all(resource_type="rooms")

new_room = ghl.calendar.resources.add(
    resource_type="rooms",
    resource={
        "name": "Conference Room A",
        "capacity": 20,
        "locationId": "your_location_id"
    }
)

# Manage calendar notifications
notifications = ghl.calendar.notifications.get_all(
    calendar_id="calendar_id",
    extra={
        "is_active": True,
        "limit": 10
    }
)

# Create appointment notes
note = ghl.calendar.appointmentnotes.add(
    appointment_id="appointment_id",
    body="Meeting notes: Discussed project timeline",
    user_id="user_id"
)
```

### Using Contacts API
```python

# Search contacts
searched_contacts = ghl.contacts.search(query="martin")

# Get all contacts
contacts = ghl.contacts.get_all(location_id="your_location_id")

# Create a new contact
new_contact = ghl.contacts.add({
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "locationId": "your_location_id"
})

# Add a task for a contact
task = ghl.contacts.tasks.add(
    contact_id="contact_id",
    title="Follow up",
    due_date="2024-01-15T10:00:00Z"
)
```

### Using Conversations API
```python
# Get all conversations
conversations = ghl.conversations.get_all(location_id="your_location_id")

# Get conversation messages
messages = ghl.conversations.messages.get_all(
    conversation_id="conversation_id",
    limit=50,
    skip=0
)

# Send a message
new_message = ghl.conversations.messages.add(
    conversation_id="conversation_id",
    message={
        "body": "Hello! How can I help you today?",
        "type": "text"
    }
)

# Send an email in conversation
email_message = ghl.conversations.email.send(
    conversation_id="conversation_id",
    email={
        "subject": "Meeting Follow-up",
        "body": "Thank you for your time today...",
        "to": ["recipient@example.com"]
    }
)

# Get conversation providers
providers = ghl.conversations.providers.get_all(location_id="your_location_id")

# Update conversation status
updated_conversation = ghl.conversations.update(
    conversation_id="conversation_id",
    data={
        "status": "closed",
        "assignedTo": "user_id"
    }
)

# Search conversations
search_results = ghl.conversations.search(
    location_id="your_location_id",
    query="customer support",
    filters={
        "status": "open",
        "dateRange": {
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2024-01-31T23:59:59Z"
        }
    }
)
```

## Support
You can support us with any amount. It's all appreciated.

<a href="https://www.buymeacoffee.com/m2kdevelopments" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" />
</a>

<a href="https://paypal.me/m2kdevelopment" target="_blank">
    <img src="https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_111x69.jpg" alt="PayPal Logo" />
</a>

