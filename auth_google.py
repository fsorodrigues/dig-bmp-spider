import os
from oauth2client.service_account import ServiceAccountCredentials

GSHEETS_SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
GSHEETS_CLIENT_SECRET_FILE = 'gsheet-auth.json'
GSHEETS_APPLICATION_NAME = 'Google Sheets API VTDigger'

def get_authorization_url():
    creds = ServiceAccountCredentials.from_json_keyfile_name(GSHEETS_CLIENT_SECRET_FILE, GSHEETS_SCOPE)
    return creds
