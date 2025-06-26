# AI AUTOMATION AGENT

## How it Works
This AI browser automation agent is built using LangChain’s create_react_agent and AgentExecutor functions. It operates by utilizing internal and custom tools to perform web page interactions based on user instructions.

### Tools used:
I used three built-in Playwright tools:
- click_element (Clicks an element)
- navigate_browser (Navigates to a given URL)
- previous_webpage (Goes back to the previous page)

I also created three custom tools:
- Fuzzy Fetch HTML (Finds HTML elements with text matching a given phrase)
- Get All Elements (Extracts all HTML elements on a page)
- Downloads Tool (Downloads files from a page)

### Libraries used:
- Beautiful Soup
- Playwright
- LangChain
- FastAPI
- SequenceMatcher

## Steps automated
- The agent uses these tools to gather data required for making decisions.

## Improvement / Future work
Three major improvements can be made:

1. Invest in language models that support higher Tokens Per Minute (TPM).
2. Create more niche and dynamic tools.
3. I currently limit the token size of get_all_element tool to 10,000 but if I build a custom agent from scratch, I will have greater control over token truncation and manage inputs within a set token budget.

## Time spent
I spent approximately 2 days building this agent.

## Set up App

**Before you begin**  
Ensure the following files are present in the project root:  
- `.env` (your environment variables)  
- `requirements.txt` (your Python dependencies)

## Create a virtual environment
```bash
python -m venv .venv
```

## Install requirement files
Ensure you are in the virtual environment you created.
```bash
pip install -r requirements.txt
```

## Install playwright
Ensure you are in the virtual environment you created.
```bash
playwright install
```

## Access the application
Once you've followed the above steps, you can run the main file.
```bash
python main.py
```