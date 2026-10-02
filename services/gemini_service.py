"""Gemini integration for Sight Companion vision and education features."""

from google import genai
from google.genai import types
from config import settings
import prompts

# Client is created lazily so the app can start even without a key (for /health)
_client = None


def get_client():
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def _image_part(image_bytes: bytes, mime_type: str = "image/jpeg"):
    return types.Part.from_bytes(data=image_bytes, mime_type=mime_type)


def _lang_note(language: str) -> str:
    if language == "ur":
        return "Respond in Urdu."
    return "Respond in English."


async def describe_scene(
    image_bytes: bytes, language: str = "en", mime_type: str = "image/jpeg"
) -> str:
    client = get_client()
    response = await client.aio.models.generate_content(
        model=settings.model_name,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"{prompts.SCENE_DESCRIPTION_SYSTEM}\n{_lang_note(language)}"
                    ),
                    _image_part(image_bytes, mime_type=mime_type),
                ],
            )
        ],
    )
    return (response.text or "").strip()


async def read_text(
    image_bytes: bytes, mime_type: str = "image/jpeg"
) -> str:
    client = get_client()
    response = await client.aio.models.generate_content(
        model=settings.model_name,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompts.TEXT_READING_SYSTEM),
                    _image_part(image_bytes, mime_type=mime_type),
                ],
            )
        ],
    )
    return (response.text or "").strip()


async def ask_about_image(
    image_bytes: bytes,
    question: str,
    language: str = "en",
    mime_type: str = "image/jpeg",
) -> str:
    client = get_client()
    response = await client.aio.models.generate_content(
        model=settings.model_name,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=(
                            f"{prompts.TUTOR_SYSTEM}\n{_lang_note(language)}\n\n"
                            f"Question: {question}"
                        )
                    ),
                    _image_part(image_bytes, mime_type=mime_type),
                ],
            )
        ],
    )
    return (response.text or "").strip()


async def tutor_from_text(
    material: str,
    question: str,
    complexity: str = "medium",
    language: str = "en",
) -> str:
    client = get_client()
    prompt = (
        f"{prompts.TUTOR_SYSTEM}\n{_lang_note(language)}\n"
        f"Complexity level: {complexity}\n\n"
        f"Study material:\n{material}\n\n"
        f"Student question: {question}"
    )
    response = await client.aio.models.generate_content(
        model=settings.model_name,
        contents=prompt,
    )
    return (response.text or "").strip()


async def generate_quiz(material: str, language: str = "en") -> str:
    client = get_client()
    prompt = (
        f"{prompts.QUIZ_SYSTEM}\n{_lang_note(language)}\n\n"
        f"Study material:\n{material}"
    )
    response = await client.aio.models.generate_content(
        model=settings.model_name,
        contents=prompt,
    )
    return (response.text or "").strip()
