import asyncio
import unittest.mock as mock

import pytest

from stagehand.client import Stagehand
from stagehand.page import StagehandPage
from stagehand.schemas import ActOptions, ObserveOptions


class TestClientLockScenarios:
    """Tests for specific lock scenarios in the Stagehand client."""

    @pytest.fixture
    async def mock_stagehand_with_page(self):
        """Create a Stagehand with mocked page for testing."""
        stagehand = Stagehand(
            server_url="http://localhost:8000",
            session_id="test-scenario-session",
            browserbase_api_key="test-api-key",
            browserbase_project_id="test-project-id",
        )

        # Create a mock for the _execute method
        stagehand._execute = mock.AsyncMock(side_effect=self._delayed_mock_execute)

        # Create a mock page
        mock_playwright_page = mock.MagicMock()
        stagehand.page = StagehandPage(mock_playwright_page, stagehand)

        yield stagehand

        # Cleanup
        Stagehand._session_locks.pop("test-scenario-session", None)

    async def _delayed_mock_execute(self, method, payload):
        """Mock _execute with a delay to simulate network request."""
        await asyncio.sleep(0.05)

        if method == "observe":
            return [{"selector": "#test", "description": "Test element"}]
        elif method == "act":
            return {
                "success": True,
                "message": "Action executed",
                "action": payload.get("action", ""),
            }
        elif method == "extract":
            return {"extraction": "Test extraction"}
        elif method == "navigate":
            return {"success": True}
        else:
            return {"result": "success"}

    @pytest.mark.asyncio
    async def test_interleaved_observe_act(self, mock_stagehand_with_page):
        """Test interleaved observe and act calls are properly serialized."""
        results = []

        async def observe_task():
            result = await mock_stagehand_with_page.page.observe(
                ObserveOptions(instruction="Find a button")
            )
            results.append(("observe", result))
            return result

        async def act_task():
            result = await mock_stagehand_with_page.page.act(
                ActOptions(action="Click the button")
            )
            results.append(("act", result))
            return result

        # Start both tasks concurrently
        observe_future = asyncio.create_task(observe_task())
        # Small delay to ensure observe starts first
        await asyncio.sleep(0.01)
        act_future = asyncio.create_task(act_task())

        # Wait for both to complete
        await asyncio.gather(observe_future, act_future)

        # Verify the calls to _execute were sequential
        calls = mock_stagehand_with_page._execute.call_args_list
        assert len(calls) == 2, "Expected exactly 2 calls to _execute"

        # Check the order of results
        assert len(results) == 2, "Expected 2 results"
        assert results[0][0] == "observe", "Observe should complete first"
        assert results[1][0] == "act", "Act should complete second"

    @pytest.mark.asyncio
    async def test_cascade_operations(self, mock_stagehand_with_page):
        """Test cascading operations (one operation triggers another)."""
        lock_acquire_times = []
        original_lock = mock_stagehand_with_page._get_lock_for_session()

        # Store original methods
        original_acquire = original_lock.acquire
        original_release = original_lock.release

        # Mock the lock to track acquire times
        async def tracked_acquire(*args, **kwargs):
            lock_acquire_times.append(("acquire", len(lock_acquire_times)))
            # Use the original acquire
            return await original_acquire(*args, **kwargs)

        def tracked_release(*args, **kwargs):
            lock_acquire_times.append(("release", len(lock_acquire_times)))
            # Use the original release
            return original_release(*args, **kwargs)

        # Replace methods with tracked versions
        original_lock.acquire = tracked_acquire
        original_lock.release = tracked_release

        # Create a mock for observe and act that simulate actual results
        # instead of using the real methods which would call into page
        observe_result = [{"selector": "#test", "description": "Test element"}]
        act_result = {"success": True, "message": "Action executed", "action": "Click"}

        # Create a custom implementation that uses our lock but returns mock results
        async def mock_observe(*args, **kwargs):
            lock = mock_stagehand_with_page._get_lock_for_session()
            async with lock:
                return observe_result

        async def mock_act(*args, **kwargs):
            lock = mock_stagehand_with_page._get_lock_for_session()
            async with lock:
                return act_result

        # Replace the methods
        mock_stagehand_with_page.page.observe = mock_observe
        mock_stagehand_with_page.page.act = mock_act

        # Return our instrumented lock
        mock_stagehand_with_page._get_lock_for_session = mock.MagicMock(
            return_value=original_lock
        )

        async def cascading_operation():
            # First operation
            result1 = await mock_stagehand_with_page.page.observe("Find a button")

            # Second operation depends on first
            if result1:
                result2 = await mock_stagehand_with_page.page.act(
                    f"Click {result1[0]['selector']}"
                )
                return result2

        # Run the cascading operation
        await cascading_operation()

        # Verify lock was acquired and released correctly
        assert (
            len(lock_acquire_times) == 4
        ), "Expected 4 lock events (2 acquires, 2 releases)"

        # The sequence should be: acquire, release, acquire, release
        expected_sequence = ["acquire", "release", "acquire", "release"]
        actual_sequence = [event[0] for event in lock_acquire_times]
        assert (
            actual_sequence == expected_sequence
        ), f"Expected {expected_sequence}, got {actual_sequence}"

    @pytest.mark.asyncio
    async def test_multi_session_parallel(self):
        """Test that operations on different sessions can happen in parallel."""
        # Create two Stagehand instances with different session IDs
        stagehand1 = Stagehand(
            server_url="http://localhost:8000",
            session_id="test-parallel-session-1",
            browserbase_api_key="test-api-key",
            browserbase_project_id="test-project-id",
        )

        stagehand2 = Stagehand(
            server_url="http://localhost:8000",
            session_id="test-parallel-session-2",
            browserbase_api_key="test-api-key",
            browserbase_project_id="test-project-id",
        )

        # Track execution timestamps
        timestamps = []

        # Mock _execute for both instances
        async def mock_execute_1(method, payload):
            timestamps.append(("session1-start", asyncio.get_event_loop().time()))
            await asyncio.sleep(0.1)  # Simulate work
            timestamps.append(("session1-end", asyncio.get_event_loop().time()))
            return {"result": "success"}

        async def mock_execute_2(method, payload):
            timestamps.append(("session2-start", asyncio.get_event_loop().time()))
            await asyncio.sleep(0.1)  # Simulate work
            timestamps.append(("session2-end", asyncio.get_event_loop().time()))
            return {"result": "success"}

        stagehand1._execute = mock_execute_1
        stagehand2._execute = mock_execute_2

        async def task1():
            lock = stagehand1._get_lock_for_session()
            async with lock:
                return await stagehand1._execute("test", {})

        async def task2():
            lock = stagehand2._get_lock_for_session()
            async with lock:
                return await stagehand2._execute("test", {})

        # Run both tasks concurrently
        await asyncio.gather(task1(), task2())

        # Verify the operations overlapped in time
        session1_start = next(t[1] for t in timestamps if t[0] == "session1-start")
        session1_end = next(t[1] for t in timestamps if t[0] == "session1-end")
        session2_start = next(t[1] for t in timestamps if t[0] == "session2-start")
        session2_end = next(t[1] for t in timestamps if t[0] == "session2-end")

        # Check for parallel execution (operations should overlap in time)
        time_overlap = min(session1_end, session2_end) - max(
            session1_start, session2_start
        )
        assert (
            time_overlap > 0
        ), "Operations on different sessions should run in parallel"

        # Clean up
        Stagehand._session_locks.pop("test-parallel-session-1", None)
        Stagehand._session_locks.pop("test-parallel-session-2", None)
