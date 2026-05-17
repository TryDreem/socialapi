import uuid
import aioboto3
import logging
from fastapi import UploadFile
from app.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    async def upload_file(self, file: UploadFile, user_id: str) -> str:
        logger.info("Trying to upload file to S3")
        filename = f"posts/user_{user_id}/{uuid.uuid4()}_{file.filename}"
        await file.seek(0)
        data = await file.read()

        session = self._get_session()

        async with session.client("s3", endpoint_url=settings.SUPABASE_ENDPOINT) as s3:
            await s3.put_object(
                Bucket=settings.SUPABASE_BUCKET,
                Key=filename,
                Body=data,
                ContentType=file.content_type,
                )

        logger.info("Uploading file to S3")

        return f"{settings.SUPABASE_ENDPOINT[:-2]}/object/public/{settings.SUPABASE_BUCKET}/{filename}"


    async def delete_file(self, file_url: str) -> None:
        key = file_url.split(settings.SUPABASE_BUCKET)[-1].lstrip("/")
        session = self._get_session()
        async with session.client("s3", endpoint_url=settings.SUPABASE_ENDPOINT) as s3:
            await s3.delete_object(
                Bucket=settings.SUPABASE_BUCKET,
                Key=key,
            )
        logger.info("Image was deleted from S3")


    def _get_session(self):
        session = aioboto3.Session(
            aws_access_key_id=settings.SUPABASE_ACCESS_KEY_ID,
            aws_secret_access_key=settings.SUPABASE_SECRET_ACCESS_KEY,
            region_name=settings.SUPABASE_REGION,
        )
        return session

