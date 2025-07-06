# portfolio_agent.py
from uagents import Agent, Context, Protocol
from contracts import PortfolioRequest, PortfolioResponse, Asset
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import chat_agent_executor
import json

assets_catalogue = [...]  # ⬅ load from data_models or hard-code like in assets repo

agent = Agent(name="portfolio_agent", seed="portfolio seed", port=8002, mailbox=True)
model = ChatOpenAI(temperature=0)
app = chat_agent_executor.create_tool_calling_executor(model, tools=[])

proto = Protocol(name="portfolio_protocol", version="1.0")

@proto.on_message(model=PortfolioRequest, replies=PortfolioResponse)
async def suggest(ctx: Context, sender: str, msg: PortfolioRequest):
    prompt = f"""
You are an investment advisor...
Client Risk: {msg.risk_bucket} ({msg.risk_score})
Balance: {msg.balance}
Assets: {json.dumps(assets_catalogue)}
Return JSON list of assets (symbol, weight, units) totalling 1.0
"""
    llm_out = app.invoke({"messages":[{"role":"user","content":prompt}]})
    rec = json.loads(llm_out["output"])
    await ctx.send(sender, PortfolioResponse(**rec))

agent.include(proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
