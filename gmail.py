from simplegmail import Gmail
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

gmail = Gmail()

def summarize(text):
    response = client.models.generate_content(
        model="gemini-2.5-pro-exp-03-25",
        contents=f"Summarize {text}",
    )
    return response.text

PRIORITY_SENDER_NAME = "name"
PRIORITY_SENDER_EMAIL = "example@gmail.com"
PRIORITY_USER = f"{PRIORITY_SENDER_NAME} <{PRIORITY_SENDER_EMAIL}>"
PRIORITY_KEYWORDS = ["urgent", "important", "asap"]

def check_priority(message):
    is_priority = False
    priority_reason = ""

    if message.sender.lower() == PRIORITY_USER.lower():
        is_priority = True
        priority_reason = f"Priority Sender: {PRIORITY_USER}"

    if hasattr(message, 'subject') and message.subject:
        subject_lower = message.subject.lower()
        for keyword in PRIORITY_KEYWORDS:
            if keyword.lower() in subject_lower:
                is_priority = True
                priority_reason = f"Contains keyword '{keyword}' in subject"
                break

    if hasattr(message, 'plain') and message.plain:
        content_lower = message.plain.lower()
        for keyword in PRIORITY_KEYWORDS:
            if keyword.lower() in content_lower:
                is_priority = True
                priority_reason = f"Contains keyword '{keyword}' in content"
                break

    return is_priority, priority_reason

def process_emails():
    messages = gmail.get_unread_inbox()

    for message in messages:
        if not message.plain or len(message.plain) <= 500:
            email_content = f"To: {message.recipient}<br>"
            email_content += f"From: {message.sender}<br>"
            email_content += f"Date: {message.date}<br>"
            email_content += f"Subject: {message.subject}<br>"
            email_content += f"Content: {message.plain}<br><br><br>"
        
        else:
            summary = summarize(message.plain)
            email_content = f"To: {message.recipient}<br>"
            email_content += f"From: {message.sender}<br>"
            email_content += f"Date: {message.date}<br>"
            email_content += f"Subject: {message.subject}<br>"
            email_content += f"Content: {summary}<br><br><br>"

        is_priority, priority_reason = check_priority(message)

        if is_priority:
            with open('priority_emails.md', 'a') as f:
                f.write(f"Priority Reason: {priority_reason}\n\n")
                f.write(email_content)
        
        else:
            with open('regular_emails.md', 'a') as f:
                f.write(email_content)

if __name__ == "__main__":
    print("Starting email processing...")
    process_emails()
    print("Email processing completed!")
    print("Check 'priority_emails.md' for priority messages and 'regular_emails.md' for regular messages")