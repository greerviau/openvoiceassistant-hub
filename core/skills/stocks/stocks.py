import typing
import yfinance as yf

class Stocks:
    def __init__(self, skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
        self.ova = ova
        self.watch_list = skill_config["watch_list"]

    def market_overview(self, context: typing.Dict):
        tickers = yf.Tickers(' '.join(self.watch_list))
        reports = []
        for ticker, info in tickers.tickers.items():
            try:
                open_price = int(info.info['open'])
                name = info.info['shortName']
                reports.append(f"the {name} opened at {open_price}")
            except:
                pass
        if reports:
            response = "Today "
            response += ". ".join(reports)
        else:
            response = "No stocks provided to check"

        context["response"] = response

def build_skill(skill_config: typing.Dict, ova: 'OpenVoiceAssistant'):
    return Stocks(skill_config, ova)

def default_config():
    return {
        "watch_list": [
            "^GSPC",
            "VTI",
            "BND"
        ]
    }