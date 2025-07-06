# chat_agent.py
from uagents import Agent, Context, Protocol
from contracts import *
from datetime import datetime, UTC
from uuid import uuid4
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec, ChatMessage, ChatAcknowledgement,
    TextContent, EndSessionContent
)

RISK_ADDR      = "agent1..."   # set actual address after startup
PORTFOLIO_ADDR = "agent1..."

agent = Agent(name="chat_agent", seed="chat seed", port=8000, mailbox=True)
chat_proto = Protocol(spec=chat_protocol_spec)

@chat_proto.on_message(ChatMessage)
async def inbound(ctx: Context, sender: str, msg: ChatMessage):
    # ☑ immediately ACK
    await ctx.send(sender, ChatAcknowledgement(
        timestamp=datetime.now(UTC), acknowledged_msg_id=msg.msg_id
    ))

    user_txt = [c.text for c in msg.content if isinstance(c, TextContent)][0]
    # Naïve intent: first ask risk -> then portfolio
    # In production use ASI:One or small intent classifier
    if user_txt.lower().startswith("profile"):
        await ctx.send(RISK_ADDR, RiskProfileRequest(...))
        ctx.storage.set("waiting_for", ("profile", sender))
    elif user_txt.lower().startswith("portfolio"):
        # we need risk first, fetch from db or ask risk agent again
        ...
    else:
        await ctx.send(sender, _text("Sorry, try 'profile' or 'portfolio'"))

def _text(body: str, end=True):
    content=[TextContent(type="text",text=body)]
    if end: content.append(EndSessionContent(type="end-session"))
    return ChatMessage(timestamp=datetime.now(UTC), msg_id=uuid4(), content=content)

agent.include(chat_proto, publish_manifest=True)
if __name__ == "__main__":
    agent.run()
