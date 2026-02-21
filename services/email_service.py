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
        recipients = os.getenv("NEWSLETTER_RECIPIENTS")

        if not self.sender_email or not self.sender_password:
            raise RuntimeError(
                "Email credentials not configured. "
                "Ensure SENDER_EMAIL and SENDER_PASSWORD are set in .env"
            )
        self.recipients = [email.strip() for email in recipients.split(",")]

    def _markdown_to_html(self, markdown_text: str) -> str:
        return markdown.markdown(markdown_text)

    def _wrap_template(self, html_content: str) -> str:
        return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, sans-serif;">
        
        <table width="100%" cellpadding="0" cellspacing="0" style="padding:20px 0;">
            <tr>
                <td align="center">
                    
                    <table width="700" cellpadding="0" cellspacing="0" style="background:#ffffff; padding:30px; border-radius:8px;">
                        
                        <!-- Header -->
                        <tr>
                            <td align="center" style="padding-bottom:20px;">
                                <h2 style="margin:0; color:#111827;">
                                    The Vasra’s AI Digest
                                </h2>
                                <p style="margin:5px 0 0 0; font-size:14px; color:#6b7280;">
                                    Curated by Agent Vasra
                                </p>
                            </td>
                        </tr>

                        <!-- Divider -->
                        <tr>
                            <td style="border-top:1px solid #e5e7eb; padding-top:20px;">
                                {html_content}
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td align="center" style="padding-top:40px; font-size:12px; color:#9ca3af;">
                                <p style="margin:0;">
                                    You’re receiving this because you subscribed to 
                                    <strong>The Vasra’s AI Digest</strong>.
                                </p>
                                <p style="margin:8px 0 0 0;">
                                    © 2026 Abijeeth Vasra. All rights reserved.
                                </p>
                                <p style="margin:8px 0 0 0;">
                                    Sent with ❤️ by Agent Vasra
                                </p>
                            </td>
                        </tr>

                    </table>

                </td>
            </tr>
        </table>

    </body>
    </html>
    """
    def send_email(self, subject: str, markdown_content: str):

        html_body = self._markdown_to_html(markdown_content)
        full_html = self._wrap_template(html_body)

        message = MIMEMultipart("alternative")
        message["From"] = self.sender_email
        message["Subject"] = subject

        message.attach(MIMEText(full_html, "html"))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            for recipient in self.recipients:

                message = MIMEMultipart("alternative")
                message["From"] = self.sender_email
                message["To"] = recipient
                message["Subject"] = subject

                message.attach(MIMEText(html_body, "html"))

                server.sendmail(
                    self.sender_email,
                    recipient,
                    message.as_string()
                )
