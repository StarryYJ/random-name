import numpy as np
import pandas as pd


def strategy(pos: None):
	"""
	trading strategy

	:param pos: current positions
	:return: new positions
	"""
	if pos is None:
		pos = pd.DataFrame(
			columns=['symbol', 'time', 'transaction price', 'transaction direction', 'volume',
					 'latest position'])

	return pos


def take_profit(pos: pd.DataFrame, state: pd.Series):
	"""
	take profit strategy
	:param pos: current position
	:param state: current strategy
	:return: percentage decision(s) about take profit, positive means buy and negative means sell
	"""
	group_by = pos.groupby('symbol')
	average_transaction_price = group_by.agg({'transaction price': 'mean'})
	latest = group_by.apply(max, column='time')

	tp = pd.Series(index=state.index)

	for i in range(len(average_transaction_price)):
		symbol = average_transaction_price['symbol'][i]
		direction = np.sign(latest['latest position'][i])
		price = state[symbol]
		if direction * (price - average_transaction_price) / average_transaction_price > 0.3:
			tp[symbol] = direction * -1
		elif direction * (price - average_transaction_price) / average_transaction_price > 0.1:
			tp[symbol] = direction * -0.5
		else:
			tp[symbol] = 0

	return tp


def stop_loss(pos: pd.DataFrame, state: pd.Series):
	"""
	stop loss strategy
	:param pos: current position
	:param state: current strategy
	:return: percentage decision(s) about stop loss, positive means buy and negative means sell
	"""
	group_by = pos.groupby('symbol')
	average_transaction_price = group_by.agg({'transaction price': 'mean'})
	latest = group_by.apply(max, column='time')

	sl = pd.Series(index=state.index)

	for i in range(len(average_transaction_price)):
		symbol = average_transaction_price['symbol'][i]
		direction = np.sign(latest['latest position'][i])
		price = state[symbol]
		if direction * (price - average_transaction_price) / average_transaction_price < -0.3:
			sl[symbol] = direction * -1
		elif direction * (price - average_transaction_price) / average_transaction_price < -0.1:
			sl[symbol] = direction * -0.5
		else:
			sl[symbol] = 0

	return sl


def take_action(profit, loss, position: pd.DataFrame, state: pd.Series):
	"""
	'realize' actions in trading simulation

	:param profit: output of take_profit function, percentage decision(s) about taking profit
	:param loss: output of stop_loss function, percentage decision(s) about stopping loss
	:param position: position memory data frame
	:param state: current state(prices)
	:return: this directly made change on position data frame because position is passed by reference
	"""

	current_pos = position.groupby('symbol').apply(max, column='time')

	for i in range(len(current_pos)):
		pf = profit[current_pos['symbol'][i]]
		ls = loss[current_pos['symbol'][i]]

		if pf != 0:
			position.append(current_pos.iloc[i, :], ignore_index=True)
			position.iloc[-1, 2] = state[current_pos['symbol'][i]]
			position.iloc[-1, 3] = -1 * np.sign(position.iloc[-1, 5])
			position.iloc[-1, 4] = position.iloc[-1, 5] * abs(pf)
			position.iloc[-1, 5] *= (1 + pf)

		if ls != 0:
			position.append(current_pos.iloc[i, :], ignore_index=True)
			position.iloc[-1, 2] = state[current_pos['symbol'][i]]
			position.iloc[-1, 3] = -1 * np.sign(position.iloc[-1, 5])
			position.iloc[-1, 4] = position.iloc[-1, 5] * abs(ls)
			position.iloc[-1, 5] *= (1 + ls)


def back_testing(initial_money, symbols, start, end, profit_str, loss_str, interval, positions: None):
	"""
	Back_testing with specific take_profit and stop_loss strategy on given look back period

	:param initial_money: initial investing in the market
	:param symbols: list of stocks you consider to include in your portfolio
	:param start: start date of look back period
	:param end: end date of look back period
	:param profit_str: function of take profit strategy
	:param loss_str: function of stop loss strategy
	:param interval: 'days', 'minute'
	:param positions: None, of pandas data frame with columns
					['symbol', 'time', 'transaction price', 'transaction direction', 'volume', 'latest position']
	:return: total profit
	"""
	if positions is None:
		positions = pd.DataFrame(
			columns=['symbol', 'time', 'transaction price', 'transaction direction', 'volume',
					 'latest position'])

	# 	read stock data with suitable API, combine to a data frame whose columns stands for symbols and index for time
	data = pd.DataFrame()

	for i in range(len(data)):
		tp = profit_str(positions, data.iloc[i, :])
		sl = loss_str(positions, data.iloc[i, :])

		if not (all(tp == 0) and all(sl == 0)):
			take_action(tp, sl, positions, data.iloc[i, :])

	market_value = initial_money
	for i in range(len(positions)):
		market_value += -1 * np.prod(positions.iloc[i, 2:5])

	profit = market_value - initial_money

	print('--------------------------------------------------------\n')
	print('Back testing from {0} to {1}: \n'.format(start, end))
	print('Total profit is ' + str(profit) + '.\n')
	print('Taking {0} as initial investing, percentile profit is {1}.\n'.format(initial_money, profit/initial_money))
	print('--------------------------------------------------------\n')

	return profit


def simulated_trading(initial_money, symbols, profit_str, loss_str, interval, memory_address=None):
	"""
	simulate trading to test strategy performance

	:param initial_money: initial investing in the market
	:param symbols: list of stocks you consider to include in your portfolio
	:param profit_str: function of take profit strategy
	:param loss_str: function of stop loss strategy
	:param interval: time gap on checking actions
	:param memory_address: where to read/store memory
	:return: total profit
	"""
	if memory_address is not None:
		memory = pd.read_csv(memory_address)
	else:
		memory = pd.DataFrame(
			columns=['symbol', 'time', 'transaction price', 'transaction direction', 'volume',
					 'latest position'])

	if memory_address is None:
		memory.to_csv('memory/strategy1.csv', index=False)
	else:
		memory.to_csv(memory_address)
	pass
