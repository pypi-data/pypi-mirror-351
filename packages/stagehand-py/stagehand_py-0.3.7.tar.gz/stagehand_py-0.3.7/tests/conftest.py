import asyncio

import pytest

# Set up pytest-asyncio as the default
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for each test session.
    This helps with running async tests.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
