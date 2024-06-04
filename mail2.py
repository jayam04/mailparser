import email
import re

class Mail:
    def __init__(self, id: str, raw_email: str, sender: str = None, recipient: str = None, subject: str = None, date: str = None):
        # Basics of email
        self.id = id
        self.raw_email = raw_email
        self.message = email.message_from_string(self.raw_email)

        self.subject = subject
        self.date = date
        self.sender = sender
        self.recipient = recipient
        self.original_sender = sender

        self.from_server = None
        self.body = {}

        # Parsing mail
        self.parse()
        self.parse_body()
        self.find_server()

    def __str__(self):
        string = ""
        string += f"{self.id}: {self.subject}\n"
        string += f"Sender: {self.sender}\n"
        string += f"Original Sender: {self.original_sender}\n"
        string += f"Recipient: {self.recipient}\n"
        string += f"Date: {self.date}\n"
        string += f"From Server: {self.from_server}\n"
        string += "-"*84 + '\n'
        string += f"Body: {self.body}\n"
        string += "-"*84 + '\n'
        string += f"Raw Email: {self.raw_email}\n"

        return string

    def parse(self):
        """
        Parses the raw email into a dictionary.
        """
        if self.message.get("Subject"):
            self.subject = self.message.get("Subject")
        if self.message.get("From"):
            self.sender = self.message.get("From").split("<")[1].split(">")[0]
        if self.message.get("Date"):
            self.date = self.message.get("Date")

    def parse_body(self):
        """
        Parses the body of type text/plain, text/html, or multipart/alternative.
        """
        if self.message.is_multipart():
            for part in self.message.walk():
                print(part.get_content_type())
                if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                    self.body[part.get_content_type()] = part.get_payload()
        else:
            self.body[self.message.get_content_type] = self.message.get_payload()
        
        for key in self.body.keys():
            self.body[key] = self.body[key].replace("=\r\n", "\n")

    def find_server(self):
        """
        Finds the server from which the email was sent.
        """
        smtp_domain = self.message.get("Received")
        if smtp_domain:
            self.from_server = smtp_domain.split("from")[1].split("by")[0].strip().split()[0]



class Gmail(Mail):
    def __init__(self, id: str, raw_email: str, sender: str = None, recipient: str = None):
        super().__init__(id, raw_email, sender, recipient)

        self.update_details_from_message()


    def update_details_from_message(self):
        forward_pattern = re.compile(
                r"---------- Forwarded message --------- "
                r"From: (.*?) "
                r"Date: (.*?) "
                r"Subject: (.*?) "
                r"To: (.*?) "
                )
        return
        forward_match = forward_pattern.search(self.body["text/plain"])
        if forward_match:
            # Extract the details from the forwarded section
            self.original_sender = forward_match.group(1).split("<")[1].split(">")[0]
            # TODO: get date, subject, etc from email.
