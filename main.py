from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# import uvicorn
import asyncio
from prompts import AgentSystemPrompt
from agent import Agent
from util.logging_util import get_logger
from user_input import USER_INPUT

# Init logger
logger = get_logger(__name__)

# Initialize app
app = FastAPI()

# Pydantic model for user input
class UserInput(BaseModel):
    instruction: str

@app.post("/run-agent/")
async def run_agent(data: UserInput):
    """Run the Agent with user input."""
    logger.info("Application Started via API Request")
    prompt_template = AgentSystemPrompt.get_system_prompt()
    agent = Agent(system=prompt_template)

    try:
        result = await agent.run(data.instruction)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Unable to complete request, reason: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
# To test
async def main():
    logger.info("Application Started")

    # Get prompt template
    prompt_template = AgentSystemPrompt.get_system_prompt()

    # Send prompt to Agent
    agent = Agent(system=prompt_template)

    # Get example user prompt from user_input.py
    user_instructions = USER_INPUT

    try:
        await agent.run(user_instructions)
    except Exception as e:
        logger.error(f"Unable to complete request, reason: {e}")

if __name__ == "__main__":
    # # Launch the app
    # uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

    asyncio.run(main())