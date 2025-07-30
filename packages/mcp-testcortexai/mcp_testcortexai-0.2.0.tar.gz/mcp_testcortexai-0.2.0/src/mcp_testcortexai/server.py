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

def get_base_url():
    base_url = os.getenv("TESTRAIL_BASE_URL")
    if not base_url:
        raise ValueError("TestRail base URL not set in environment variables.")
    return base_url.rstrip('/')  # Remove trailing slash if present

def make_api_call(endpoint: str) -> str:
    try:
        base_url = get_base_url()
        url = f"{base_url}/index.php?/api/v2/{endpoint}"
        response = requests.get(url, auth=get_auth(), timeout=10)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Failed to connect to TestRail API: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

@mcp.tool()
def welcome_testcortexai() -> str:
    return "Welcome to TestCortex AI"

@mcp.tool()
def get_test_projects() -> str:
    """
    Get all the test projects in the testrail
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
    
