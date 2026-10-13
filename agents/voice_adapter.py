from agents.ai_service import process_customer_message


def handle_voice_text(
    transcript: str,
    session_id: str
) -> dict:
    """
    Receives transcribed customer speech.

    Returns the AI response as structured text.

    Audio processing is handled by the voice system.
    """

    result = process_customer_message(
        message=transcript,
        session_id=session_id
    )

    return {
        "session_id": session_id,
        "transcript": transcript,
        "intent": result["intent"],
        "response_text": result["response"],
        "action": result["action"]
    }