import trapilot

if __name__ == "__main__":
    exchange = trapilot.blankly.EXCHANGE_CLASS()
    strategy = trapilot.blankly.Strategy(exchange)

    if trapilot.blankly.is_deployed:
        strategy.start()
    else:
        strategy.backtest(to="1y", initial_values={"QUOTE_ASSET": 10000})
