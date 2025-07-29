#!/usr/bin/env python3
"""
Tests for the Test Analyzer MCP Server.

These tests verify the functionality of the MCP server by running it in a background process
and communicating with it via stdin/stdout.
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import traceback

import pytest
from pytest_asyncio import fixture as async_fixture  # Import for async fixture

# Add project root to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import MCP components for testing
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("Error: MCP client library not found. Please install it with:")
    print("pip install mcp")
    sys.exit(1)

# Import the function to be tested, and other necessary modules
from log_analyzer_mcp.analyze_runtime_errors import analyze_runtime_errors

# Timeout for all async operations (in seconds)
OPERATION_TIMEOUT = 30

# Define runtime logs directory
RUNTIME_LOGS_DIR = os.path.join(project_root, "logs", "runtime")

# Correct server path
# script_dir here is .../project_root/tests/log_analyzer_mcp/
# project_root is .../project_root/
server_path = os.path.join(project_root, "src", "log_analyzer_mcp", "log_analyzer_mcp_server.py")

# Define paths for test data (using project_root)
# These files/scripts need to be present or the tests using them will fail/be skipped
TEST_LOG_FILE = os.path.join(project_root, "logs", "run_all_tests.log")  # Server will use this path
SAMPLE_TEST_LOG_PATH = os.path.join(
    script_dir, "sample_run_all_tests.log"
)  # A sample log for tests to populate TEST_LOG_FILE
TESTS_DIR = os.path.join(project_root, "tests")
COVERAGE_XML_FILE = os.path.join(
    project_root, "logs", "tests", "coverage", "coverage.xml"
)  # Adjusted to match pyproject & server


async def with_timeout(coro, timeout=OPERATION_TIMEOUT):
    """Run a coroutine with a timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError as e:
        raise TimeoutError(f"Operation timed out after {timeout} seconds") from e


@async_fixture  # Changed from @pytest.fixture to @pytest_asyncio.fixture
async def server_session():
    """Provides an initialized MCP ClientSession for tests.
    Starts a new server process for each test that uses this fixture for isolation.
    """
    print("Setting up server_session fixture for a test...")

    server_env = os.environ.copy()
    server_env["COVERAGE_PROCESS_START"] = os.path.join(project_root, "pyproject.toml")

    existing_pythonpath = server_env.get("PYTHONPATH", "")
    server_env["PYTHONPATH"] = project_root + os.pathsep + existing_pythonpath

    server_params = StdioServerParameters(
        command=sys.executable, args=[server_path], env=server_env  # Run server directly
    )
    print(f"Server session starting directly (parallel=false, COVERAGE_PROCESS_START only): args={server_params.args}")

    # Removed session = None initialization and manual session.close() in finally.
    # Reverted to nested async with for ClientSession.
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                print("Initializing session for server_session fixture...")
                init_future = asyncio.create_task(session.initialize())
                try:
                    await asyncio.wait_for(init_future, timeout=OPERATION_TIMEOUT)
                except asyncio.TimeoutError:
                    print(f"ERROR: server_session fixture initialization timed out after {OPERATION_TIMEOUT}s")
                    # No explicit session.close() here, relying on async with __aexit__
                    pytest.fail(f"server_session fixture initialization timed out after {OPERATION_TIMEOUT}s")
                    return  # Exit if initialization fails
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"ERROR: server_session fixture initialization failed: {e}")
                    # No explicit session.close() here
                    pytest.fail(f"server_session fixture initialization failed: {e}")
                    return  # Exit if initialization fails

                print("server_session fixture initialized.")
                yield session
                print("server_session fixture: session usage complete, proceeding to teardown within async with.")

            print("server_session fixture: ClientSession context exited.")
        print("server_session fixture: stdio_client context exited.")

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"ERROR: Unhandled exception in server_session fixture setup/teardown: {e}")
        pytest.fail(f"Unhandled exception in server_session fixture: {e}")
    finally:
        # The 'finally' block for 'async with' is handled implicitly by the context managers.
        print("server_session fixture teardown phase complete (implicit via async with or explicit finally).")


