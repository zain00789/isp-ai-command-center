from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


# 1. Voice service health check
def test_voice_health():
    response = client.get("/api/v1/voice/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "voice"
    assert response.json()["mode"] == "real"


# 2. Empty audio must be rejected
def test_empty_audio_rejected():
    response = client.post(
        "/api/v1/voice/transcribe",
        files={
            "file": ("empty.wav", b"", "audio/wav")
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Audio file is empty"


# 3. Unsupported file format must be rejected
def test_unsupported_audio_format_rejected():
    response = client.post(
        "/api/v1/voice/transcribe",
        files={
            "file": ("notes.txt", b"hello", "text/plain")
        }
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported audio format"


# 4. Audio larger than 10 MB must be rejected
def test_oversized_audio_rejected():
    large_audio = b"0" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/api/v1/voice/transcribe",
        files={
            "file": ("large.wav", large_audio, "audio/wav")
        }
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Audio file exceeds the 10 MB limit"


# 5. Missing audio upload must be rejected
def test_missing_audio_file():
    response = client.post("/api/v1/voice/transcribe")

    assert response.status_code == 422


# 6. Invalid content type must be rejected
def test_invalid_content_type():
    response = client.post(
        "/api/v1/voice/transcribe",
        files={
            "file": ("fake.wav", b"fake audio", "application/octet-stream")
        }
    )

    assert response.status_code == 415


# 7. Unsupported image upload must be rejected
def test_image_upload_rejected():
    response = client.post(
        "/api/v1/voice/transcribe",
        files={
            "file": ("picture.png", b"fake image", "image/png")
        }
    )

    assert response.status_code == 415

def test_voice_chat_requires_account_verification():
    response = client.post(
        "/api/v1/voice/chat",
        json={
            "text": "Show my bill for ISP12345",
            "session_id": "test-voice-001"
        }
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "account_support"
    assert response.json()["action"] == "verification_required"
    assert "customer verification" in response.json()["response"].lower()