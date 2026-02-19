import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


async def send_confirmation_email(email: str, confirmation_url) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
                auth=("api", settings.MAILGUN_API_KEY),
                data={"from": f"SocialAPI <noreply@{settings.MAILGUN_DOMAIN}>",
                      "to": [email],
                      "subject": "Confirm your email - Social API",
                      "text": f"""
                      
                        Please confirm your email by clicking the link below:
                        {confirmation_url}
                        
                        This link will expire in 24 hours.
                        
                        If you didn't register, please ignore this email.
                        
                        Best regards,
                        SocialAPI Team
                    """

                }
            )

        response.raise_for_status()
        logger.info(f"Confirmation email sent to {email}")
        return True

    except Exception as e:
        logger.error(f"Error sending confirmation email: {e}")
        return False




