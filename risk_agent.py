# risk_agent.py
import os, time, json
from datetime import datetime, UTC
from uagents import Agent, Context, Protocol
from langchain_openai import ChatOpenAI
from contracts import RiskProfileRequest, RiskProfileResponse
from uagents_core.contrib.protocols.chat import chat_protocol_spec

agent = Agent(
    name="risk_profile_agent",
    seed="risk profile seed phrase",
    port=8001,
    mailbox=True          # so it can run local *or* on Agentverse
)

# Simple LangGraph wrapper – official pattern
from langgraph.prebuilt import chat_agent_executor
model = ChatOpenAI(temperature=0)
app = chat_agent_executor.create_tool_calling_executor(model, tools=[])

def llm_risk(prompt: str) -> dict:
    messages = {"messages": [{"role": "user", "content": prompt}]}
    final = None
    for chunk in app.stream(messages):
        final = list(chunk.values())[0]
    return json.loads(final["messages"][-1].content)

proto = Protocol(name="risk_profile_protocol", version="1.0")

@proto.on_message(model=RiskProfileRequest, replies=RiskProfileResponse)
async def handle(ctx: Context, sender: str, msg: RiskProfileRequest):
    ctx.logger.info(f"⌛ Profiling {len(msg.transactions)} transactions for {msg.user_id}")
    prompt = f"""
You are an investment advisor...
<transactions>{[t.dict() for t in msg.transactions]}</transactions>
Return JSON with risk_bucket, risk_score
"""
    result = llm_risk(prompt)
    await ctx.send(sender, RiskProfileResponse(user_id=msg.user_id, **result))

agent.include(proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
