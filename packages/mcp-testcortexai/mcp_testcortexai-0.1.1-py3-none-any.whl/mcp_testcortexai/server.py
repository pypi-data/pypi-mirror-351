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
    return
    """
        "🧠 **Welcome to TestCortex AI**\n\n"
        "I’m your intelligent assistant for orchestrating end-to-end quality engineering — powered by the Goose AI platform.\n"
        "With seamless integrations across **TestRail**, **Jira**, and **Tax Butler**, I help you:\n\n"
        "- 🔍 Gain deep visibility into test coverage, runs, and results\n"
        "- 📂 Navigate projects, suites, sections, and test cases effortlessly\n"
        "- 🐞 Track and manage Jira defects with full context and traceability\n"
        "- 🤖 Automate insights, transitions, and cross-system validations\n"
        "- ⚙️ Execute test scenarios directly via **Tax Butler** to validate logic and calculations\n\n"
        "### 🚀 Quick Start Commands:\n"
        "`cortex-ai > testrail_projects()` – View all TestRail projects\n"
        "`cortex-ai > jira_issue('PROJ-456')` – Get detailed Jira issue information\n"
        "`cortex-ai > testrail_create_case(...)` – Add a new test case\n"
        "`cortex-ai > jira_create_issue(...)` – File a new bug or task\n"
        "`cortex-ai > run_test_with_butler(...)` – Execute test scenarios in Tax Butler\n\n"
        "Let **TestCortex AI** be the brain of your test stack — built on Goose, designed for scale. 🧠⚙️"

    """

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
    
