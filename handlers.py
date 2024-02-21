# @schedule(interval="1h", symbol="BTCUSDT")
# def handler(state, data):
#     ema_long = data.ema(40).last
#     ema_short = data.ema(20).last
#     # we skip execution on missing data
#     if ema_long is None:
#         return False
#     has_position = has_open_position(data.symbol, include_dust=True)
#     if ema_short > ema_long and not has_position:
#         print("Buying {}".format(data.symbol))
#         order_market_amount(symbol=data.symbol,amount=0.001)
#     elif ema_short < ema_long and has_position:
#         print("Selling {}".format(data.symbol))
#         close_position(data.symbol)



# Check outstanding limit order
# def initialize(state):
#    state.run_once = False
#    state.order=None
#    state.order_id = None
# @schedule(interval="1h", symbol="BTCUSDT")
# def handler(state, data):
#    if not state.run_once:
#       state.run_once = True
#       limit_price = float(data.close.last * 0.99)
#       state.order = order_limit_value(symbol = data.symbol, limit_price = limit_price, value = 100)
#       # record the order id
#       state.order_id = state.order.id
#       ''' method 1 using order object '''
#       if state.order is not None :
#          state.order.refresh()
#          if state.order.is_filled():
#             print(f"Checking order with object. The order {state.order.id} was filled")
#             state.order = None
#       ''' method 2 looking up the order with id '''
#       if state.order_id is not None :
#          temp_order = query_order(state.order_id)
#          if temp_order.is_filled():
#             print(f"Check order with id. The order {temp_order.id} was filled")
#             state.order_id = None



# Buy Example
# def initialize(state):
#     state.buy_order = None
# @schedule(interval="1h", symbol="BTCUSDT", window_size=200)
# def handler_1h(state, data):
#    pos = query_open_position_by_symbol(symbol=data.symbol, include_dust=False)
#    if pos is None:   # if there is not a position then place an order
#       if state.buy_order is None:   # make sure there is only one buy order at a time
#          # place a trailing order 1% above the current market price that tracks the price within 2%
#          stop_price = data.close[-1]*1.01 # price the order is initially placed at
#          state.buy_order = order_trailing_iftouched_amount(data.symbol, amount=0.01, trailing_percent=0.02, stop_price=stop_price)
#    else:
#       # if the traliing order was filled close the close_position
#       close_position(data.symbol)
#       state.buy_order = None      # reset buy order so we can place another

# Sell Example
# def initialize(state):
#     state.buy_order = None
#     state.sell_order = None
# @schedule(interval="1h", symbol="BTCUSDT", window_size=200)
# def handler_1h(state, data):
#     pos = query_open_position_by_symbol(symbol=data.symbol, include_dust=False)
#     if pos is None:  # if there is not a position then place a market buy order
#        # place buy market order
#        state.buy_order = order_amount(data.symbol, 0.01)
#        # place trailing stop loss for order
#        amount = -subtract_order_fees(buy_order.quantity)  # adjust sell for fees and make negative
#        stop_price = data.close[-1]*0.97    # 3 % below market
#        state.sell_order = order_trailing_iftouched_amount(data.symbol, amount=amount, trailing_percent=0.05, stop_price=stop_price)



# Buy Example
# stop_price = data.close[-1]*1.01 # buy traling needs to be place above current market price
# state.buy_order = order_trailing_iftouched_value("BTCUSDT", value=500, trailing_percent=0.02, stop_price=stop_price)

# Sell Example
# stop_price = data.close[-1]*0.98 # sell traling order needs to be place below current market price
# state.sell_order = order_trailing_iftouched_value("BTCUSDT", value=-500, trailing_percent=



# # send a market order for 0.05 BTC
# market_order = order_amount(symbol="BTCUSDT", amount=0.005)
# print(market_order.type)

# # send a limit buy order with a limit price of 30000
# limit_order = order_amount(symbol="BTCUSDT", amount=0.005, limit_price=30000)
# print(limit_order.type)

# # place a stop buy market order when price reaches 31000
# stop_order = order_amount(symbol="BTCUSDT", amount=0.005, stop_price=31000)
# print(stop_order.type)

