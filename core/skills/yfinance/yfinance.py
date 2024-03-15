import typing
import yfinance as yf
import logging
logger = logging.getLogger("skill.yfinance")

class YFinance:
    def __init__(self, skill_config: typing.Dict, ova: "OpenVoiceAssistant"):
        self.ova = ova
        self.watch_list = skill_config["watch_list"]

    def market_overview(self, context: typing.Dict):
        tickers = yf.Tickers(" ".join(self.watch_list))
        reports = []
        for ticker, info in tickers.tickers.items():
            try:
                open_price = int(info.info["open"])
                name = info.info["shortName"]
                reports.append(f"the {name} opened at {open_price}")
            except Exception as e:
                logger.exception("Exception fetching stock price")
                pass
        if reports:
            response = "Today "
            response += ". ".join(reports)
        else:
            response = "No stocks provided to check"

        context["response"] = response