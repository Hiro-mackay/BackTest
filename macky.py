#!/usr/bin/python
# coding: UTF-8

import pickle as pk
from indicators import iMACD, iStochastic, iRSI, iADXWilder, iDEMA, iADX
import pandas as pd

"""
import numpy as np
from collections import Counter
import csv
"""


class Post_Process(object):
    """
    Post Process

        self.ohlc : EUR/USDレート columns=['Open', 'High', 'Low', 'Close'] index_cok=["Time"]

        candle -> 陽線、陰線の作成
            True : 陽線  False : 陰線

        def judgement(high, low)
        high -> highエントリー
        low  -> lowエントリー
        When "judgment()" is executed, total profit and winning percentage indication
    """

    def __init__(self):
        # レート作成
        self.ohlc = pk.load(open('EURUSD_M5.pkl', 'rb'))
        # ベット金額
        self.bet = 10000

    def trend_line_signal(self, top_line, middle_line, bottom_line=None):
        """
        上抜けシグナル判定関数


        インジゲータのシグナル線が以下のように並ぶ場合、True
        ------  top_line
        ------  middle_line
        ------  bottom_line(middle_line)

        :param top_line:
        :param middle_line:
        :param bottom_line:
        :return:
        """

        _bottom_line = middle_line if bottom_line is None else bottom_line
        return (top_line > middle_line) & (middle_line >= _bottom_line)

    def low_entry_create(self, upper, main, signal=None):  # upper_draw low_entry
        """
        main:インジゲータメインライン
        signal:インジゲータシグナルライン
        upper:シグナルポイント(70~80)

        :param main:
        :param signal:
        :param upper:
        :return:
        """
        _signal = 100 if signal is None else signal
        return (main > upper) & (_signal > upper)

    def high_entry_create(self, lower, main, signal=None):  # lower_draw high_entry
        """
        main:インジゲータメインライン
        signal:インジゲータシグナルライン
        upper:シグナルポイント(70~80)



        :param main:
        :param signal:
        :param lower:
        :return:
        """
        _signal = 0 if signal is None else signal
        return (main < lower) & (_signal < lower)

    def entry_signal(self, signal, determined_point):
        """
        signal -> インジゲータによるエントリーシグナルの配列
        determined_point -> エントリーポイント
            True:エントリーシグナルが出た直後
            False:エントリーシグナルが終わる直前

        True:インジゲーターエントリ−ポイント
        :param signal:
        :return:
        """
        return (signal != signal.shift(1)) & (signal == determined_point)

    def judgment(self, high_entry, low_entry, judge_time):
        candle = self.candle((judge_time // 5) - 1)
        win_high = (high_entry == candle) & (high_entry == True)
        win_low = ~(low_entry == candle) & (low_entry == True)
        lose_high = ~(high_entry == candle) & (high_entry == True)
        lose_low = (low_entry == candle) & (low_entry == True)

        win_H = win_high.value_counts()[True]
        win_L = win_low.value_counts()[True]
        lose_H = lose_high.value_counts()[True]
        lose_L = lose_low.value_counts()[True]

        print("High Entry")
        self.finance(win_H, lose_H)
        print("Low Entry")
        self.finance(win_L, lose_L)

    def candle(self, judge_time):
        return (self.ohlc["Open"] < self.ohlc["Close"].shift(-judge_time)).shift(-1)

    def finance(self, win, lose):
        profit = win * self.bet
        loss = lose * self.bet
        print("総利益:{}円".format(profit - loss))
        print("利益:{}円".format(profit))
        print("損失:{}円".format(loss))
        print("勝率:{:.2f}\n".format(100 * profit / (profit + loss)))


class MA_Signal_Create(Post_Process):
    def __init__(self):
        super().__init__()

        self.period_short_term = 55
        self.period_medium_term = 144
        self.period_long_term = 233
        self.ma_entry_time = 15

        self.weight_short = pd.DataFrame(index=self.ohlc.index, columns=[])
        self.weight_medium = pd.DataFrame(index=self.ohlc.index, columns=[])
        self.weight_long = pd.DataFrame(index=self.ohlc.index, columns=[])
        self.weight_short["Weight"] = 0
        self.weight_medium["Weight"] = 0
        self.weight_long["Weight"] = 0


        self.short_ma = iDEMA(self.ohlc, self.period_short_term)
        self.medium_ma = iDEMA(self.ohlc, self.period_medium_term)
        self.long_ma = iDEMA(self.ohlc, self.period_long_term)

        self.rising_trend = self.trend_line_signal(self.short_ma, self.medium_ma, self.long_ma)
        self.down_trend = self.trend_line_signal(self.long_ma, self.medium_ma, self.short_ma)

    def MA_ind(self):
        print("Double Exponential Moving Average")
        self.judgment(self.rising_trend, self.down_trend, self.ma_entry_time)

    def MA_neural_network(self):
        w_short = 0.1
        w_medium = 0.1
        w_long = 0.1


class Rsi_Signal_Create(Post_Process):

    def __init__(self):
        super().__init__()

        # RSI設定値
        self.rsi_period = 14
        self.rsi_upper = 70
        self.rsi_lower = 30
        self.rsi_entry_time = 5

        # インジゲータ作成
        self.rsi = iRSI(self.ohlc, self.rsi_period)
        self.low_signal = self.low_entry_create(self.rsi_upper, self.rsi)
        self.high_signal = self.high_entry_create(self.rsi_lower, self.rsi)

        self.low_entry = self.entry_signal(self.low_signal, False)
        self.high_entry = self.entry_signal(self.high_signal, False)

    def rsi_ind(self):
        print("RSI")
        self.judgment(self.high_entry, self.low_entry, self.rsi_entry_time)


class Macd_Signal_Create(Post_Process):

    def __init__(self):
        super().__init__()

        # MACD設定値
        self.macd_f_period = 12
        self.macd_s_period = 26
        self.macd_signal = 9
        self.macd_entry_time = 5

        # インジゲータ作成
        self.macd = iMACD(self.ohlc, self.macd_f_period, self.macd_s_period, self.macd_signal)

    def macd_ind(self):
        print("MACD")
        macd_high_signal = (self.macd['Main'] > self.macd['Signal'])
        macd_low_signal = (self.macd['Main'] < self.macd['Signal'])
        self.judgment(macd_high_signal, macd_low_signal, self.macd_entry_time)


class Stoch_Signal_Create(Post_Process):

    def __init__(self):
        super().__init__()

        # Stochastic設定値
        self.stoch_kpwriod = 5  # default 5
        self.stoch_dperiod = 3  # default 3
        self.stoch_slowing = 3  # default 3
        self.stoch_upper = 70
        self.stoch_lower = 30
        self.stoch_entry_time = 5

        # インジゲータ作成
        self.stoch = iStochastic(self.ohlc, self.stoch_kpwriod, self.stoch_kpwriod, self.stoch_slowing)

        low_signal = self.low_entry_create(self.stoch_upper, self.stoch['Main'], self.stoch["Signal"])
        high_signal = self.high_entry_create(self.stoch_lower, self.stoch['Main'], self.stoch["Signal"])

        self.low_entry = self.entry_signal(low_signal, False)
        self.high_entry = self.entry_signal(high_signal, False)

    def stoch_ind(self):
        """
        self.stoch -> columns=['Main', 'Signal']
        Main = ％D
        Signal = Slow%D

        Highシグナル:Slow%D < 30% and %D ↗30
        Lowシグナル:Slow%D > 70 and %D ↘70
        """
        print("ストキャスティクス")

        self.judgment(self.high_entry, self.low_entry, self.stoch_entry_time)

    def mackay(self, rsi_high, rsi_low, sto_high, sto_low):
        high = ((rsi_high == True) & (sto_high == True))
        low = ((rsi_low == True) & (sto_low == True))
        print("mackay")
        self.judgment(high, low, self.stoch_entry_time)


class ADXW_Signal_Create(MA_Signal_Create):
    def __init__(self):
        """
        ADXWインジゲータ

        トレンド:順張り
        ボックス:エントリー禁止

        シグナル:トレンド発生時、+DI（-DI）が-DI（+DI）->Mainの順に抜ける
        トレンド判定:移動平均線 or Mainが上昇
        """
        super().__init__()
        self.adxw_period = 13
        self.adxw_entry_time = 15

        self.adxw = iADX(self.ohlc, self.adxw_period)
        """
        self.high_signal = \
            self.upper_draw_signal(self.adxw["PlusDI"], self.adxw["Main"], self.adxw["MinusDI"])

        self.low_signal = \
            self.lower_draw_signal(self.adxw["MinusDI"], self.adxw["Main"], self.adxw["PlusDI"])
        """

        high_signal_1 = self.trend_line_signal(self.adxw["PlusDI"], self.adxw["Main"], self.adxw["MinusDI"])
        high_signal_2 = self.trend_line_signal(self.adxw["Main"], self.adxw["PlusDI"])
        self.high_signal = (high_signal_1.shift(1) == high_signal_2) & (high_signal_2 == True)

        low_signal_1 = self.trend_line_signal(self.adxw["MinusDI"], self.adxw["Main"], self.adxw["PlusDI"])
        low_signal_2 = self.trend_line_signal(self.adxw["Main"], self.adxw["MinusDI"])
        self.low_signal = (low_signal_1.shift(1) == low_signal_2) & (low_signal_2 == True)

    def adxw_ind(self):
        print("ADXWilder")
        self.high_entry = self.entry_signal(self.high_signal, True)
        self.low_entry = self.entry_signal(self.low_signal, True)

        self._high_entry = (self.high_entry == self.rising_trend) & (self.high_entry == True)
        self._low_entry = (self.low_entry == self.down_trend) & (self.low_entry == True)
        self.judgment(self._high_entry, self._high_entry, self.adxw_entry_time)


def back_test():
    stoch = Stoch_Signal_Create()
    rsi = Rsi_Signal_Create()
    macd = Macd_Signal_Create()
    adxw = ADXW_Signal_Create()
    MA = MA_Signal_Create()
    """
    stoch.stoch_ind()
    rsi.rsi_ind()
    macd.macd_ind()
    """
    adxw.adxw_ind()
    MA.MA_ind()



if __name__ == '__main__':
    back_test()
