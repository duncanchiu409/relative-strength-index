import pandas as pd
import numpy as np
from copy import copy
from LocalRecord import LocalRecord

class RelativeStrengthIndex:
    def __init__(self, lookback: int, direction: int):
        self._lb = lookback
        self._direction = direction # 1 = Long only, 0 = Both, -1 = Short only
        self._pending_record = None
        self._curr_rsi = np.nan
        self._curr_gains = np.nan
        self._curr_loses = np.nan
        self.trading_records = []

    def _create_entries(self, entry_i: int, time_index: pd.DatetimeIndex, open: np.ndarray, direction: int):
        new_record = LocalRecord(entry_index=entry_i, entry_price=open[entry_i], entry_timestamp=time_index[entry_i], exit_index=-1, exit_price=np.nan, exit_timestamp=time_index[entry_i], percentage_change=np.nan, trading_type=direction)
        self._pending_record = new_record
    
    def _create_exites(self, exit_i: int, time_index: pd.DatetimeIndex, open: np.ndarray, direction: int):
        assert self._pending_record.trading_type == direction
        self._pending_record.exit_index = exit_i
        self._pending_record.exit_timestamp = time_index[exit_i]
        self._pending_record.exit_price = open[exit_i]
        self._pending_record.percentage_change = (self._pending_record.exit_price - self._pending_record.entry_price) * self._pending_record.trading_type / self._pending_record.entry_price * 100
        self.trading_records.append(copy(self._pending_record))
        self._pending_record = None

    def update(self, i: int, time_index: pd.DatetimeIndex, open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray):
        if i < self._lb-1:
            return
        elif i == self._lb-1:
            # initialize RSI
            price_changes = close[i-self._lb:i+1] - open[i-self._lb:i+1]
            gains = np.where(price_changes > 0, price_changes, 0)  # Separate gains
            losses = np.where(price_changes < 0, -price_changes, 0)  # Separate losses
            
            self._curr_gains = np.sum(gains)  # Initial average gain
            self._curr_loses = np.sum(losses)  # Initial average loss
            
            if self._curr_loses == 0:  # Prevent division by zero
                self._curr_rsi = 100
            else:
                rs = self._curr_gains / self._curr_loses
                self._curr_rsi = 100 - (100 / (1 + rs))
        else:
            # Check Entry
            if self._pending_record == None:
                if self._curr_rsi < 20 and self._direction != -1:
                    self._create_entries(i, time_index, open, 1) # Long
                elif self._curr_rsi > 80 and self._direction != 1:
                    self._create_entries(i, time_index, open, -1) # Short

            else:
                if self._curr_rsi > 80 and self._direction != -1:
                    self._create_exites(i, time_index, open, 1) # Long
                elif self._curr_rsi < 20 and self._direction != 1:
                    self._create_entries(i, time_index, open, -1) # Short

            # Update RSI
            self._curr_gains = self._curr_gains - self._curr_gains / self._lb + np.max([close[i] - open[i], 0])
            self._curr_loses = self._curr_loses - self._curr_loses / self._lb + np.max([open[i] - close[i], 0])

            if self._curr_loses == 0:  # Prevent division by zero
                self._curr_rsi = 100
            else:
                rs = self._curr_gains / self._curr_loses
                self._curr_rsi = 100 - (100 / (1 + rs))

