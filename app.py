import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
YOUR_USER_ID = "YOUR_SLACK_USER_ID"

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(token=SLACK_BOT_TOKEN)

# Dictionary to store message ratings
message_ratings = {}

@app.event("app_mention")
def handle_app_mentions(body, say):
    user_id = body['event']['user']
    channel_id = body['event']['channel']
    say(f"Hi <@{user_id}>! Please rate the urgency and importance of the message (low/medium/high). For example: `urgency: high, importance: medium`", channel=channel_id)

@app.event("message")
def handle_message_events(body, say):
    text = body['event'].get('text', '').lower()
    user_id = body['event']['user']
    channel_id = body['event']['channel']
    
    if "urgency:" in text and "importance:" in text:
        try:
            urgency = text.split("urgency:")[1].split(",")[0].strip()
            importance = text.split("importance:")[1].strip()
            
            if urgency in ["low", "medium", "high"] and importance in ["low", "medium", "high"]:
                message = f"Message from <@{user_id}>: {body['event'].get('text')}"
                message_ratings[message] = (urgency, importance)
                
                say(f"Thank you, <@{user_id}>! Your message has been rated as {urgency} urgency and {importance} importance.", channel=channel_id)
                
                # Notify you with the message ratings
                client.chat_postMessage(channel=YOUR_USER_ID, text=f"New message with ratings:\n{message}\nUrgency: {urgency}\nImportance: {importance}")

                # Repost the message in the appropriate channel
                rating_channel = f"{urgency}_urgency_messages"
                say(f"{message}\nUrgency: {urgency}\nImportance: {importance}", channel=rating_channel)
            else:
                say(f"Sorry, <@{user_id}>! Please provide valid urgency and importance ratings (low/medium/high).", channel=channel_id)
        except Exception as e:
            say(f"Sorry, <@{user_id}>! There was an error processing your message. Please try again.", channel=channel_id)

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
