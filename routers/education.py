"""Education endpoints: AI tutor and quiz generation."""

import logging
from fastapi import APIRouter, Form, HTTPException, Security, status
from services import gemini_service
from dependencies import verify_api_key

router = APIRouter(
    prefix="/education",
    tags=["Education"],
    dependencies=[Security(verify_api_key)],
)
logger = logging.getLogger("sight_companion.education")


@router.post("/tutor")
async def tutor(
    material: str = Form(...),
    question: str = Form(...),
    complexity: str = Form("medium"),
    language: str = Form("en"),
):
    """Answer a question about study material in spoken-style language."""
    if complexity not in ("simple", "medium", "detailed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="complexity must be simple, medium, or detailed",
        )
    try:
        answer = await gemini_service.tutor_from_text(
            material, question, complexity, language
        )
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Error in tutor endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable",
        )


@router.post("/generate-quiz")
async def generate_quiz(
    material: str = Form(...),
    language: str = Form("en"),
):
    """Generate practice questions from study material."""
    try:
        quiz = await gemini_service.generate_quiz(material, language)
        return {"quiz": quiz}
    except Exception as e:
        logger.error(f"Error in generate_quiz endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable",
        )
