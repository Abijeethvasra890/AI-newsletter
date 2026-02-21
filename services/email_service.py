import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import markdown
from dotenv import load_dotenv


class EmailService:

    def __init__(self):

        # Load .env automatically
        load_dotenv()

        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")

        if not self.sender_email or not self.sender_password:
            raise RuntimeError(
                "Email credentials not configured. "
                "Ensure SENDER_EMAIL and SENDER_PASSWORD are set in .env"
            )

    def _markdown_to_html(self, markdown_text: str) -> str:
        return markdown.markdown(markdown_text)

    def _wrap_template(self, html_content: str) -> str:
        return f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f6f8;
                    padding: 20px;
                }}
                .container {{
                    max-width: 700px;
                    margin: auto;
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                }}
                h1, h2 {{
                    color: #111827;
                }}
                p {{
                    color: #374151;
                    line-height: 1.6;
                }}
                ul {{
                    padding-left: 20px;
                }}
                .footer {{
                    margin-top: 40px;
                    font-size: 12px;
                    color: #9ca3af;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                {html_content}
                <div class="footer">
                    Sent via <b>The Backprop Bulletin 🚀</b>
                </div>
            </div>
        </body>
        </html>
        """

    def send_email(self, to_email: str, subject: str, markdown_content: str):

        html_body = self._markdown_to_html(markdown_content)
        full_html = self._wrap_template(html_body)

        message = MIMEMultipart("alternative")
        message["From"] = self.sender_email
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(MIMEText(full_html, "html"))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(
                self.sender_email,
                to_email,
                message.as_string()
            )
