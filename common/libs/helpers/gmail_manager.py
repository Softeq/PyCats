import imaplib
import logging

log = logging.getLogger(__name__)


class GmailManager:

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __enter__(self):
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(self.email, self.password)
        return self

    def __exit__(self, *args):
        self.mail.logout()

    def get_emails(self, subject):
        emails = []
        log.info(f"Getting messages from inbox with subject '{subject}'")
        self.mail.select('inbox')
        result, data = self.mail.search(None, f'(UNSEEN SUBJECT "{subject}")')
        log.info(f"Result {result}")
        uids = data[0].split()
        if result == 'OK':
            for uid in uids:
                result, email = self.mail.fetch(uid, '(RFC822)')
                email_body = email[0][1].decode('utf-8')
                emails.append(email_body)
        log.info(f"Collected {len(emails)} emails")
        return emails

    def remove_emails(self):
        self.mail.select('inbox')
        result, data = self.mail.search(None, 'ALL')
        uids = data[0].split()
        for uid in uids:
            self.mail.store(uid, '+FLAGS', '\\Deleted')
        self.mail.expunge()
        log.info(f"Deleting all emails in {self.email}")

    def wait_until_email_appears(self, subject="", timeout=20):
        import time
        end_time = time.time() + timeout
        while True:
            emails = self.get_emails(subject)
            if emails:
                return emails
            time.sleep(2)
            if time.time() > end_time:
                break
        raise Exception(f"Message '{subject}' not found")
