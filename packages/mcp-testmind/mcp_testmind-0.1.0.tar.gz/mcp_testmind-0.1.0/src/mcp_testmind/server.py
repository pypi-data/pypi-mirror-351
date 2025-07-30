import requests
import os
import json
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from html2text import html2text

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS


mcp = FastMCP("test_mind")

def get_auth():
    username = os.getenv("TESTRAIL_USERNAME")
    api_key = os.getenv("TESTRAIL_API_KEY")
    if not username or not api_key:
        raise ValueError("TestRail credentials not set in environment variables.")
    return (username, api_key)

def make_api_call(endpoint: str) -> str:
    try:
        url = f"https://cktax.testrail.io/index.php?/api/v2/{endpoint}"
        response = requests.get(url, auth=get_auth(), timeout=10)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Failed to connect to TestRail API: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

@mcp.tool()
def welcome_testrail() -> str:
    """
    Welcome to TestMind! Pick a test suite to start with,
    or explore the entire suite!
    """
    return make_api_call("get_projects")

@mcp.tool()
def get_test_suites(project_id: int) -> str:
    """
    Get all test suites for a given project ID.
    """
    return make_api_call(f"get_suites/{project_id}")

@mcp.tool()
def get_test_sections(project_id: int, suite_id: int) -> str:
    """
    Get all sections for a given project and suite ID.
    """
    return make_api_call(f"get_sections/{project_id}&suite_id={suite_id}")

@mcp.tool()
def get_test_cases(project_id: int, suite_id: int) -> str:
    """
    Get all test cases for a given project and suite ID.
    """
    return make_api_call(f"get_cases/{project_id}&suite_id={suite_id}")

@mcp.tool()
def get_test_runs(project_id: int) -> str:
    """
    Get all test runs for a given project ID.
    """
    return make_api_call(f"get_runs/{project_id}")

@mcp.tool()
def get_tests(run_id: int) -> str:
    """
    Get all tests for a given run ID.
    """
    return make_api_call(f"get_tests/{run_id}")
    