# # when the price reaches 30250 place a limit order with limit price of 30000
# iftouchedLimit = order_amount(symbol="BTCUSDT", amount=0.005, limit_price=30000, stop_price=30250)
# print(iftouchedLimit.type)



# # send a market order for 200 USDT
# market_order = order_value(symbol="BTCUSDT", value=200)
# print(market_order.type)

# # send a limit buy order with a limit price of 30000
# limit_order = order_value(symbol="BTCUSDT", value=200, limit_price=30000)
# print(limit_order.type)

# # place a stop buy market order when price reaches 31000
# stop_order = order_value(symbol="BTCUSDT", value=200, stop_price=31000)
# print(stop_order.type)

# # when the price reaches 30250 place a limit order with limit price of 30000
# iftouchedLimit = order_value(symbol="BTCUSDT", value=200, limit_price=30000, stop_price=30250)
# print(iftouchedLimit.type)



# # sends a limit order for 20% of the porfolio value
# order_target(symbol="BTCUSDT", target_percent=0.2, limit_price=7800.00)



# ''' Rebalance portfolio allocation with market orders '''
# import numpy as np
# @schedule(interval="1h", symbol="BTCUSDT")
# def handler(state, data):
#     weight = query_position_weight(symbol="BTCUSDT")
#     target_alloc = 0.2    # target to have 20% of the portfolio value in BTC
#     # check if the portfolio allocation is within 1% of target
#     if not np.isclose(float(weight), target_alloc, atol=0.01) :
#         # rebalance portfolio
#         order = order_target("BTCUSDT", 0.2)
#     else:
#         log(f"porfolio is balanced {weight}", severity=2)



# @schedule(interval="5m",symbol="BTCUSDT")
# def handler(state,data):
#     with OrderScope.sequential(fail_on_error=False, wait_for_entire_fill=False):
#         order_1 = order_market_value("BTCUSDT",100,8000)
#         order_2 = order_market_value("BTCUSDT",100,9000)
#         order_3 = order_market_value("BTCUSDT",100,9000)



# @schedule(interval="5m",symbol="BTCUSDT")
# def handler(state,data):
#     with OrderScope.sequential(fail_on_error=False, wait_for_entire_fill=False):
#         order_1 = order_market_value("BTCUSDT",0)
#         order_2 = order_market_value("BTCUSDT",100)



# @schedule(interval="5m",symbol=["BTCUSDT","ETHUSDT"])
# def handler(state,data):
#     with OrderScope.sequential(fail_on_error=True, wait_for_entire_fill=False):
#         order_1 = order_limit_amount("BTCUSDT",0.5, 4000)
#         order_2 = order_market_value("ETHUSDT",500)



# # We're entering the scope, orders in OCO mode will not be submitted immediatly
# with OrderScope.one_cancels_others():
#     order_1 = order_limit_amount("BTCUSDT", amount=0.01, limit_price=10323)
#     order_2 = order_limit_amount("ETHUSDT", amount=24.03, limit_price=314)
#     print(order_1.status) # OrderStatus.Created
#     print(order_2.status) # OrderStatus.Created
# # Scope is exited, orders are submitted, and order ojects are refreshed
# print(order_1.status) # OrderStatus.Pending
# print(order_2.status) # OrderStatus.Pending



# @schedule(interval="5m",symbol="BTCUSDT")
# def handler(state,data):
#     with OrderScope.one_cancels_others():
#         buy_order = order_iftouched_market_amount("BTCUSDT",-0.5,8500)
#         sell_order = order_iftouched_market_amount("BTCUSDT",-0.5,9000)



# btc = query_balance("BTC")
# eth = query_balance("ETH")
# print( btc.free + eth.free )




# btc = query_balance_free("BTC")
# '''
# Note the conversion to float when multiplying with regular floats
# '''
# print( float(btc) * 2.0 )



# btc_locked = query_balance_locked("BTC")
# if btc_locked > 0:
#     print("Bot has open orders")



# all_balances = query_balances()
# for balance in all_balances:
#     print(balance.free)