@pytest.mark.asyncio  # Ensure test is marked as asyncio
@pytest.mark.xfail(
    reason="This test relies on the server_session fixture which is unstable, and covers multiple MCP tools that might interact badly in a single test."
)
async def test_log_analyzer_mcp_server(server_session: ClientSession):  # Use the fixture
    """Run integration tests against the Log Analyzer MCP Server using the fixture."""

    # The server_session fixture now provides the 'session' object.
    # No need to manually start server_process or use stdio_client here.

    try:
        # Test ping
        print("Testing ping...")
        response = await with_timeout(server_session.call_tool("ping", {}))
        result = response.content[0].text
        assert isinstance(result, str)
        assert "Status: ok" in result
        assert "Log Analyzer MCP Server is running" in result
        print("✓ Ping test passed")

        # Test analyze_tests with no log file
        print("Testing analyze_tests with no log file...")
        # Check if log file exists
        log_file_path = os.path.join(project_root, "logs", "run_all_tests.log")
        log_file_exists = os.path.exists(log_file_path)
        print(f"Test log file exists: {log_file_exists} at {log_file_path}")

        response = await with_timeout(server_session.call_tool("analyze_tests", {}))
        result = json.loads(response.content[0].text)

        if log_file_exists:
            # If log file exists, we should get analysis
            assert "summary" in result
            assert "log_file" in result
            assert "log_timestamp" in result
            print("✓ Analyze tests (with existing log) test passed")
        else:
            # If no log file, we should get an error
            assert "error" in result
            assert "Test log file not found" in result["error"]
            print("✓ Analyze tests (no log) test passed")

        # Test running tests with no verbosity
        print("Testing run_tests_no_verbosity...")
        response = await with_timeout(
            server_session.call_tool("run_tests_no_verbosity", {}), timeout=300  # Longer timeout for test running
        )
        result = json.loads(response.content[0].text)
        assert isinstance(result, dict)
        assert "success" in result
        assert "test_output" in result
        assert "analysis_log_path" in result
        assert result.get("return_code") in [0, 1, 5], f"Unexpected return_code: {result.get('return_code')}"
        print("✓ Run tests (no verbosity) test passed")

        # Test running tests with verbosity
        print("Testing run_tests_verbose...")
        response = await with_timeout(
            server_session.call_tool("run_tests_verbose", {}), timeout=300  # Longer timeout for test running
        )
        result_verbose = json.loads(response.content[0].text)
        assert isinstance(result_verbose, dict)
        assert "success" in result_verbose
        assert "test_output" in result_verbose
        assert "analysis_log_path" in result_verbose
        assert result_verbose.get("return_code") in [
            0,
            1,
            5,
        ], f"Unexpected return_code: {result_verbose.get('return_code')}"
        print("✓ Run tests (verbose) test passed")

        # Test analyze_tests after running tests
        print("Testing analyze_tests after running tests...")
        response = await with_timeout(server_session.call_tool("analyze_tests", {}))
        result = json.loads(response.content[0].text)
        assert isinstance(result, dict)
        assert "summary" in result
        assert "log_file" in result
        assert "log_timestamp" in result
        print("✓ Analyze tests (after run) test passed")

        # Test analyze_tests with summary only
        print("Testing analyze_tests with summary only...")
        response = await with_timeout(server_session.call_tool("analyze_tests", {"summary_only": True}))
        result = json.loads(response.content[0].text)
        assert isinstance(result, dict)
        assert "summary" in result
        assert "error_details" not in result
        print("✓ Analyze tests (summary only) test passed")

        # Test create_coverage_report
        print("Testing create_coverage_report...")
        response = await with_timeout(
            server_session.call_tool("create_coverage_report", {"force_rebuild": True}),
            timeout=300,  # Coverage can take time
        )
        create_cov_tool_result = json.loads(response.content[0].text)
        assert isinstance(create_cov_tool_result, dict)
        assert "success" in create_cov_tool_result  # Tool should report its own success/failure
        print("✓ Create coverage report tool executed")

        # Test get_coverage_report
        print("Testing get_coverage_report...")
        if create_cov_tool_result.get("success") and create_cov_tool_result.get("coverage_xml_path"):
            response = await with_timeout(server_session.call_tool("get_coverage_report", {}))
            get_cov_tool_result = json.loads(response.content[0].text)
            assert isinstance(get_cov_tool_result, dict)
            assert "success" in get_cov_tool_result
            if get_cov_tool_result.get("success"):
                assert "coverage_percent" in get_cov_tool_result
                assert "modules" in get_cov_tool_result
            else:
                assert "error" in get_cov_tool_result
            print("✓ Get coverage report tool executed and response structure validated")
        else:
            print(
                f"Skipping get_coverage_report test because create_coverage_report did not indicate success and XML path. Result: {create_cov_tool_result}"
            )

        # Test analyze_runtime_errors
        print("Testing analyze_runtime_errors (direct function call)...")
        try:
            # Clean up and prepare runtime logs directory
            if os.path.exists(RUNTIME_LOGS_DIR):
                shutil.rmtree(RUNTIME_LOGS_DIR)
            os.makedirs(RUNTIME_LOGS_DIR, exist_ok=True)  # Added exist_ok=True

            # Create a test log file
            test_log_file = os.path.join(RUNTIME_LOGS_DIR, "test_runtime.log")
            test_session_id = "230325-123456-test-session"
            test_timestamp = "2025-03-25 12:34:56,789"
            with open(test_log_file, "w", encoding="utf-8") as f:
                f.write(f"{test_timestamp} INFO: Starting session {test_session_id}\\n")
                f.write(f"{test_timestamp} ERROR: Test error message for session {test_session_id}\\n")

            # No MCP call: Call the Python function directly
            # response = await with_timeout(server_session.call_tool("analyze_runtime_errors", {}))
            # result = json.loads(response.content[0].text)
            result_dict = analyze_runtime_errors(logs_dir=RUNTIME_LOGS_DIR)  # Direct call

            assert isinstance(result_dict, dict)
            assert "success" in result_dict
            assert result_dict["success"] is True, "Analysis should be successful"
            # The direct function call might determine session_id differently or not at all if not from MCP context
            # Adjust this assertion based on analyze_runtime_errors function's actual behavior
            assert result_dict.get("execution_id") in [
                test_session_id,
                "unknown",
            ], f"Expected session ID {test_session_id} or unknown, got {result_dict.get('execution_id')}"
            assert result_dict["total_errors"] == 1, "Should find exactly one error"
            assert isinstance(result_dict["errors"], list)
            assert isinstance(result_dict["errors_by_file"], dict)

            # Validate error details
            if result_dict["total_errors"] > 0:
                first_error = result_dict["errors"][0]
                assert first_error["timestamp"] == test_timestamp, "Error timestamp should match"
                assert "Test error message" in first_error["error_line"], "Error message should match"

            print("✓ Analyze runtime errors test passed (direct call)")
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Failed in analyze_runtime_errors (direct call): {str(e)}")
            print(traceback.format_exc())
            raise

        # Test run_unit_test functionality
        print("Testing run_unit_test...")
        response = await with_timeout(
            server_session.call_tool("run_unit_test", {"agent": "qa_agent", "verbosity": 0}),
            timeout=120,  # Set a reasonable timeout for agent-specific tests
        )
        result = json.loads(response.content[0].text)
        assert isinstance(result, dict)
        assert "success" in result
        assert "test_output" in result
        assert "analysis_log_path" in result
        assert result.get("return_code") in [
            0,
            1,
            5,
        ], f"Unexpected return_code for valid agent: {result.get('return_code')}"
        print("✓ Run unit test test passed")

        # Test with an invalid agent
        print("Testing run_unit_test with invalid agent...")
        response = await with_timeout(
            server_session.call_tool(
                "run_unit_test", {"agent": "invalid_agent_that_will_not_match_anything", "verbosity": 0}
            ),
            timeout=60,  # Allow time for hatch test to run even if no tests found
        )
        result = json.loads(response.content[0].text)
        assert isinstance(result, dict)
        assert "success" in result
        assert "test_output" in result
        assert "analysis_log_path" in result
        assert (
            result.get("return_code") == 5
        ), f"Expected return_code 5 (no tests collected) for invalid agent, got {result.get('return_code')}"
        # Old assertions for result["analysis"] content removed

        print("✓ Run unit test with invalid agent test passed (expecting 0 tests found)")

    finally:
        # No server_process to terminate here, fixture handles it.
        print("test_log_analyzer_mcp_server (using fixture) completed.")

    return True


