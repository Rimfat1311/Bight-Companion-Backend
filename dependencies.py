"""Dependencies for authentication and request validation."""

import secrets
import logging
from typing import Tuple
from fastapi import HTTPException, Security, UploadFile, status
from fastapi.security import APIKeyHeader
from config import settings

logger = logging.getLogger("sight_companion")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# 413 Payload / Content Too Large
HTTP_413_STATUS = getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verifies the X-API-Key header using constant-time comparison."""
    if not api_key or not secrets.compare_digest(api_key, settings.app_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return api_key


async def validate_image_file(image: UploadFile) -> Tuple[bytes, str]:
    """Validates image content type and size limit (10 MB). Returns (image_bytes, content_type)."""
    content_type = image.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    image_bytes = await image.read()
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty image provided",
        )

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=HTTP_413_STATUS,
            detail="Image size exceeds maximum limit of 10 MB",
        )

    return image_bytes, content_type
