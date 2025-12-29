import pandas as pd
import numpy as np

#calculate rsi indicator
def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

#calculate macd indicator
def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }

#calculate simple moving averages
def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    return prices.rolling(window=period).mean()

#calculate bollinger bands
def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2) -> dict:
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return {
        'upper': upper_band,
        'middle': sma,
        'lower': lower_band
    }

#generate trading signal from indicators
def generate_signal(rsi: float, macd_hist: float, price: float, sma_20: float, sma_50: float) -> dict:
    signals = []
    strength = 0
    
    #rsi signals
    if rsi < 30:
        signals.append('rsi_oversold')
        strength += 1
    elif rsi > 70:
        signals.append('rsi_overbought')
        strength -= 1
    
    #macd signals
    if macd_hist > 0:
        signals.append('macd_bullish')
        strength += 1
    else:
        signals.append('macd_bearish')
        strength -= 1
    
    #moving average crossover
    if price > sma_20 > sma_50:
        signals.append('ma_uptrend')
        strength += 1
    elif price < sma_20 < sma_50:
        signals.append('ma_downtrend')
        strength -= 1
    
    #overall direction
    if strength >= 2:
        direction = 'bullish'
    elif strength <= -2:
        direction = 'bearish'
    else:
        direction = 'neutral'
    
    return {
        'direction': direction,
        'strength': strength,
        'signals': signals,
        'confidence': abs(strength) / 3
    }