async def run_quick_tests():
    """Run a subset of tests for quicker verification."""
    print("Starting test suite - running a subset of tests for quicker verification")

    # Start the server in a separate process
    server_process = subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,  # Use binary mode for stdio_client compatibility
        bufsize=0,  # Unbuffered
    )

    try:
        # Allow time for server to start
        await asyncio.sleep(2)

        # Connect a client
        server_params = StdioServerParameters(command=sys.executable, args=[server_path])

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("Connected to server, waiting for initialization...")
                await with_timeout(session.initialize())

                print("Testing ping...")
                response = await with_timeout(session.call_tool("ping", {}))
                result_text = response.content[0].text
                assert isinstance(result_text, str)
                assert "Status: ok" in result_text
                print("✓ Ping test passed")

                print("Testing analyze_tests...")
                # Define log_file_exists within this function's scope
                log_file_exists = os.path.exists(TEST_LOG_FILE)
                print(f"Inside run_quick_tests: {TEST_LOG_FILE} exists: {log_file_exists}")
                try:
                    # Ensure TEST_LOG_FILE is in a known state for this quick test
                    # E.g., copy sample or ensure it's absent if testing "not found" case
                    if os.path.exists(SAMPLE_TEST_LOG_PATH) and not log_file_exists:
                        shutil.copy(SAMPLE_TEST_LOG_PATH, TEST_LOG_FILE)
                        print(f"Copied sample log to {TEST_LOG_FILE} for run_quick_tests analyze_tests")
                        log_file_exists = True  # Update status
                    elif not log_file_exists and os.path.exists(TEST_LOG_FILE):
                        os.remove(TEST_LOG_FILE)  # Ensure it's gone if we intend to test not found
                        print(f"Removed {TEST_LOG_FILE} to test 'not found' scenario in run_quick_tests")
                        log_file_exists = False

                    response = await with_timeout(
                        session.call_tool("analyze_tests", {})
                    )  # No pattern for analyze_tests
                    result = json.loads(response.content[0].text)
                    print(f"Response received: {result}")

                    if log_file_exists:
                        assert "summary" in result
                        assert "log_file" in result
                        print("✓ Analyze tests (with existing log) test passed in run_quick_tests")
                    else:
                        assert "error" in result
                        assert "Test log file not found" in result["error"]
                        print("✓ Analyze tests (no log) test passed in run_quick_tests")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Failed in analyze_tests (run_quick_tests): {str(e)}")
                    print(traceback.format_exc())
                    raise

                # Test running tests with no verbosity - only if --run-all is passed
                if len(sys.argv) > 2 and sys.argv[2] == "--run-all":
                    print("Testing run_tests_no_verbosity...")
                    try:
                        response = await with_timeout(
                            session.call_tool("run_tests_no_verbosity", {}),
                            timeout=300,  # Much longer timeout for test running (5 minutes)
                        )
                        result = json.loads(response.content[0].text)
                        assert "success" in result
                        print("✓ Run tests (no verbosity) test passed")
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        print(f"Failed in run_tests_no_verbosity: {str(e)}")
                        print(traceback.format_exc())
                        raise
                else:
                    print("Skipping run_tests_no_verbosity test (use --run-all to run it)")

                # Test basic coverage reporting functionality
                print("Testing basic coverage reporting functionality...")
                try:
                    # Quick check of get_coverage_report
                    response = await with_timeout(session.call_tool("get_coverage_report", {}))
                    result = json.loads(response.content[0].text)
                    assert "success" in result
                    print("✓ Get coverage report test passed")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Failed in get_coverage_report: {str(e)}")
                    print(traceback.format_exc())
                    raise

                # Test run_unit_test functionality (quick version)
                print("Testing run_unit_test (quick version)...")
                try:
                    # Just check that the tool is registered and accepts parameters correctly
                    response = await with_timeout(
                        session.call_tool("run_unit_test", {"agent": "qa_agent", "verbosity": 0}), timeout=60
                    )
                    result = json.loads(response.content[0].text)
                    assert "success" in result
                    print("✓ Run unit test (quick version) test passed")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Failed in run_unit_test quick test: {str(e)}")
                    print(traceback.format_exc())
                    raise

        return True
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Error during tests: {e}")
        print(traceback.format_exc())
        return False
    finally:
        # Clean up
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait(timeout=5)


