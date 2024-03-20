import typing
INTENTIONS = [
        {
            "action": "market_overview",
            "patterns": [
                "hows the market doing today",
                "hows the stock market",
                "whats the stock market update",
                "give me an update on the stock market",
                "how are the stocks doing today",
                "show me the current stock market status",
                "whats the latest news on the stock market",
                "can you provide me with a stock market update",
                "whats the stock market looking like right now",
                "give me the latest stock market information",
                "tell me about the stock market performance",
                "whats happening in the stock market",
                "show me the stock market trends"
            ]
        }
    ]

def build_skill(skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
    from .yfinance import YFinance
    return YFinance(skill_config, ova)

def manifest():
    return {
        "name": "Yahoo Finance",
        "id": "yfinance",
        "category": "stock_market",
        "requirements": ["yfinance==0.2.36"],
        "config": {
            "watch_list": [
                "^GSPC",
                "VTI",
                "BND"
            ]
        }
    }