import numpy as np
import pandas as pd

from vectorbt import graphics


def on_positions(posret_sr):
    """Equity on positions"""
    return (posret_sr + 1).cumprod()


def diffs(posret_sr):
    """Equity diffs on positions (absolute returns)"""
    return (on_positions(posret_sr) - on_positions(posret_sr).shift().fillna(1)).iloc[1::2]


def from_returns(rate_sr, posret_sr):
    """
    Generate equity in base and quote currency from position returns

    :param posret_sr: position returns (both short/long positions)
    :return: dataframe
    """
    quote_sr = np.cumprod(posret_sr + 1)
    quote_sr *= rate_sr.loc[posret_sr.index[0]]
    quote_sr /= rate_sr.loc[quote_sr.index]
    # Hold and cash periods
    pos_sr = pd.Series([1, -1] * (len(posret_sr.index) // 2), index=posret_sr.index)
    hold_mask = pos_sr.reindex(rate_sr.index).ffill() == 1
    hold_rates = rate_sr.loc[hold_mask]
    cash_rates = rate_sr.loc[~hold_mask]
    hold_sr = quote_sr.iloc[0::2].reindex(hold_rates.index).ffill() * hold_rates
    cash_sr = (quote_sr.iloc[1::2].reindex(cash_rates.index) * cash_rates).ffill()
    # Fill dataframe
    equity_df = hold_sr.append(cash_sr).sort_index().to_frame('base')
    equity_df['quote'] = equity_df['base'] / rate_sr
    return equity_df


def plot(rate_sr, equity_df):
    print("base")
    graphics.plot_line(equity_df['base'], benchmark=rate_sr)
    print("quote")
    graphics.plot_line(equity_df['quote'], benchmark=rate_sr * 0 + 1)
