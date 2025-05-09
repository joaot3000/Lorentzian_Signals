#!/usr/bin/env python3
"""
Email to Telegram Bot - Single File Version

This script monitors an email account and sends notifications
to Telegram about new emails.
"""

import os
import time
import imaplib
import email
import requests
import logging
from email.header import decode_header
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailClient:
    """Handles email connection and fetching"""
    
    def __init__(self):
        self.server = os.getenv('EMAIL_SERVER', 'imap.gmail.com')
        self.port = int(os.getenv('EMAIL_PORT', 993))
        self.username = os.getenv('EMAIL_USERNAME')
        self.password = os.getenv('EMAIL_PASSWORD')
        self.mail = None

    def connect(self) -> bool:
        """Connect to email server"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.server, self.port)
            self.mail.login(self.username, self.password)
            return True
        except Exception as e:
            logger.error(f"Email connection failed: {e}")
            return False

    def fetch_unread_emails(self, limit: int = 10) -> list:
        """Fetch unread emails"""
        if not self.mail:
            logger.error("Not connected to email server")
            return []

        try:
            status, _ = self.mail.select('INBOX')
            if status != "OK":
                return []

            status, messages = self.mail.search(None, 'UNSEEN')
            if status != "OK":
                return []

            email_ids = messages[0].split()
            emails = []
            
            for email_id in email_ids[:limit]:
                status, msg_data = self.mail.fetch(email_id, '(RFC822)')
                if status != "OK":
                    continue
                
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                email_info = {
                    'id': email_id.decode(),
                    'subject': self._decode_header(email_message
