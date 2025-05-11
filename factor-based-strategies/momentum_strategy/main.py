from AlgorithmImports import *

class MomentumStrategy(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2023, 1, 1)
        self.SetCash(100000)

        self.symbols = [Symbol.Create(ticker, SecurityType.Equity, Market.USA) 
                        for ticker in ["AAPL", "MSFT", "GOOG", "META", "TSLA", "AMZN", "NVDA", "PEP", "JNJ", "UNH", "V", "MA", "HD", "PG", "DIS"]]
        
        for symbol in self.symbols:
            self.AddEquity(symbol.Value, Resolution.Daily)
        
        self.momentum_period = 126  # Approx 6 months of trading days
        self.rebalance_month = -1
        self.momentum_scores = {}

        self.Schedule.On(self.DateRules.MonthStart("AAPL"), self.TimeRules.AfterMarketOpen("AAPL", 30), self.Rebalance)

    def Rebalance(self):
        if self.rebalance_month == self.Time.month:
            return  # Already rebalanced this month
        self.rebalance_month = self.Time.month

        self.momentum_scores.clear()

        for symbol in self.symbols:
            history = self.History(symbol, self.momentum_period, Resolution.Daily)
            if history.empty: continue

            close_prices = history['close']
            ret = (close_prices.iloc[-1] / close_prices.iloc[0]) - 1
            self.momentum_scores[symbol] = ret

        top_momentum = sorted(self.momentum_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        top_symbols = [symbol for symbol, score in top_momentum]

        self.Debug(f"{self.Time.date()} Top momentum: {[s.Value for s in top_symbols]}")

        # Liquidate those not in top
        for holding in self.Portfolio:
            if holding.Value.Invested and holding.Key not in top_symbols:
                self.Liquidate(holding.Key)

        # Invest equally in top
        weight = 1.0 / len(top_symbols)
        for symbol in top_symbols:
            self.SetHoldings(symbol, weight)