import requests
from datetime import datetime, timezone
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



NOTION_SECRET = 'USE YOUR OWN SECRET DUMBO'
DATABASE_ID = 'f49a5090b98a44dea1c49c3d8d2d7402'
SENDER_EMAIL = 'notionDemoExample123@outlook.com'
SENDER_PASSWORD = 'USE YOUR OWN PASSWORDDD'
EMAIL_SUBJECT = 'SUB to be sent'



 
headers = {
    "Authorization" : "Bearer " + NOTION_SECRET,
    "Content-Type" : "application/json",
    "Notion-Version" : "2022-06-28",
}




def send_outlook_mail(email_description, receiver):
    # SMTP server settings for Outlook
    smtp_server = 'smtp.office365.com'
    smtp_port = 587  # or 25 if not using STARTTLS

    # Outlook account credentials
    sender_email = SENDER_EMAIL
    sender_password = SENDER_PASSWORD

    # Create a multipart message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver
    message['Subject'] = EMAIL_SUBJECT

    # Add email description as plain text
    message.attach(MIMEText(email_description, 'plain'))

    try:
        # Create a secure connection with the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        print('Email sent successfully!')
    except Exception as e:
        print(f'An error occurred while sending the email: {str(e)}')




# Updates the status for those for which email is to be sent
def updatePage(PAGE_ID, headers):
    updateUrl = f"https://api.notion.com/v1/pages/{PAGE_ID}"

    updateData = {
        'properties' :{
            'Status': {
                'status': {
                    'name':'Done',
                    'color':'green'
                }
            }
        }
        
    }

    data = json.dumps(updateData)

    response = requests.request("PATCH", updateUrl, headers=headers, data=data)

    # print(response.status_code)
    # print(response.text)





# To get data from notion
def get_pages(num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    #Comment this out to dump all data to a file
    with open('db.json', 'w', encoding='utf8') as f:
       json.dump(data, f, ensure_ascii=False, indent=4)




    # print(data)
    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        # print(data)
        results.extend(data["results"])

    return results







pages = get_pages()
for page in pages:
    page_id = page["id"]
    props = page["properties"]
    email_desc = props["Organizer desc"]["title"][0]["text"]["content"]
    emails = props["Organizer emails"]
    status = props["Status"]






    # Checking if there are emails to be sent and sending them
    if status['status']['color']=='purple':
        # print(page['properties'],'\n\n')
        print(status['status']['name'])


        email_list = list((emails['rich_text'][0]['text']['content']).split())
        print(email_list)
        print(email_desc)

        for email in email_list:
            send_outlook_mail(email_description=email_desc,receiver=email)

        updatePage(PAGE_ID=page_id, headers=headers)