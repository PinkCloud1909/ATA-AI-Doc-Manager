from google.adk.agents.llm_agent import Agent

# Simple Hello World Agent
root_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="dms_assistant",
    description="A helpful assistant for the document management system.",
    instruction="You are a helpful, friendly AI assistant. Answer user queries concisely and politely."
)