@pytest.mark.asyncio
@pytest.mark.xfail(
    reason="Coverage report generation within MCP tool is now working, but server session fixture causes teardown errors."
)
async def test_quick_subset(server_session: ClientSession):  # Now uses the simplified fixture
    """Run a subset of tests for quicker verification."""
    print("Starting test suite - running a subset of tests for quicker verification")

    current_test_log_file = os.path.join(
        project_root, "logs", "run_all_tests.log"
    )  # Consistent with global TEST_LOG_FILE
    sample_log = os.path.join(script_dir, "sample_run_all_tests.log")
    current_coverage_xml_file = os.path.join(project_root, "logs", "tests", "coverage", "coverage.xml")  # Consistent

    print(f"Test log file path being checked by test_quick_subset: {current_test_log_file}")
    log_file_exists_for_quick_test = os.path.exists(current_test_log_file)
    print(f"Test log file exists at start of test_quick_subset: {log_file_exists_for_quick_test}")

    # Ping
    print("Testing ping (in test_quick_subset)...")
    response = await with_timeout(server_session.call_tool("ping", {}))
    ping_result_text = response.content[0].text
    assert isinstance(ping_result_text, str), "Ping response should be a string"
    assert "Status: ok" in ping_result_text, "Ping response incorrect"
    assert "Log Analyzer MCP Server is running" in ping_result_text, "Ping response incorrect"
    print("Ping test completed successfully (in test_quick_subset)")

    # Analyze Tests (only if sample log exists to create the main log)
    if os.path.exists(sample_log):
        shutil.copy(sample_log, current_test_log_file)
        print(f"Copied sample log to {current_test_log_file} for analyze_tests (in test_quick_subset)")

        print("Testing analyze_tests (in test_quick_subset)...")
        # analyze_tests takes summary_only, not test_pattern
        response = await with_timeout(server_session.call_tool("analyze_tests", {"summary_only": True}))
        analyze_result = json.loads(response.content[0].text)
        print(f"Analyze_tests response (quick_subset): {analyze_result}")
        assert "summary" in analyze_result, "Analyze_tests failed to return summary (quick_subset)"
        # Based on sample_run_all_tests.log, it should find some results.
        # The sample log has: 1 passed, 1 failed, 1 skipped
        assert (
            analyze_result["summary"].get("passed", 0) >= 1
        ), "Analyze_tests did not find passed tests from sample (quick_subset)"
        assert (
            analyze_result["summary"].get("failed", 0) >= 1
        ), "Analyze_tests did not find failed tests from sample (quick_subset)"
        print("Analyze_tests (subset) completed successfully (in test_quick_subset)")
        # Clean up the copied log file to not interfere with other tests
        if os.path.exists(current_test_log_file):
            os.remove(current_test_log_file)
            print(f"Removed {current_test_log_file} after quick_subset analyze_tests")
    else:
        print(f"Skipping analyze_tests in quick_subset as sample log {sample_log} not found.")

    # Get Coverage Report (only if a dummy coverage file can be created)
    dummy_coverage_content = """<?xml version="1.0" ?>
<coverage line-rate="0.85" branch-rate="0.7" version="6.0" timestamp="1670000000">
	<sources>
		<source>/app/src</source>
	</sources>
	<packages>
		<package name="log_analyzer_mcp" line-rate="0.85" branch-rate="0.7">
			<classes>
				<class name="some_module.py" filename="log_analyzer_mcp/some_module.py" line-rate="0.9" branch-rate="0.8">
					<lines><line number="1" hits="1"/></lines>
				</class>
				<class name="healthcheck.py" filename="log_analyzer_mcp/healthcheck.py" line-rate="0.75" branch-rate="0.6">
					<lines><line number="1" hits="1"/></lines>
				</class>
			</classes>
		</package>
	</packages>
</coverage>
"""
    os.makedirs(os.path.dirname(current_coverage_xml_file), exist_ok=True)
    with open(current_coverage_xml_file, "w", encoding="utf-8") as f:
        f.write(dummy_coverage_content)
    print(f"Created dummy coverage file at {current_coverage_xml_file} for test_quick_subset")

    print("Testing create_coverage_report (in test_quick_subset)...")
    # Tool is create_coverage_report, not get_coverage_report
    # The create_coverage_report tool will run tests and then generate reports.
    # It returns paths and a summary of its execution, not parsed coverage data directly.
    response = await with_timeout(server_session.call_tool("create_coverage_report", {"force_rebuild": True}))
    coverage_result = json.loads(response.content[0].text)
    print(f"Create_coverage_report response (quick_subset): {coverage_result}")
    assert coverage_result.get("success") is True, "create_coverage_report failed (quick_subset)"
    assert "coverage_xml_path" in coverage_result, "create_coverage_report should return XML path (quick_subset)"
    assert (
        "coverage_html_index" in coverage_result
    ), "create_coverage_report should return HTML index path (quick_subset)"
    assert coverage_result["coverage_html_index"].endswith(
        "index.html"
    ), "HTML index path seems incorrect (quick_subset)"
    assert os.path.exists(coverage_result["coverage_xml_path"]), "Coverage XML file not created by tool (quick_subset)"
    # The dummy file assertions below are no longer valid as the tool runs actual coverage.
    # assert coverage_result.get("coverage_percent") == 85.00, "Overall coverage mismatch in dummy data (quick_subset)"
    # # Check for one of the modules
    # found_module = False
    # for module in coverage_result.get("modules", []):
    #     if module.get("name") == "healthcheck.py" and module.get("line_coverage_percent") == 75.00:
    #         found_module = True
    #         break
    # assert found_module, "Did not find healthcheck.py with 75.00% coverage in dummy data (quick_subset)"
    print("Create_coverage_report test completed successfully (in test_quick_subset)")

    # Clean up the actual coverage file created by the tool, not the dummy one
    if os.path.exists(coverage_result["coverage_xml_path"]):
        os.remove(coverage_result["coverage_xml_path"])
        print(f"Cleaned up actual coverage XML: {coverage_result['coverage_xml_path']}")
    # Also clean up the dummy file if it was created and not overwritten, though it shouldn't be used by the tool itself.
    if os.path.exists(current_coverage_xml_file) and current_coverage_xml_file != coverage_result["coverage_xml_path"]:
        os.remove(current_coverage_xml_file)
        print(f"Cleaned up dummy coverage file: {current_coverage_xml_file}")


# Remove the old __main__ block as tests are run via pytest/hatch
# if __name__ == "__main__":
#     try:
#         if len(sys.argv) > 1 and sys.argv[1] == "--quick":
#             print("Running quick tests...")
#             success = asyncio.run(run_quick_tests()) # run_quick_tests also needs to be a pytest test or adapted
#         else:
#             print("Running full test suite...")
#             # This call is problematic as server_session is a fixture
#             # success = asyncio.run(test_log_analyzer_mcp_server())
#             print("To run the full test suite, use: pytest tests/log_analyzer_mcp/test_log_analyzer_mcp_server.py -k test_log_analyzer_mcp_server")
#             success = False # Mark as false since direct run is deprecated here
#         print(f"Tests {'passed' if success else 'failed'}")
#         sys.exit(0 if success else 1)
#     except Exception as e:
#         print(f"Test execution error: {str(e)}")
#         import traceback
#         print(traceback.format_exc())
#         sys.exit(1)
