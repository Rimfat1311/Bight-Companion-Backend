"""Test suite for Sight Companion API."""

import io
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from main import app
from config import settings

client = TestClient(app)
VALID_HEADERS = {"X-API-Key": settings.app_api_key}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "Sight Companion API"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data
    assert "vision" in data["endpoints"]
    assert "education" in data["endpoints"]


def test_auth_missing():
    # Vision endpoint without API key
    files = {"image": ("test.jpg", b"fake image content", "image/jpeg")}
    response = client.post("/vision/describe-scene", files=files)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"

    # Education endpoint without API key
    response = client.post(
        "/education/tutor",
        data={"material": "test", "question": "test", "complexity": "medium"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_auth_invalid():
    files = {"image": ("test.jpg", b"fake image content", "image/jpeg")}
    response = client.post(
        "/vision/describe-scene",
        headers={"X-API-Key": "wrong-key"},
        files=files,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_vision_invalid_mime_type():
    files = {"image": ("test.txt", b"plain text content", "text/plain")}
    response = client.post(
        "/vision/describe-scene",
        headers=VALID_HEADERS,
        files=files,
    )
    assert response.status_code == 400
    assert "File must be an image" in response.json()["detail"]


def test_vision_empty_image():
    files = {"image": ("empty.jpg", b"", "image/jpeg")}
    response = client.post(
        "/vision/describe-scene",
        headers=VALID_HEADERS,
        files=files,
    )
    assert response.status_code == 400
    assert "Empty image" in response.json()["detail"]


def test_vision_oversized_image():
    # Create an image larger than 10MB (10MB + 1KB)
    oversized_data = b"a" * (10 * 1024 * 1024 + 1024)
    files = {"image": ("large.jpg", oversized_data, "image/jpeg")}
    response = client.post(
        "/vision/describe-scene",
        headers=VALID_HEADERS,
        files=files,
    )
    assert response.status_code == 413
    assert "exceeds maximum limit" in response.json()["detail"]


def test_education_invalid_complexity():
    response = client.post(
        "/education/tutor",
        headers=VALID_HEADERS,
        data={
            "material": "test material",
            "question": "test question",
            "complexity": "super-hard",
        },
    )
    assert response.status_code == 400
    assert "complexity must be simple, medium, or detailed" in response.json()["detail"]


@patch("services.gemini_service.describe_scene", new_callable=AsyncMock)
def test_vision_describe_scene_success(mock_describe):
    mock_describe.return_value = "A clear hallway with a wooden door on the left."
    files = {"image": ("hallway.png", b"fake-png-bytes", "image/png")}
    response = client.post(
        "/vision/describe-scene",
        headers=VALID_HEADERS,
        files=files,
        data={"language": "en"},
    )
    assert response.status_code == 200
    assert response.json() == {"description": "A clear hallway with a wooden door on the left."}
    mock_describe.assert_awaited_once_with(b"fake-png-bytes", language="en", mime_type="image/png")


@patch("services.gemini_service.read_text", new_callable=AsyncMock)
def test_vision_read_text_success(mock_read_text):
    mock_read_text.return_value = "ROOM 101 - EXIT"
    files = {"image": ("sign.jpeg", b"fake-jpeg-bytes", "image/jpeg")}
    response = client.post(
        "/vision/read-text",
        headers=VALID_HEADERS,
        files=files,
    )
    assert response.status_code == 200
    assert response.json() == {"text": "ROOM 101 - EXIT"}
    mock_read_text.assert_awaited_once_with(b"fake-jpeg-bytes", mime_type="image/jpeg")


@patch("services.gemini_service.tutor_from_text", new_callable=AsyncMock)
def test_education_tutor_success(mock_tutor):
    mock_tutor.return_value = "Gravity is the force that pulls objects toward each other."
    response = client.post(
        "/education/tutor",
        headers=VALID_HEADERS,
        data={
            "material": "Gravity is a fundamental force...",
            "question": "What is gravity?",
            "complexity": "simple",
            "language": "en",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"answer": "Gravity is the force that pulls objects toward each other."}
    mock_tutor.assert_awaited_once_with(
        "Gravity is a fundamental force...",
        "What is gravity?",
        "simple",
        "en",
    )
