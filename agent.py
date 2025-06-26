from typing import Dict
from llm.model import ChatModel
from tools import AiTools
from openai import RateLimitError
from langchain.agents import create_react_agent, AgentExecutor
from playwright.async_api import async_playwright
from langchain.memory import ConversationBufferMemory
from util.logging_util import get_logger

logger = get_logger(__name__)


class Agent:
    """An AI Agent for planning and executing automation steps."""

    def __init__(self, system: str = ""):
        logger.info("Initializing Agent Class")
        self.system = system
        self.model = ChatModel.chat_model
        self.agent = None
        self.tools_for_agent = []
        print(f"system: {system}")

    async def setup(self):
        """Set up the async browser and tools, and build the Agent."""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        tools_class = AiTools(async_browser=browser)
        self.tools_for_agent = tools_class.ai_tools(return_tool=True)

        # Create a short‐term buffer memory
        memory = ConversationBufferMemory(
            k=1,
            memory_key="agent_scratchpad",
            return_messages=True
        )

        agent = create_react_agent(
            llm=self.model,
            tools=self.tools_for_agent,
            prompt=self.system)

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools_for_agent,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=200,
            # max_execution_time=30,
            return_intermediate_steps=False,)

        self.agent = agent_executor

    async def run(self, user_message: str) -> Dict:
        """Run the Agent after setup."""
        if self.agent is None:
            await self.setup()

        logger.info(f"User_message: {user_message}")

        try:
            result = await self.agent.ainvoke({"input": user_message})
        except RateLimitError:
            logger.warning("Rate limit exceeded.")
            return {"error": "Rate limit exceeded. Try again later."}
        except Exception as e:
            logger.error(f"Unable to complete request, reason: {e}")
            return {"error": str(e)}

        return result
