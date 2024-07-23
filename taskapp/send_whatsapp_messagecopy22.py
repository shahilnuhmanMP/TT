# import os
# import django
# from datetime import datetime
# from twilio.rest import Client
#
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task.settings')
# django.setup()
# from .models  import Event  # Updated import statement
# # Your Twilio Account SID and Auth Token
# account_sid = 'AC4591f77757cca8099d611ca9b3122d5a'
# auth_token = 'b4420d2044a47d60f73871ff8849cd2e'
#
# # Initialize Twilio Client
# client = Client(account_sid, auth_token)
#
# # Get today's date
# today_date = datetime.now().date()
#
# # Query events from the database where start date matches today's date
# events_today = Event.objects.filter(start_datetime_allday__contains=[str(today_date)])
# print("came till here again",events_today)
#
# # Rest of your script
# if events_today:
#     # Define the message content and recipient
#     message_content = "Hello from your Django cron job! Today's events:\n"
#     for event in events_today:
#         message_content += f"- {event.summary} at {event.start_datetime_allday}\n"
#
#     # recipient_phone_number = "whatsapp:+1234567890"  # Replace with the recipient's WhatsApp number
#
#     # Send the WhatsApp message
#     message = client.messages.create(
#         body=message_content,
#         from_='whatsapp:+14155238886',  # Replace with your Twilio WhatsApp number
#         to='whatsapp:+919539123525'
#     )
#
#     print("WhatsApp message sent successfully!")
# else:
#     print("No events for today.")




import os
import django
from datetime import datetime
from twilio.rest import Client


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task.settings')
django.setup()
from .models  import Event, Child , CustomUser # Updated import statement
# Your Twilio Account SID and Auth Token
account_sid = 'AC4591f77757cca8099d611ca9b3122d5a'
auth_token = 'b4420d2044a47d60f73871ff8849cd2e'

# Initialize Twilio Client
client = Client(account_sid, auth_token)

# Get today's date
today_date = datetime.now().date()

# Query events from the database where start date matches today's date
events_today = Event.objects.filter(start_datetime_allday__contains=[str(today_date)])
print("came till here again",events_today)
events_dict = {}

for event in events_today:
    child_id = event.child_id
    user_id = Child.objects.get(id=child_id).user_id
    if user_id not in events_dict:
        events_dict[user_id] = []
    events_dict[user_id].append(event)

# Iterate over events for each user's child and send messages
for user_id, events in events_dict.items():
    user = CustomUser.objects.get(id=user_id)
    for event in events:

        # Define the message content
        message_content = f"Hello {user.username}!\n\nEvent Details:\n"
        message_content += f"Summary: {event.summary}\n"
        message_content += f"Start Date/Time: {event.start_datetime}\n"
        message_content += f"End Date/Time: {event.end_datetime}\n"
        message_content += f"Repeat: {event.repeat}\n"

        # message_content += f"- {event.summary} at {event.start_datetime_allday}\n"

    # recipient_phone_number = "whatsapp:+1234567890"  # Replace with the recipient's WhatsApp number

    # Send the WhatsApp message
    message = client.messages.create(
        body=message_content,
        from_='whatsapp:+14155238886',  # Replace with your Twilio WhatsApp number
        to='whatsapp:+919539123525'
    )

    print("WhatsApp message sent successfully!")
else:
    print("No events for today.")
