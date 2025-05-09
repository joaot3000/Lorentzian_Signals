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
                    'subject': self._decode_header(email_message['Subject']),
                    'from': self._decode_header(email_message['From']),
                    'date': email_message['Date'],
                    'body': self._extract_body(email_message)
                }
                emails.append(email_info)
            
            return emails
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    def _decode_header(self, header):
        """Decode email headers"""
        if header is None:
            return ""
        decoded = decode_header(header)
        return ''.join(
            t[0].decode(t[1] or 'utf-8') if isinstance(t[0], bytes) else t[0]
            for t in decoded
        )

    def _extract_body(self, email_message):
        """Extract email body text"""
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()
        return body

    def disconnect(self):
        """Close email connection"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass

class TelegramBot:
    """Handles Telegram notifications"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_email_notification(self, email_data: dict) -> bool:
        """Send formatted email notification"""
        subject = email_data.get('subject', 'No Subject')
        sender = email_data.get('from', 'Unknown Sender')
        body_preview = (email_data.get('body', '')[:200] + '...') if len(email_data.get('body', '')) > 200 else email_data.get('body', '')
        
        message = (
            f"📧 *New Email Received*\n\n"
            f"*From:* {sender}\n"
            f"*Subject:* {subject}\n\n"
            f"*Preview:*\n{body_preview}"
        )
        
        return self._send_message(message, parse_mode="Markdown")

    def _send_message(self, text: str, parse_mode: str = None) -> bool:
        """Send raw message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

def main():
    """Main execution loop"""
    email_client = EmailClient()
    telegram_bot = TelegramBot()
    
    check_interval = int(os.getenv('CHECK_INTERVAL', 300))  # 5 minutes default
    max_emails = int(os.getenv('MAX_EMAILS', 10))
    
    logger.info("Starting email monitoring service...")
    
    while True:
        try:
            # Connect to email server
            if not email_client.connect():
                logger.error("Failed to connect to email server. Retrying...")
                time.sleep(check_interval)
                continue
            
            # Fetch unread emails
            unread_emails = email_client.fetch_unread_emails(limit=max_emails)
            
            if unread_emails:
                logger.info(f"Found {len(unread_emails)} new emails")
                
                for email_data in unread_emails:
                    # Send notification via Telegram
                    if telegram_bot.send_email_notification(email_data):
                        logger.info(f"Notification sent for email from {email_data['from']}")
                    else:
                        logger.error(f"Failed to send notification for email from {email_data['from']}")
            
            email_client.disconnect()
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        
        # Wait before next check
        logger.info(f"Next check in {check_interval} seconds at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(check_interval)

if __name__ == "__main__":
    main()
