#!/usr/bin/python
# -*- Coding: utf-8 -*-

class Finance:

    def __init__(self):
        self.asset = 100000
        self.bet = 10000

    def increase(self):
        self.asset += self.bet

    def decrease(self):
        self.asset -= (self.bet * 2)

    def print(self):
        print(self.asset)

class Entry_position:

    def __init__(self):
        self.position = "None"

    def high(self):
        self.position = "High"

    def low(self):
        self.position = "Low"

    def entry(self, posi):
        if posi is "High":
            self.high()
        else:
            self.low()

    def reset(self):
        self.position = "None"


class Signal_entry_create():
    """
    シグナル、エントリーの作成

        self.rsi_period : RSI期間の設定 default:14
        self.rsi_upper : RSI売りエントリーのシグナル値
        self.rsi_lower : RSI買いエントリーのシグナル値
        self.ohlc : EUR/USDレート columns=['Open', 'High', 'Low', 'Close'] index_cok=["Time"]

        def candle_stick() -> 陽線、陰線の作成
            True : 陽線  False : 陰線
    """

    def __init__(self):
        self.rsi_period = 14
        self.rsi_upper = 80
        self.rsi_lower = 20


        self.ohlc = pk.load(open('EURUSD_M5.pkl', 'rb'))

    def rsi_indicator(self):
        self.rsi = ind.iRSI(self.ohlc, self.rsi_period)

    def rsi_signal(self):
        self.high_entry = (self.rsi.shift() < self.rsi_lower).values
        self.low_entry = (self.rsi.shift() > self.rsi_upper).values

    def candle_stick(self):
        self.ck = (self.ohlc["Open"] < self.ohlc["Close"]).values

    def signal_create(self):
        self.rsi_indicator()
        self.rsi_signal()
        self.candle_stick()

if __name__ == '__main__':

    Fin = Finance()
    for now in range(10):
        if now % 2:
            Fin.increase()
        else:
            Fin.decrease()
    Fin.print()

def Backtest(ohlc, high_entry, low_entry, candle_stick):
    fn = Finance()

    for now in range(5, ohlc.shape[0]):
        if high_entry[now]:
            fn.calcu(judgment(candle_stick[now], True))
        elif low_entry[now]:
            fn.calcu(judgment(candle_stick[now], False))

    Report(fn.bet, fn.win, fn.lose)