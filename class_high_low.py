#!/usr/bin/python
# -*- Coding: utf-8 -*-

# import pandas as pd
# import numpy as np
import pickle as pk
import indicators as ind


class Finance:

    def __init__(self):
        self.asset = 100000
        self.bet = 10000
        self.win = 0
        self.lose = 0

    def increase(self):
        self.win += 1

    def decrease(self):
        self.lose += 1

    def calcu(self, which_one):
        if which_one:
            self.increase()
        else:
            self.decrease()


class Signal_entry_create:
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
        # RSI設定値
        self.rsi_period = 14
        self.rsi_upper = 70
        self.rsi_lower = 30

        # MACD設定値
        self.macd_f_period = 12
        self.macd_s_period = 26
        self.macd_signal = 9

        # レート作成
        self.ohlc = pk.load(open('EURUSD_M5.pkl', 'rb'))

        # インジゲーター ＆ ローソク足作成
        self.ck = (self.ohlc["Open"] < self.ohlc["Close"]).values
        self.rsi = ind.iRSI(self.ohlc, self.rsi_period)
        self.macd = ind.iMACD(self.ohlc, self.macd_f_period, self.macd_s_period, self.macd_signal)


def Report(bet, win, lose):
    profit = ((win - lose) * bet) / 10000
    trade = win + lose
    winning = 100 * win / trade

    print("ベット:{}円, 利益:{}万円, 総トレード数:{}, 勝率:{:.4}".format(bet, profit, trade, winning))


def judgment(candle_line, position):
    return candle_line == position


def Backtest(ohlc, high_entry, low_entry, candle_stick):
    fn = Finance()

    for now in range(5, ohlc.shape[0]):
        if high_entry[now]:
            fn.calcu(judgment(candle_stick[now], True))
        elif low_entry[now]:
            fn.calcu(judgment(candle_stick[now], False))

    Report(fn.bet, fn.win, fn.lose)


if __name__ == '__main__':
    sec = Signal_entry_create()

    h_entry = ((sec.rsi.shift() < sec.rsi_lower) & (sec.macd["Main"] > sec.macd["Signal"])).values
    l_entry = ((sec.rsi.shift() > sec.rsi_upper) & (sec.macd["Main"] < sec.macd["Signal"])).values

    Backtest(sec.ohlc, h_entry, l_entry, sec.ck)
