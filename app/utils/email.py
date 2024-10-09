from fastapi_mail import FastMail, MessageSchema
from ..models.auth import settings
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSendError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


async def send_verification_email(email: str, token: str):
    try:
        verification_link = f"{settings.MAIL_SERVER}/verify-email?token={token}"
        message = MessageSchema(
            subject="Email Verification",
            recipients=[email],  
            body=f"Click on the following link to verify your email: {verification_link}",
            subtype="html"  
        )
        fm = FastMail(settings)
        await fm.send_message(message)
        logger.info(f"Verification email successfully sent to {email}")

    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")
        raise EmailSendError(f"Failed to send verification email to {email}: {str(e)}")
   
    except TimeoutError:
        logger.error(f"Timeout occurred while sending email to {email}")
        raise EmailSendError(f"Timeout occurred while sending email to {email}")
    
    except ValueError as ve:
        logger.error(f"Invalid email address: {email} | Error: {str(ve)}")
        raise EmailSendError(f"Invalid email address: {email}")
