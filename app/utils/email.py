from fastapi_mail import FastMail, MessageSchema
from fastapi.templating import Jinja2Templates
from fastapi import Request
from ..models.auth import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory=settings.TEMPLATE_FOLDER)

class EmailSendError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

async def send_verification_email(email: str, token: str, request: Request):
    try:
        verification_link = f"{settings.MAIL_SERVER}/verify-email?token={token}"
        html_content = templates.TemplateResponse(
            "verification_email.html", {"request": request, "verification_link": verification_link}
        )
        
        message = MessageSchema(
            subject="Email Verification",
            recipients=[email],  
            body=html_content.body,  # Rendered HTML content
            subtype="html"
        )
        
        fm = FastMail(settings)
        await fm.send_message(message)
        logger.info(f"Verification email successfully sent to {email}")

    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")
        raise EmailSendError(f"Failed to send verification email to {email}: {str(e)}")

async def send_password_reset_email(email: str, reset_link: str, request: Request):
    try:
        html_content = templates.TemplateResponse(
            "password_reset_email.html", {"request": request, "reset_link": reset_link}
        )
        
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            body=html_content.body,  # Rendered HTML content
            subtype="html"
        )
        
        fm = FastMail(settings)
        await fm.send_message(message)
        logger.info(f"Password reset email successfully sent to {email}")
    
    except Exception as e:
        logger.error(f"Error sending password reset email to {email}: {str(e)}")
        raise EmailSendError(f"Failed to send password reset email to {email}: {str(e)}")
