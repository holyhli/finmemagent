# risk_agent.py
import json
from dotenv import load_dotenv
from uagents import Agent, Context, Protocol
from langchain_anthropic import ChatAnthropic
from contracts import RiskProfileRequest, RiskProfileResponse

load_dotenv()

agent = Agent(
    name="risk_profile_agent",
    seed="risk profile seed phrase",
    port=8001,
    mailbox=True
)

# Simple LangGraph wrapper – official pattern
from langgraph.prebuilt import chat_agent_executor
model = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0)
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
You are an investment advisor analyzing a user's financial transactions to determine their risk profile.

Transactions: {msg.transactions}

Based on these transactions, analyze the user's spending patterns and financial behavior.
Return a JSON object with exactly these fields:
- risk_bucket: one of "conservative", "moderate", "aggressive"
- risk_score: a number between 0.0 and 1.0 (0 = very conservative, 1 = very aggressive)
- reasoning: brief explanation of the assessment

Example format:
{{
  "risk_bucket": "moderate",
  "risk_score": 0.6,
  "reasoning": "Regular income with moderate discretionary spending suggests balanced risk tolerance."
}}
"""
    result = llm_risk(prompt)
    await ctx.send(sender, RiskProfileResponse(user_id=msg.user_id, **result))

agent.include(proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
