def mask_email(email: str) -> str:
    try:
        username, domain = email.split("@")
        masked_username = f"{username[:3]}***"
        return f"{masked_username}@{domain}"
    except (ValueError, IndexError):
        return "***@***"
