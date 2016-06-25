import datetime
import pandas as pd
import numpy as np
import quandl
from abc import ABCMeta, abstractmethod


class MovingAverageXStrategy():
	def __init__(self,symbol,bars,short_window,long_window):
		self.symbol=symbol
		self.bars = bars
		self.short_window=short_window
		self.long_window=long_window

	def generate_signals(self):
		signals=pd.DataFrame(index=self.bars.index)
		signals['signal']=0

		signals['short_mavg']=pd.rolling_mean(self.bars['Close'],self.short_window, min_periods=1)
		signals['long_mavg']=pd.rolling_mean(self.bars['Close'],self.long_window,min_periods=1)

		signals['signal'][self.short_window:] = np.where(signals['short_mavg'][self.short_window:] > signals['long_mavg'][self.short_window:],1,0)
		signals['positions'] = signals['signal'].diff()
		self.signals=signals

		return signals	

class PostEarningsDriftStrategy():
	def __init__(self,symbol,bars,window):
		self.symbol=symbol
		self.bars = bars
		self.window=window
	def generate_signals(self):
		return 0

class MarketonClosePortfolio():
	def __init__(self,symbol,bars,signals,initial_capital):
		self.symbol=symbol
		self.bars=bars
		self.signals=signals
		self.initial_capital=initial_capital

	def generate_positions(self):
		positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
		positions[self.symbol]=100*self.signals['signal']
		self.positions=positions
		return positions

	def backtest_portfolio(self):
		portfolio = self.positions[self.symbol] * self.bars['Close']
		pos_diff= self.positions[self.symbol].diff()

		portfolio['holdings']=(self.positions*self.bars['Close'])
		portfolio['cash']=self.initial_capital - (pos_diff*self.bars['Close']).cumsum()

		portfolio['total']=portfolio['cash']+portfolio['holdings']
		portfolio['returns']=portfolio['total'].pct_change()
		return portfolio


if __name__=='__main__':
	symbol = 'ORCL'
	bars= pd.read_csv('orcl-2000.csv')

	mac=MovingAverageXStrategy(symbol,bars,short_window=40,long_window=100)
	signals=mac.generate_signals()

	portfolio=MarketOnClosePortfolio(symbol,bars,signals,initial_capital=100000.0)
	returns = portfolio.backtest_portfolio()

