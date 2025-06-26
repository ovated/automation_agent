from typing import List
import json
import aiohttp
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.tools import tool

from pydantic_schema import (
    ClickInput,
    NavigateInput,
    FuzzySearchInput,
    GetAllElementsInput,
    DownloadFileInput,
    NoInput,
)

from util.utils import TokenUtils
from util.logging_util import get_logger

logger = get_logger(__name__)


class AiTools:
    """All tools available to the Agent for browser automation."""

    def __init__(self, async_browser=None):
        """
        async_browser: An async Playwright browser instance.
        """
        if async_browser is None:
            raise ValueError("async_browser must be provided for Playwright tools.")

        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)

        # Get relevant playwright tools
        playwright_click_tool = next((t for t in toolkit.get_tools() if t.name == "click_element"), None)
        playwright_navigate_tool = next((t for t in toolkit.get_tools() if t.name == "navigate_browser"), None)
        playwright_back_tool = next((t for t in toolkit.get_tools() if t.name == "previous_webpage"), None)

        @tool(args_schema=ClickInput)
        async def click_element_tool(selector: str) -> str:
            """Click an element by its CSS selector."""
            logger.info(f"click_element_tool called with {selector}")
            try:
                return await playwright_click_tool._arun(selector)
            except Exception as e:
                logger.error(f"Error in click_element_tool for selector [{selector}]: {e}")
                return f"Error clicking element {selector} error: {str(e)}"

        @tool(args_schema=NavigateInput)
        async def navigate_tool(url: str) -> str:
            """Navigate into the given URL."""
            logger.info(f"navigate_tool called with {url}")
            url = url.strip().strip('"').strip()
            try:
                return await playwright_navigate_tool._arun(url)
            except Exception as e:
                logger.error(f"Error in navigate_tool for url [{url}]: {e}")
                return f"Error navigating to [{url}], error: {e}"

        @tool(args_schema=NoInput)
        async def navigate_back_tool() -> str:
            """Navigate back to the previous page."""
            logger.info("navigate_back_tool called.")
            try:
                return await playwright_back_tool._arun({})
            except Exception:
                logger.error("Error in navigate_back_tool.")
                return "Error navigating back"

        @tool(args_schema=FuzzySearchInput)
        async def fuzzy_fetch_html_tool(data: str) -> str:
            """Get elements with similarity text ratio >= 0.8, otherwise top 50 elements by ratio."""
            logger.info(f"fuzzy_fetch_html_tool called with {data}")
            payload = json.loads(data)
            url = payload["url"]
            search_text = payload["search_text"]
            threshold = 0.8

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    try:
                        if response.status != 200:
                            return f"Request failed with status code {response.status}"

                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        matched_elements = []
                        all_elements = []
                        search_lower = search_text.lower()

                        for elem in soup.find_all(True):  # All tags
                            text = elem.get_text(strip=True)
                            if text:
                                attrs_string = " ".join([f'{k}="{v}"' for k, v in elem.attrs.items()])
                                element_string = (
                                    f"<{elem.name} {attrs_string}>{text}</{elem.name}>"
                                    if len(text) < 100
                                    else f"<{elem.name} {attrs_string}>"
                                )
                                ratio = SequenceMatcher(None, text.lower(), search_lower).ratio()
                                all_elements.append((element_string, ratio))
                                if ratio >= threshold:
                                    matched_elements.append(element_string)

                        if matched_elements:
                            return '\n'.join(matched_elements)
                        else:
                            sorted_elements = sorted(all_elements, key=lambda x: x[1], reverse=True)[:50]
                            return '\n'.join([element for element, _ in sorted_elements]) if sorted_elements else "No elements found."

                    except Exception as e:
                        logger.error(f"Error fetching element with fuzzy_fetch_html_tool, Error: {e}")
                        return "Error fetching element with fuzzy_fetch_html_tool"

        @tool(args_schema=GetAllElementsInput)
        async def fetch_all_elements_tool(data: str) -> str:
            """Get all HTML elements for the given URL (async)."""
            logger.info(f"fetch_all_elements_tool called with {data}")
            payload = json.loads(data)
            url = payload["url"]

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    try:
                        if response.status != 200:
                            return f"Request failed with status code {response.status}"

                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        results = []
                        for elem in soup.find_all(True):  # All tags
                            text = elem.get_text(strip=True)
                            attrs_string = " ".join([f'{k}="{v}"' for k, v in elem.attrs.items()])
                            if text and len(text) < 100:
                                results.append(f"<{elem.name} {attrs_string}>{text}</{elem.name}>")
                            else:
                                results.append(f"<{elem.name} {attrs_string}>")
                        final_result = '\n'.join(results) if results else "No elements found."

                        return TokenUtils.truncate_to_10000_tokens(final_result)
                    except Exception as e:
                        logger.error(f"Error fetching elements in fetch_all_elements_tool, Error:{e}")
                        return "Error fetching elements with fetch_all_elements_tool"

        @tool(args_schema=DownloadFileInput)
        async def download_file_tool(data: str) -> str:
            """Async download a file from a given URL and save it to a local path."""
            logger.info(f"download_file_tool called with {data}")
            payload = json.loads(data)
            url = payload["url"]
            save_as = payload.get("save_as", "downloaded_file.pdf")

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            return f"Failed with status code {response.status}"
                        with open(save_as, "wb") as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                return f"File saved as {save_as}"
            except Exception as e:
                logger.error(f"In download_file_tool, an error occured. Error:{e}")
                return f"Error downloading file: {e}"

        # Define playwright tools
        self.playwright_tools = [
            click_element_tool,
            navigate_tool,
            navigate_back_tool
        ]

        # Define custom tools
        self.fuzzy_fetch_html_tool = fuzzy_fetch_html_tool
        self.fetch_all_elements_tool = fetch_all_elements_tool
        self.download_file_tool = download_file_tool

    def ai_tools(self, return_tool: bool = False) -> List:
        """Return the available tools.

        Args:
            return_tool (bool): If True, return instances of tools for the agent.
                                If False, return OpenAI-style tool definitions.
        """
        # Get playwright tools
        tools = [t for t in self.playwright_tools]

        # Append custom tools
        tools.append(self.fuzzy_fetch_html_tool)
        tools.append(self.fetch_all_elements_tool)
        tools.append(self.download_file_tool)

        return tools if return_tool else [convert_to_openai_function(t) for t in tools]
