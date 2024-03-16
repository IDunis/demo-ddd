import trapilot

if __name__ == "__main__":
    exchange = trapilot.EXCHANGE_CLASS()
    strategy = trapilot.Strategy(exchange)

    if trapilot.is_deployed:
        strategy.start()
    else:
        strategy.backtest(to='1y', initial_values={'QUOTE_ASSET': 10000})
