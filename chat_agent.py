# chat_agent.py
from uagents import Agent, Context, Protocol, Model
from contracts import RiskProfileRequest, RiskProfileResponse, PortfolioRequest, PortfolioResponse
from datetime import datetime, UTC
from pydantic import Field

# Agent addresses - update these after starting the other agents
RISK_ADDR = "agent1..."  # Update with actual risk agent address
PORTFOLIO_ADDR = "agent1..."  # Update with actual portfolio agent address

# ALWAYS use descriptive names and unique seeds
agent = Agent(
    name="chat_agent",
    seed="chat_agent_unique_seed_phrase_2024",
    port=8003,
    mailbox=True  # Remove endpoint when using mailbox
)

# Simple message models for basic communication
class UserMessage(Model):
    content: str
    user_id: str

class ChatResponse(Model):
    response: str
    agent_name: str

# Create simple protocol for basic communication
chat_proto = Protocol(name="basic_chat_protocol", version="1.0")

# Add event handlers
@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🚀 Chat agent started successfully!")
    ctx.logger.info(f"📍 Agent address: {agent.address}")
    ctx.logger.info(f"🌐 Listening on port 8000")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("🛑 Chat agent shutting down...")

@chat_proto.on_message(model=UserMessage, replies=ChatResponse)
async def handle_user_message(ctx: Context, sender: str, msg: UserMessage):
    ctx.logger.info(f"📨 Received message from {sender}: {msg.content}")

    user_text = msg.content.lower()

    # Simple intent handling
    if "profile" in user_text:
        # Mock transaction data for demo
        sample_transactions = [
            {"amount": 1000, "category": "salary", "date": "2024-01-01"},
            {"amount": -50, "category": "groceries", "date": "2024-01-02"},
            {"amount": -200, "category": "entertainment", "date": "2024-01-03"}
        ]

        response_text = "I would analyze your risk profile based on your transactions. For demo purposes, your risk profile would be: Conservative (score: 0.3)"

    elif "portfolio" in user_text:
        response_text = "Please request your risk profile first by sending a message with 'profile'"

    else:
        response_text = """Hello! I can help you with:
• Send a message with 'profile' to get your risk profile
• Send a message with 'portfolio' to get investment recommendations"""

    await ctx.send(sender, ChatResponse(
        response=response_text,
        agent_name="chat_agent"
    ))

# Include protocol and run
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    print("""
🤖 Starting Chat Agent...

This agent will:
1. Listen for chat messages
2. Respond to 'profile' and 'portfolio' commands
3. Provide investment advice through other agents

💬 Send messages via the chat protocol
🛑 Stop with Ctrl+C
    """)
    agent.run()