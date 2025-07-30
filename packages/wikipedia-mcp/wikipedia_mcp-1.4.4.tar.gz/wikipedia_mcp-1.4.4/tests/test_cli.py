"""
Tests for the command-line interface of Wikipedia MCP server.
"""
import subprocess
import sys
import pytest

# Path to the wikipedia-mcp executable
WIKIPEDIA_MCP_CMD = ["wikipedia-mcp"]

def run_mcp_command(args, expect_timeout=False):
    """Helper function to run the wikipedia-mcp command and return its output."""
    try:
        process = subprocess.run(
            WIKIPEDIA_MCP_CMD + args,
            capture_output=True,
            text=True,
            check=False,
            timeout=3  # Shorter timeout for faster tests
        )
        return process
    except FileNotFoundError:
        try:
            process = subprocess.run(
                [sys.executable, "-m", "wikipedia_mcp"] + args,
                capture_output=True,
                text=True,
                check=False,
                timeout=3
            )
            return process
        except subprocess.TimeoutExpired as e:
            if expect_timeout:
                return e
            else:
                raise
    except subprocess.TimeoutExpired as e:
        if expect_timeout:
            return e
        else:
            raise


def test_cli_stdio_transport_starts():
    """Test that stdio transport starts without immediate errors."""
    args = ["--transport", "stdio", "--log-level", "INFO"]
    result = run_mcp_command(args, expect_timeout=True)

    # For stdio mode, we expect the process to start and then timeout waiting for input
    # This indicates the server started successfully
    assert isinstance(result, subprocess.TimeoutExpired), "Expected timeout for stdio mode"
    
    # Check that some logging output was captured (from any source)
    stderr_bytes = result.stderr if hasattr(result, 'stderr') else b''
    stderr_output = stderr_bytes.decode('utf-8', errors='replace') if isinstance(stderr_bytes, bytes) else stderr_bytes
    
    # At minimum, we should see some log output indicating the process started
    assert len(stderr_output.strip()) > 0, "Expected some log output on stderr"
    
    # Verify stdout is empty (no prints interfering with stdio protocol)
    stdout_bytes = result.stdout if hasattr(result, 'stdout') else b''
    if stdout_bytes is None:
        stdout_bytes = b''
    stdout_output = stdout_bytes.decode('utf-8', errors='replace') if isinstance(stdout_bytes, bytes) else str(stdout_bytes)
    assert stdout_output.strip() == "", "stdout should be empty for stdio transport"


def test_cli_sse_transport_starts():
    """Test that sse transport starts without immediate errors."""
    args = ["--transport", "sse", "--log-level", "INFO"]
    result = run_mcp_command(args, expect_timeout=True)

    # For sse mode, we expect the process to start the HTTP server and then timeout
    assert isinstance(result, subprocess.TimeoutExpired), "Expected timeout for sse mode"
    
    # Check that logging output was captured
    stderr_bytes = result.stderr if hasattr(result, 'stderr') else b''
    stderr_output = stderr_bytes.decode('utf-8', errors='replace') if isinstance(stderr_bytes, bytes) else stderr_bytes
    
    # Should see uvicorn startup messages for sse mode
    assert "uvicorn" in stderr_output.lower() or "application startup" in stderr_output.lower(), \
        "Expected uvicorn startup messages for sse transport"


def test_cli_invalid_transport():
    """Test CLI behavior with an invalid transport option."""
    args = ["--transport", "invalid_transport_option"]
    result = run_mcp_command(args)
    assert result.returncode != 0, "Should exit with non-zero code for invalid transport"
    assert "invalid choice: 'invalid_transport_option'" in result.stderr, "Should show argparse error"


def test_cli_help_message():
    """Test that the help message can be displayed."""
    args = ["--help"]
    result = run_mcp_command(args)
    assert result.returncode == 0, "Help should exit with code 0"
    assert "usage:" in result.stdout.lower(), "Should show usage information"
    assert "--transport" in result.stdout, "Should show transport option"
    assert "--log-level" in result.stdout, "Should show log-level option"


def test_cli_log_levels():
    """Test different log levels work without errors."""
    for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        args = ["--transport", "stdio", "--log-level", level]
        result = run_mcp_command(args, expect_timeout=True)
        
        # Should timeout (indicating successful start) rather than exit with error
        assert isinstance(result, subprocess.TimeoutExpired), f"Expected timeout for log level {level}" 