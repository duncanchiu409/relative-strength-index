import numpy as np
import pandas as pd
from dataclasses import dataclass

@dataclass
class LocalRecord:
    entry_index: int
    entry_price: float
    entry_timestamp: pd.Timestamp

    exit_index: int
    exit_price: float
    exit_timestamp: pd.Timestamp

    trading_type: int
    percentage_change: float

def calculate_equity_curve(records_df: pd.DataFrame, equity_curve: pd.Series) -> pd.DataFrame:
    # Zero out values after last trade
    if len(records_df) > 0:
        equity_curve[0:records_df['entry_index'][0]] = 0
        equity_curve[records_df['exit_index'].iloc[-1]:] = 0
    else:
        return pd.Series([])
    
    # Zero out values between trades
    for i in range(len(records_df) - 1):
        current_exit = records_df['exit_index'][i]
        next_entry = records_df['entry_index'][i + 1]
        equity_curve[current_exit:next_entry] = 0
        
    return equity_curve.cumsum()

def sanity_check():
    return