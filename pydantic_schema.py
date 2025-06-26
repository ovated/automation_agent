from pydantic import BaseModel, Field


class ClickInput(BaseModel):
    """Input schema for clicking an element."""
    selector: str = Field(..., description="CSS selector of the element to click.")

class NavigateInput(BaseModel):
    """Input schema for navigation."""
    url: str = Field(..., description="The URL to navigate to.")

class GetAllElementsInput(BaseModel):
    """Input schema for extracting all HTML elements."""
    data: str = Field(..., description='A JSON-encoded object containing "url".')

class FuzzySearchInput(BaseModel):
    """Input schema for extracting HTML elements based on a search text."""
    data: str = Field(..., description='A JSON-encoded object with "url" and "search_text".')

class DownloadFileInput(BaseModel):
    """Input schema for downloading a file."""
    data: str = Field(..., description='A JSON-encoded object containing "url" and "save_as".')

class NoInput(BaseModel):
    """Input schema for tools that take no input."""