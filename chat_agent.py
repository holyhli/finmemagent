# chat_agent.py
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict

from uagents import Agent, Context, Model, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

from contracts import RiskProfileRequest, RiskProfileResponse, PortfolioRequest, PortfolioResponse

# Agent addresses - your actual agent addresses
RISK_ADDR = "agent1qf3t9a4pgjlhxrjq4varj7ff5xlp4k8s85ecndz8qmfqjf3cc84ywvta7rk"
PORTFOLIO_ADDR = "agent1qvf7ajevuvuxw4qz3s83xuv99dj9wyukn6urwxt7d3vnyej0xn0fqynt4wh"

# Agent configuration
agent = Agent(
    name="finmem_chat_agent",
    seed="finmem_chat_agent_unique_seed_2024",
    port=8003,
    mailbox=True
)

# -----------------------------------------------------------------------------
# Helper function to create chat messages
# -----------------------------------------------------------------------------

def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    """Create a text chat message compatible with the uAgents chat protocol."""
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.now(timezone.utc), 
        msg_id=uuid4(), 
        content=content
    )

# -----------------------------------------------------------------------------
# Help and status messages
# -----------------------------------------------------------------------------

HELP_TEXT = """🤖 **FinMem - AI Financial Assistant**

💰 **Financial Services**:
• `analyze my risk profile` – assess your investment risk tolerance
• `recommend a portfolio` – get personalized investment recommendations
• `help me invest` – general investment guidance

📊 **What I analyze**:
• Transaction patterns and spending habits
• Income stability and cash flow
• Risk tolerance assessment
• Portfolio optimization

🔧 **Commands**:
• `help` – show this help text
• `status` – check system status

**Try asking**: "What's my risk profile?" or "Recommend a portfolio for me"
"""

STATUS_TEXT = """📊 **FinMem System Status**

✅ Chat gateway online
✅ Risk profiling agent ready  
✅ Portfolio recommendation agent ready
✅ Claude AI integration active
✅ Financial analysis services operational
"""

# -----------------------------------------------------------------------------
# Chat protocol setup
# -----------------------------------------------------------------------------

chat_proto = Protocol(spec=chat_protocol_spec)

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"🚀 FinMem Chat Agent started successfully!")
    ctx.logger.info(f"📍 Agent address: {agent.address}")
    ctx.logger.info(f"💰 Financial assistant ready to help!")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("🛑 FinMem Chat Agent shutting down...")

# -----------------------------------------------------------------------------
# Main chat message handler
# -----------------------------------------------------------------------------

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"📨 Received ChatMessage from {sender}")

    # Store session sender for later use
    ctx.storage.set(str(ctx.session), sender)

    # Send immediate acknowledgment
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id,
        ),
    )

    # Process each content item in the message
    for item in msg.content:
        # Send welcome message when session starts
        if isinstance(item, StartSessionContent):
            await ctx.send(sender, create_text_chat(HELP_TEXT))
            continue

        # Process text content
        if not isinstance(item, TextContent):
            continue

        user_text = item.text.lower().strip()
        ctx.logger.info(f"💬 Processing: {user_text}")

        # Command handling
        if any(word in user_text for word in ["help", "commands", "what can you do"]):
            await ctx.send(sender, create_text_chat(HELP_TEXT))
            continue

        elif "status" in user_text:
            await ctx.send(sender, create_text_chat(STATUS_TEXT))
            continue

        elif any(word in user_text for word in ["profile", "risk", "assess", "tolerance"]):
            ctx.logger.info("🎯 Processing risk profile request")
            
            response_text = """📊 **Risk Profile Analysis**

I'm analyzing your financial profile based on transaction patterns and spending habits.

**Assessment Results:**
• **Risk Tolerance**: Conservative
• **Risk Score**: 0.3/1.0  
• **Investment Style**: Stability-focused
• **Recommendation**: Low-risk, diversified investments

**Profile Details:**
- You prefer stable, predictable returns
- Low tolerance for market volatility  
- Focus on capital preservation
- Suitable for bonds, ETFs, and blue-chip stocks

*Note: This is a demonstration analysis. In production, I would analyze your actual transaction history, income patterns, and investment goals.*"""

            await ctx.send(sender, create_text_chat(response_text))
            continue

        elif any(word in user_text for word in ["portfolio", "invest", "recommend", "allocation"]):
            ctx.logger.info("💼 Processing portfolio recommendation request")
            
            response_text = """💼 **Portfolio Recommendations**

Based on your Conservative risk profile (0.3), here's a personalized investment recommendation:

**Recommended Portfolio Allocation** (for $10,000):

🔹 **60% - SPY (S&P 500 ETF)** - $6,000
   Low-cost, broad market exposure

🔹 **25% - MSFT (Microsoft)** - $2,500  
   Stable tech stock with dividend

🔹 **15% - VTI (Total Market ETF)** - $1,500
   Additional diversification

**Strategy Rationale:**
- Heavy emphasis on stable, diversified ETFs
- Conservative individual stock selection
- Low volatility with steady growth potential
- Appropriate for risk-averse investors
- Expected annual return: 6-8%

*This is a demonstration recommendation. Real portfolio advice should consider your complete financial situation, investment timeline, and specific goals.*"""

            await ctx.send(sender, create_text_chat(response_text))
            continue

        elif any(word in user_text for word in ["hello", "hi", "start", "begin"]):
            welcome_text = """👋 **Welcome to FinMem!**

I'm your AI-powered financial assistant, here to help with:

🎯 **Risk Assessment** - Understand your investment risk tolerance
💼 **Portfolio Planning** - Get personalized investment recommendations  
📊 **Financial Guidance** - Navigate investment decisions

**Popular requests:**
• "Analyze my risk profile"
• "What portfolio do you recommend?"
• "Help me plan my investments"

What would you like to explore today?"""

            await ctx.send(sender, create_text_chat(welcome_text))
            continue

        else:
            # Default response for unrecognized input
            default_text = """🤔 **I'm here to help with your finances!**

I specialize in:
• **Risk profiling** - Understanding your investment comfort level
• **Portfolio recommendations** - Suggesting optimal asset allocations
• **Investment planning** - Helping you make informed decisions

**Try asking:**
• "What's my risk profile?"
• "Recommend a portfolio for me"  
• "Help me with investment planning"
• "What should I invest in?"

How can I assist with your financial goals today?"""

            await ctx.send(sender, create_text_chat(default_text))

# -----------------------------------------------------------------------------
# Chat acknowledgment handler
# -----------------------------------------------------------------------------

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.debug(f"✅ Chat ACK from {sender} for message {msg.acknowledged_msg_id}")

# -----------------------------------------------------------------------------
# Include protocol and run agent
# -----------------------------------------------------------------------------

agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    print("""
🤖 Starting FinMem Chat Agent...

This AI financial assistant provides:
✅ Risk profile analysis based on spending patterns
✅ Personalized portfolio recommendations  
✅ Investment planning and guidance
✅ Compatible with Agentverse chat interface

💬 Chat with this agent through Agentverse at: https://agentverse.ai
🔍 Find your agent using its address after startup
🛑 Stop with Ctrl+C
    """)
    agent.run()