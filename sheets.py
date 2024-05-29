import json
import os

from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build


# Project Config
PROJECT_ID = "mailparser-crimsontwilight"
SERVICE_ACCOUNT_CREDENTILS = None
if os.environ.get("DATA_WIZARDS_MAILPARSER_CREDENTIALS"):
    SERVICE_ACCOUNT_CREDENTILS = json.loads(os.environ["DATA_WIZARDS_MAILPARSER_CREDENTIALS"])

GOOGLE_SERVICE_ACCOUNT = "/home/jayam/Dropbox.old/Documents/keys/mailparser/data-wizards-mailparser-crimsontwilight.json"
SHEETID = "19akPwXet5WExRZSeUA2IFW28OndjciMgrgt1UitEmzg"

cred = None
# try:
#     cred = service_account.Credentials.from_service_account_file(
#         GOOGLE_SERVICE_ACCOUNT)
# except:
#     print("No credentials founds!!")


def update_sheet(sheet_id: str, values: list, sheet_name: str, credentials: dict = SERVICE_ACCOUNT_CREDENTILS):
    try:
        global cred
        if credentials:
            cred = service_account.Credentials.from_service_account_info(credentials)
        

        service = build('sheets', 'v4', credentials=cred, client_options={
                        "quota_project_id": PROJECT_ID})

        # Call the Sheets API
        sheet = service.spreadsheets()

        # Update the sheet with new data
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': [[0]]
        }
        # result = sheet.values().batchUpdate(spreadsheetId=SHEETID,
        #                                     body=body).execute()
        result = sheet.values().append(spreadsheetId=SHEETID,
                                       range=f"{sheet_name}!A2:Z",
                                       valueInputOption="USER_ENTERED",
                                       body={
                                           "values": values
                                       }).execute()
        print(f"{(result.get('updates').get('updatedCells'))} cells appended.")

        # Get updated data
        # TODO: get updated data and check if it's updated correctly based on total and total in db

    except HttpError as error:
        print(error)
