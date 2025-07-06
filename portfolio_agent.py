# portfolio_agent.py
import json
from dotenv import load_dotenv
from uagents import Agent, Context, Protocol
from contracts import PortfolioRequest, PortfolioResponse
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import chat_agent_executor

load_dotenv()

assets_catalogue = [
    {"symbol": "AAPL", "name": "Apple Inc.", "type": "stock", "risk_level": "medium"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "type": "stock", "risk_level": "medium"},
    {"symbol": "MSFT", "name": "Microsoft Corp.", "type": "stock", "risk_level": "low"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "type": "stock", "risk_level": "high"},
    {"symbol": "BTC", "name": "Bitcoin", "type": "crypto", "risk_level": "high"},
    {"symbol": "ETH", "name": "Ethereum", "type": "crypto", "risk_level": "high"},
    {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "type": "etf", "risk_level": "low"},
    {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "type": "etf", "risk_level": "low"}
]

agent = Agent(name="portfolio_agent", seed="portfolio seed", port=8002, mailbox=True)
model = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0)
app = chat_agent_executor.create_tool_calling_executor(model, tools=[])

proto = Protocol(name="portfolio_protocol", version="1.0")

@proto.on_message(model=PortfolioRequest, replies=PortfolioResponse)
async def suggest(ctx: Context, sender: str, msg: PortfolioRequest):
    prompt = f"""
You are an investment advisor. Create a portfolio recommendation based on the client's risk profile.
Client Risk: {msg.profile.risk_bucket} (score: {msg.profile.risk_score})
Balance: ${msg.total_balance}
Available Assets: {json.dumps(assets_catalogue)}

Return a JSON object with:
- portfolio: list of assets with symbol, weight (as decimal), and dollar_amount
- reasoning: explanation of the recommendation

Example format:
{{
  "portfolio": [
    {{"symbol": "SPY", "weight": 0.6, "dollar_amount": 6000}},
    {{"symbol": "AAPL", "weight": 0.4, "dollar_amount": 4000}}
  ],
  "reasoning": "Based on your risk profile..."
}}
"""
    try:
        llm_out = app.invoke({"messages":[{"role":"user","content":prompt}]})
        result = json.loads(llm_out["messages"][-1].content)
        await ctx.send(sender, PortfolioResponse(
            user_id=msg.user_id,
            portfolio=result.get("portfolio", []),
            reasoning=result.get("reasoning", "Portfolio recommendation generated")
        ))
    except Exception as e:
        ctx.logger.error(f"Error generating portfolio: {e}")
        await ctx.send(sender, PortfolioResponse(
            user_id=msg.user_id,
            portfolio=[],
            reasoning=f"Error generating portfolio: {str(e)}"
        ))

agent.include(proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
