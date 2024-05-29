import email
import re
from bs4 import BeautifulSoup
from email.parser import BytesParser


class Mail:
    def __init__(self, id: str, raw_email: str):
        self.id = id
        self.raw_email = raw_email
        self.message = email.message_from_string(self.raw_email)

        self.subject = None
        self.date = None
        self.sender_email = None
        self.original_sender = None
        self.original_sender_name = None
        self.recipient = None

        self.raw_body = {}
        self.body = {}

        self.from_server = None
        self.type = None

        self.parse()
        self.parse_body()
        self.find_from_server()
        self.find_original_sender()

    def __str__(self) -> str:
        if self.subject:
            return f"{self.id}: {self.subject}"
        else:
            return f"{self.id}: No Subject"

    def parse(self):
        """
        Parses the raw email into a dictionary.
        """
        self.subject = self.message.get("Subject")
        self.sender_email = self.message.get("From").split("<")[1].split(">")[0]
        self.date = self.message.get("Date")
        self.recipient = self.message.get("To")

    def parse_body(self):
        """
        Parses the body of type text/plain, text/html, or multipart/alternative.
        """
        if self.message.is_multipart():
            for part in self.message.walk():
                print(part.get_content_type())
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    self.raw_body[part.get_content_type()] = part.get_payload()
        else:
            self.raw_body = self.message.get_payload()
            self.body_type.add(self.message.get_content_type())
        
        self.body = self.raw_body
        for key in self.body.keys():
            self.body[key] = self.body[key].replace("=\r\n", "")
            self.body[key] = self.body[key].replace("\r\n", " ")

    def find_from_server(self):
        """
        Finds the server that the email was sent from.
        """
        smtp_domain = self.message.get("Received")
        if smtp_domain:
            self.from_server = smtp_domain.split("from")[1].split("by")[0].strip().split()[0]
            # Check if the server is of Google
            if self.from_server.endswith("smtp.gmail.com") or self.from_server.endswith("google.com"):
                self.type = "gmail"
        else:
            self.from_server = None

    def find_original_sender(self):
        """
        Finds the original sender of the email.
        """
        if self.type == "gmail":
            forward_pattern = re.compile(
                r"---------- Forwarded message --------- "
                r"From: (.*?) "
                r"Date: (.*?) "
                r"Subject: (.*?) "
                r"To: (.*?) "
                )

        # Find the forwarded message section
        forward_match = forward_pattern.search(self.raw_body["text/plain"])  # TODO: add fail safe for html body
        if forward_match:
            # Extract the details from the forwarded section
            self.original_sender = forward_match.group(1).split("<")[1].split(">")[0]
            self.original_sender_name = forward_match.group(1).split("<")[0].strip()
            date_field = forward_match.group(2)
            subject_field = forward_match.group(3)
            to_field = forward_match.group(4)
            
            # Remove the forwarded section from the email body
            self.body["text/plain"] = forward_pattern.sub("", self.raw_body["text/plain"])



    def print_verbose(self, print_body: bool = True, print_raw: bool = False):
        print(f"{self.id}: {self.subject}")
        print(f"Sender: {self.sender_email}")
        print(f"Original Sender: {self.original_sender_name} ({self.original_sender})")
        print(f"Recipient: {self.recipient}")
        print(f"Date: {self.date}")
        print(f"From Server: {self.from_server}")
        print(f"Type: {self.type}")
        if print_body:
            print("-"*84)
            print(f"Body: {self.body}")
        if print_raw:
            print("-"*84)
            print(f"Raw Email: {self.raw_email}")



class ParsedMail:
    def __init__(self, mail: Mail, parser = None):
        self.mail = mail
        self.id = mail.id

        self.variables = {}

    def parse(self):
        if self.mail.original_sender == "services@cdslindia.co.in":
            soup = BeautifulSoup(self.mail.body["text/html"], 'html.parser')
            demat_account_match = re.search(r'account ending with \*(\d+)', self.mail.body["text/plain"])
            self.variables["demat_account"] = "*" + demat_account_match.group(1) if demat_account_match else None

            # Extract the table values using regex
            transactions = []
            table_rows = soup.find_all('tr')
            for row in table_rows[1:]:  # Skip the header row
                cols = row.find_all('td')
                if len(cols) == 6:
                    sr_no = cols[0].text.strip()
                    company_name = re.sub(r'\s+', ' ', cols[1].text.strip())  # Replace multiple spaces with single space
                    isin = re.sub(r'\s+', '', cols[2].text.strip())  # Remove any extra spaces within ISIN
                    quantity = cols[3].text.strip().replace(' ', '')  # Remove spaces within quantity
                    debit_credit = cols[4].text.strip()
                    date_time = cols[5].text.strip()
                    transactions.append((sr_no, company_name, isin, quantity, debit_credit, date_time))
            self.variables["transactions"] = transactions

    def get_config(self):
        return {
            "originalSender": self.mail.original_sender,
            "originalSenderName": self.mail.original_sender_name,
            "sender": self.mail.sender_email,
            "subject": self.mail.subject,
        }
    
    def generate_sheet_data(self, row_rules):
        data = []
        for transaction in self.variables["transactions"]:
            row = []
            for i in row_rules:
                if i == "":
                    row.append("")
                elif "#" == i[0]:
                    row.append(transaction[int(i[1:]) - 1])
                elif "$" == i[0]:
                    row.append(self.variables[i[1:]])
            data.append(row)
        return data

    def print_variables(self):
        print(f"{self.id}: {self.variables}")

