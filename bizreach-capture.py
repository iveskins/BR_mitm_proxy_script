import logging
import html
import json
#import os
from datetime import datetime
#from bs4 import BeautifulSoup
from mitmproxy import http
import re
import sqlite3

# Import the new HTML parser class
from html_parser import HTMLTableParser

class Handler:
    def __init__(self):
        # Log filename for application logs
        app_log_filename = f"mitmproxy_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(level=logging.WARNING, 
                            format='%(asctime)s %(levelname)s %(name)s %(message)s',
                            filename=app_log_filename)
        self.app_logger = logging.getLogger('app_logger')

        # Log filename for output data
        self.data_log_filename = f"mitmproxy_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.data_logger = logging.getLogger('data_logger')
        data_handler = logging.FileHandler(self.data_log_filename)
        data_formatter = logging.Formatter('%(message)s')
        data_handler.setFormatter(data_formatter)
        self.data_logger.addHandler(data_handler)
        self.data_logger.setLevel(logging.INFO)

        self.db_filename = 'jobs.db'

    def response(self, flow: http.HTTPFlow) -> None:
        target_url = "/dwr/call/plaincall/candidateAjaxMessage.getMessageDetailContent.dwr"
        self.app_logger.warning('URL: %s', flow.request.pretty_url)

        if target_url in flow.request.pretty_url:
            response_content = flow.response.get_text()
            match = re.search(r'(html:\")(.+)(\",)', response_content, re.DOTALL)
            if match:
                self.app_logger.warning('re: match')
                html_content = match.group(2)
                decoded_html = html.unescape(html_content)
                decoded_text = bytes(decoded_html, 'utf-8').decode('unicode_escape')

                # Use the new HTML parser
                parser = HTMLTableParser(decoded_text)
                target_classes = ["pg-message-job-detail-table", "sg-table sg-table-style-add-sideborders breath-m pg-job-detail-table sg-box"]
                tables_data = parser.parse_tables(target_classes)

                # Convert tables data to string for logging and database insertion
                formatted_data = json.dumps(tables_data, indent=4, ensure_ascii=False)

                # Insert data into database
                self.insert_into_db(flow.request.pretty_url, formatted_data)

                # Log extracted data to a separate file
                self.data_logger.info(f"URL: {flow.request.pretty_url}\nExtracted Data:\n{formatted_data}\n-------------------------------------------------\n\n")
            else:
                self.app_logger.warning('re: nomatch')

    def insert_into_db(self, url, data):
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()

        job_id = self.extract_job_id(data)

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY, 
                job_details TEXT, 
                gpt_response TEXT, 
                batch_status TEXT, 
                sync_status TEXT
            )
        ''')

        cursor.execute('''
            INSERT OR REPLACE INTO jobs (job_id, job_details)
            VALUES (?, ?)
        ''', (job_id, data))

        conn.commit()
        conn.close()

    def extract_job_id(self, data):
        try:
            data_json = json.loads(data)
            # Assuming job ID is in the 'sg-table sg-table-style-add-sideborders breath-m pg-job-detail-table sg-box' section
            return data_json.get('sg-table sg-table-style-add-sideborders breath-m pg-job-detail-table sg-box', {}).get('求人番号')
        except json.JSONDecodeError:
            self.app_logger.warning("Failed to decode JSON for extracting job ID")
            return None


addons = [Handler()]

