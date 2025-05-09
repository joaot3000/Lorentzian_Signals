# Add this near the top with other configs
ALLOWED_SENDER = os.getenv('ALLOWED_SENDER', 'alerts@tradingview.com')

# Modify the fetch_unread_emails method in EmailClient class
def fetch_unread_emails(self, limit: int = 10) -> list:
    """Fetch unread emails only from TradingView"""
    if not self.mail:
        logger.error("Not connected to email server")
        return []

    try:
        status, _ = self.mail.select('INBOX')
        if status != "OK":
            return []

        # Search for unread emails from TradingView
        status, messages = self.mail.search(
            None,
            f'(UNSEEN FROM "{ALLOWED_SENDER}")'
        )
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
            
            # Verify it's actually from TradingView
            sender = self._decode_header(email_message['From'])
            if ALLOWED_SENDER.lower() not in sender.lower():
                continue
                
            email_info = {
                'id': email_id.decode(),
                'subject': self._decode_header(email_message['Subject']),
                'from': sender,
                'date': email_message['Date'],
                'body': self._extract_body(email_message)
            }
            emails.append(email_info)
        
        return emails
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        return []

# Update the Telegram notification format for TradingView alerts
def send_email_notification(self, email_data: dict) -> bool:
    """Send formatted TradingView alert to Telegram"""
    alert_subject = email_data.get('subject', 'TradingView Alert')
    alert_body = email_data.get('body', 'No details')
    
    # Extract the important part (usually the first line)
    alert_message = alert_body.split('\n')[0].strip()
    
    message = (
        f"🚨 *TradingView Alert* 🚨\n\n"
        f"*{alert_subject}*\n\n"
        f"```\n{alert_message}\n```\n\n"
        f"_Sent at {email_data['date']}_"
    )
    
    return self._send_message(message, parse_mode="Markdown")
