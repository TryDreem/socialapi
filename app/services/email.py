import httpx
import logging
from app.config import settings
from app.core.utils import mask_email

logger = logging.getLogger(__name__)


async def send_confirmation_email(email: str, confirmation_url) -> bool:

    logger.info(f"📤 Sending confirmation email to {mask_email(email)}")

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
                        
                        This link will expire in 1 hour.
                        
                        If you didn't register, please ignore this email.
                        
                        Best regards,
                        SocialAPI Team
                    """

                }
            )

        response.raise_for_status()
        logger.info(f"✅ Confirmation email sent successfully to {mask_email(email)}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to send email to {mask_email(email)}: {e}")
        return False




