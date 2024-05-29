import boto3
from config import get_rules
from mail import Mail, ParsedMail
from sheets import update_sheet

MAIL_BUCKET_NAME = "mailparser2"

def lambda_handler(event, context):
  """Reads email details from an SES trigger event.

  Args:
      event: The SES trigger event containing email details.
      context: The Lambda context object.

  Returns:
      A dictionary containing details about the processed email.
  """

  # Get the email details from the event
  records = event['Records']

  for record in records:
    ses_message = record['ses']['mail']

    # TODO: test
    s3_client = boto3.client('s3')
    object_key = ses_message['messageId']
    email_content = s3_client.get_object(Bucket=MAIL_BUCKET_NAME, Key=object_key)['Body'].read()
    print(email_content)
    print(ses_message)

    mail = Mail(ses_message['messageId'], email_content.decode('utf-8'))
    parsedmail = ParsedMail(mail)
    parsedmail.parse()

    rules = get_rules(parsedmail)

    data = parsedmail.generate_sheet_data(rules["row"])

    update_sheet(rules["sheetId"], data, rules["sheetName"])

    # Extract relevant email details
    sender = ses_message['source']
    recipient = ses_message['destination'][0]
    subject = None
    body = None

    # Extract headers (optional)
    for header in ses_message.get('headers', []):
      if header['name'] == 'Subject':
        subject = header['value']
      elif header['name'] == 'Content-Type' and header['value'].startswith('text/plain'):
        body = ses_message.get('body', '')
        break  # Only process plain text bodies for simplicity

    # Process the email details (replace with your logic)
    print(f"Received email from {sender} to {recipient}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")

    # You can further process the email details here
    # For example, store them in a database, send notifications, etc.

  return {
      'message': 'Successfully processed email details'
  }
