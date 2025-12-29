import numpy as np
import pandas as pd

#detect doji patterns from ohlc data
def analyze_candles(open_prices, close_prices, high_prices, low_prices, 
                    threshold=0.1, support_level=None):
    """
    analyzes candles to detect doji patterns
    doji = small body relative to range, indicates indecision
    
    threshold: body_size <= threshold * range
    """
    if len(open_prices) == 0:
        return {'doji': False}
    
    #get latest candle
    open_price = open_prices[-1]
    close_price = close_prices[-1]
    high_price = high_prices[-1]
    low_price = low_prices[-1]
    
    #calculate body and range
    body_size = abs(close_price - open_price)
    candle_range = high_price - low_price
    
    if candle_range == 0:
        return {'doji': False}
    
    #check if doji
    is_doji = body_size <= (threshold * candle_range)
    
    if not is_doji:
        return {'doji': False}
    
    #classify doji type
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price
    
    if lower_shadow > upper_shadow * 2:
        doji_type = 'dragonfly'  #bullish reversal
    elif upper_shadow > lower_shadow * 2:
        doji_type = 'gravestone'  #bearish reversal
    else:
        doji_type = 'neutral'
    
    #check if at support level
    at_support = False
    if support_level:
        at_support = abs(low_price - support_level) < (candle_range * 0.5)
    
    return {
        'doji': True,
        'doji_type': doji_type,
        'body_size': round(body_size, 4),
        'range': round(candle_range, 4),
        'upper_shadow': round(upper_shadow, 4),
        'lower_shadow': round(lower_shadow, 4),
        'at_support': at_support,
        'open': open_price,
        'close': close_price,
        'high': high_price,
        'low': low_price
    }

#detect hammer pattern (bullish reversal)
def detect_hammer(open_price, close_price, high_price, low_price):
    body = abs(close_price - open_price)
    lower_shadow = min(open_price, close_price) - low_price
    upper_shadow = high_price - max(open_price, close_price)
    range_size = high_price - low_price
    
    if range_size == 0:
        return False
    
    #hammer: small body, long lower shadow, tiny upper shadow
    is_hammer = (
        lower_shadow > body * 2 and
        upper_shadow < body * 0.5 and
        body < range_size * 0.3
    )
    
    return is_hammer

#detect engulfing pattern
def detect_engulfing(prev_open, prev_close, curr_open, curr_close):
    #bullish engulfing
    if prev_close < prev_open and curr_close > curr_open:
        if curr_open <= prev_close and curr_close >= prev_open:
            return 'bullish_engulfing'
    
    #bearish engulfing
    if prev_close > prev_open and curr_close < curr_open:
        if curr_open >= prev_close and curr_close <= prev_open:
            return 'bearish_engulfing'
    
    return None

#comprehensive pattern detection
def detect_all_patterns(df: pd.DataFrame) -> dict:
    if len(df) < 2:
        return {}
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    patterns = {
        'doji': analyze_candles(
            df['Open'].values,
            df['Close'].values,
            df['High'].values,
            df['Low'].values
        ),
        'hammer': detect_hammer(
            latest['Open'],
            latest['Close'],
            latest['High'],
            latest['Low']
        ),
        'engulfing': detect_engulfing(
            prev['Open'],
            prev['Close'],
            latest['Open'],
            latest['Close']
        )
    }
    
    return patterns
