import requests

import trapilot
from trapilot.data import PriceReader


def price_event(price, symbol, state: trapilot.StrategyState):
    """This function will give an updated price every 15 seconds from our definition below"""
    state.variables["history"].append(price)
    rsi = trapilot.indicators.rsi(state.variables["history"])
    curr_value = state.interface.account[state.base_asset].available
    if rsi[-1] < 30 and not curr_value:
        # Dollar cost average buy
        buy = trapilot.trunc(state.interface.cash / price, 5)
        state.interface.market_order(symbol, side="buy", size=buy)
    elif rsi[-1] > 70 and curr_value:
        # Dollar cost average sell
        state.interface.market_order(symbol, side="sell", size=curr_value)


def init(symbol, state: trapilot.StrategyState):
    # Download price data to give context to the algo
    state.variables["history"] = state.interface.history(
        symbol, to=150, return_as="deque", resolution=state.resolution
    )["close"]


if __name__ == "__main__":
    # This downloads an example CSV
    data = requests.get(
        "https://firebasestorage.googleapis.com/v0/b/trapilot-6ada5.appspot.com/o/demo_data.csv?alt=media&token=acfa5c39-8f08-45dc-8be3-2033dc2b7b28"
    ).text
    with open("./price_examples.csv", "w") as file:
        file.write(data)

    # Run on the keyless exchange, starting at 100k
    exchange = trapilot.KeylessExchange(
        price_reader=PriceReader("./price_examples.csv", "BTC-USD")
    )

    # Use our strategy helper
    strategy = trapilot.Strategy(exchange)

    # Make the price event function above run every day
    strategy.add_price_event(price_event, symbol="BTC-USD", resolution="1d", init=init)

    # Backtest the strategy
    results = strategy.backtest(
        start_date=1598377600, end_date=1650067200, initial_values={"USD": 10000}
    )
    print(results)
