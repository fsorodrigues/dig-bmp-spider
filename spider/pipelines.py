# data-handling modules
import json
# import pandas as pd

# environment variables modules
import os
from dotenv import load_dotenv

# setting up module to read .env file for environment variables
APP_ROOT = os.path.join(os.path.dirname('__file__'), '.') # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

# import requests

# scrapy exceptions
from scrapy.exceptions import DropItem

# gsheets api modules
import httplib2
from apiclient import discovery
import auth_google as ag

# for email notifications
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# other utils
from datetime import datetime
import time

# Google authentication + settings
GSHEET_CREDENTIALS = ag.get_authorization_url()
http = GSHEET_CREDENTIALS.authorize(httplib2.Http())
service = discovery.build('sheets', 'v4',http=http,cache_discovery=False)
now = datetime.now()
sheet = 'Sheet1'
full_range = 'A:I'
id_range = 'B:B'
value_render_option = 'FORMATTED_VALUE'
value_input_option = 'RAW'
insert_data_option = 'INSERT_ROWS'
major_dimension = 'COLUMNS' # determines if gsheet will return/receive rows or columns

class CheckDuplicatesPipeline(object):
    #__init__ can be used to set values important for this class/pipeline
    def __init__(self):
        # getting environment variable value
        self.SPREADSHEET_ID = os.getenv('GSHEET_SPREADSHEET_ID')
        # requests data from gsheet
        self.GOOGLE_REQUEST = service.spreadsheets().values()\
            .get(spreadsheetId=self.SPREADSHEET_ID,
            range=f'{sheet}!{id_range}',
            valueRenderOption=value_render_option,
            majorDimension=major_dimension)
        self.GOOGLE_RESPONSE = self.GOOGLE_REQUEST.execute()
        # response is a list of lists
        self.list_ids = self.GOOGLE_RESPONSE['values'][0][1:]

    def process_item(self, item, spider):
        # iterating over each item handed to pipelines
        # checking if contained in list of ids gathered from gsheet
        # if item not in list, returning it here hands it to next pipeline >>>
        if item['id'] not in self.list_ids:
            return item
        # >>> else, item is dropped and doesn't reach next pipeline
        # this is done by raising an exception
        else:
            raise DropItem(f'{item["id"]} already scraped')

class ParseTime(object):
    def process_item(self, item, spider):
        item['date_created'] = now.isoformat(timespec='seconds')

        try:
            item['date'] = item['date'].isoformat(timespec='seconds')
        except:
            item['date'] = item['date']

        return item

class StorePipeline(object):
    def __init__(self):
        self.SPREADSHEET_ID = os.getenv('GSHEET_SPREADSHEET_ID')

    def process_item(self,item,spider):
        try:
            self.saveToGSheet(item)
        except:
            time.sleep(10)
            self.saveToGSheet(item)

        return item

    #########################################################
    ################## UTILS ################################
    #########################################################
    def saveToGSheet(self,data):
        # appending values to gsheet
        # major_dimension
        request = service.spreadsheets().values()\
            .append(spreadsheetId=self.SPREADSHEET_ID,
                range=f'{sheet}!{full_range}',
                valueInputOption=value_input_option,
                insertDataOption=insert_data_option,
                body={
                "values":[[value] for value in data.values()], # list comprehension, creates list of lists that is to be inputed to sheet
                "majorDimension":major_dimension }
            )
        response = request.execute()
        return response

class SendNotification(object):
    # this task is slightly different than the others.
    # processing the items here creates a long string that will became the body of the email notifications
    def __init__(self):
        self.GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
        # creates variables available in this class to store the text
        self.text = []
        self.html = []

    def process_item(self, item, spider):
        self.text.append(f'{item["name"]} - {item["license"]}\n{item["action"]}\nAccess at: {item["url"]}')
        self.html.append(f'''
            <h5 style="margin: 25px 0 5px 0">{item["name"]} - {item["license"]}, {datetime.strptime(item["date"],"%Y-%m-%dT%H:%M:%S").strftime("%b %d, %Y")}</h5>
            <a href="{item["url"]}"><p style="margin: 0 0 10px 0">{item["action"]}</p></a>
        ''')
        return item

    # close_spider is called once by scrapy before the end of this pipeline
    # this sends the email notification
    def close_spider(self, spider):
        # checks if there's any content to be sent
        if len(self.text) > 0:
            # gets today's date
            today = now.strftime("%a, %d %b")
            # wrangles text
            text_body = "\n\n".join(self.text)
            text_html = "\n".join(self.html)
            text = f'New reports scraped on {today}\n\n{text_body}'
            html = f'''<html>
            <body>
                <div>
                    <h3>New reports scraped on {today}</h3>
                    {text_html}
                </div>
            </body>
            </html>'''

            # sets email fields
            email_from = 'frodrigues@vtdigger.org'
            email_to = 'VTDigger'
            email_subscribers = [email_from,"agalloway@vtdigger.org","cmeyn@vtdigger.org","mjohnson@vtdigger.org","mfaher@vtdigger.org"]

            # creates message contents
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Board of Medical Practice {now.strftime("%m/%d/%y")}'
            msg['From'] = 'Board of Medical Practice'
            msg['To'] = email_to
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # logs into gmail (needs to change one setting in account, but easy step -- tho less secure) and sends email
            # using this because it was faster, but there's probably a way of leveraging a gmail API to make this in a more secure way.
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.ehlo()
            s.starttls()
            s.login(email_from, self.GMAIL_PASSWORD)
            s.sendmail(email_from, email_subscribers, msg.as_string())
            s.quit()

        else:
            pass
