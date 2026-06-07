import os, filetype, logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}

# Local fallback dir when S3 not configured
LOCAL_UPLOAD_DIR = "uploads"

class S3Service:
    def __init__(self):
        self.endpoint_url  = os.environ.get("R2_ENDPOINT_URL")
        self.access_key    = os.environ.get("R2_ACCESS_KEY_ID")
        self.secret_key    = os.environ.get("R2_SECRET_ACCESS_KEY")
        self.bucket        = os.environ.get("R2_BUCKET_NAME")
        self.s3_configured = all([self.endpoint_url, self.access_key, self.secret_key, self.bucket])
        if self.s3_configured:
            logger.info("S3/R2 storage configured")
        else:
            logger.warning("S3/R2 not configured - using local disk fallback")

    def _get_session(self):
        import aioboto3
        return aioboto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    async def validate_file(self, file_content: bytes, filename: str) -> Tuple[bool, str]:
        if len(file_content) > MAX_FILE_SIZE:
            return False, f"File exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit"
        # TXT files have no magic bytes — allow by extension
        if filename.lower().endswith(".txt"):
            return True, ""
        kind = filetype.guess(file_content)
        if kind is None:
            return False, "Could not detect file type"
        if kind.mime not in ALLOWED_MIME_TYPES:
            return False, f"Type '{kind.mime}' not allowed. Use PDF, DOCX or TXT"
        return True, ""

    async def upload_file(self, file_content: bytes, key: str) -> Optional[str]:
        if not self.s3_configured:
            return await self._upload_local(file_content, key)
        try:
            session = self._get_session()
            async with session.client("s3", endpoint_url=self.endpoint_url) as s3:
                await s3.put_object(Bucket=self.bucket, Key=key, Body=file_content)
                logger.info(f"Uploaded to S3: {key}")
                return key
        except Exception as e:
            logger.error(f"S3 upload failed: {e} — falling back to local")
            return await self._upload_local(file_content, key)

    async def _upload_local(self, file_content: bytes, key: str) -> str:
        import os
        local_path = os.path.join(LOCAL_UPLOAD_DIR, key.replace("/", "_"))
        os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(file_content)
        logger.info(f"Saved locally: {local_path}")
        return key

    async def download_file(self, key: str) -> Optional[bytes]:
        if not self.s3_configured:
            local_path = os.path.join(LOCAL_UPLOAD_DIR, key.replace("/", "_"))
            if os.path.exists(local_path):
                with open(local_path, "rb") as f:
                    return f.read()
            return None
        try:
            session = self._get_session()
            async with session.client("s3", endpoint_url=self.endpoint_url) as s3:
                resp = await s3.get_object(Bucket=self.bucket, Key=key)
                return await resp["Body"].read()
        except Exception:
            return None

    async def delete_file(self, key: str) -> bool:
        if not self.s3_configured:
            local_path = os.path.join(LOCAL_UPLOAD_DIR, key.replace("/", "_"))
            if os.path.exists(local_path):
                os.remove(local_path)
            return True
        try:
            session = self._get_session()
            async with session.client("s3", endpoint_url=self.endpoint_url) as s3:
                await s3.delete_object(Bucket=self.bucket, Key=key)
                return True
        except Exception:
            return False

    async def generate_presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        if not self.s3_configured:
            return f"/uploads/{key.replace('/', '_')}"
        try:
            session = self._get_session()
            async with session.client("s3", endpoint_url=self.endpoint_url) as s3:
                url = await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": key},
                    ExpiresIn=expiration,
                )
                return url
        except Exception:
            return None

s3_service = S3Service()
