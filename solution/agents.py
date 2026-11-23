"""Runner factory for local use with an explicit in-memory session service."""

from google.adk.runners import Runner

from .agent import root_agent, session_service


def create_runner() -> Runner:
    """Create a runner whose sessions retain context in memory for this process."""
    return Runner(
        agent=root_agent,
        app_name="bettys_bird_boutique",
        session_service=session_service,
    )
