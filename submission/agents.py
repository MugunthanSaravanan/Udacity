"""Local ADK runner and short-term in-memory session helpers."""

from google.adk.runners import Runner
from google.genai import types

from .agent import APP_NAME, root_agent, session_service


def create_runner() -> Runner:
    """Create a runner backed by the root agent and in-memory sessions."""
    return Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )


async def create_session(user_id: str) -> str:
    """Create a session and return its ID for subsequent turns."""
    if not user_id.strip():
        raise ValueError("user_id must not be empty")
    session = await session_service.create_session(app_name=APP_NAME, user_id=user_id)
    return session.id


async def send_message(runner: Runner, user_id: str, session_id: str, message: str) -> str:
    """Submit one user turn and return the final response text.

    Reuse the same ``user_id`` and ``session_id`` for follow-up turns so ADK can
    include the conversation history from the in-memory session service.
    """
    if not message.strip():
        raise ValueError("message must not be empty")
    content = types.Content(role="user", parts=[types.Part(text=message)])
    final_text: list[str] = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content:
            final_text.extend(
                part.text for part in event.content.parts or [] if getattr(part, "text", None)
            )
    return "\n".join(final_text) if final_text else "The agent returned no final text response."
