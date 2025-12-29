#!/usr/bin/env python3

from data_fetching import fetch_stock_ohlc, transform_ohlc_data1, fetch_historical_data
from indicators import calculate_rsi, calculate_macd, calculate_sma, generate_signal
from risk_management import set_trading_thresholds, calculate_position_size, validate_trade
import warnings
warnings.filterwarnings("ignore")

def analyze_stock(symbol: str, account_size: float = 10000, risk_percent: float = 2.0):
    print(f"\n{'='*60}")
    print(f"analyzing {symbol}")
    print(f"{'='*60}")
    
    #fetch current ohlc data (your original code)
    print("\nfetching ohlc data...")
    info = fetch_stock_ohlc(symbol)
    
    if 'error' in info:
        print(f"error: {info['error']}")
        return
    
    #transform to clean dict (your original code)
    clean_data = transform_ohlc_data1(info)
    print(f"current price: ${clean_data['close']}")
    print(f"range: ${clean_data['low']} - ${clean_data['high']}")
    
    #calculate trading thresholds (your original code)
    print("\ncalculating thresholds...")
    thresholds = set_trading_thresholds(clean_data)
    
    print(f"volatility: ${thresholds['volatility']}")
    print(f"stop loss: ${thresholds['stop_loss']}")
    print(f"take profit: ${thresholds['take_profit']}")
    print(f"risk/reward: {thresholds['risk_reward_ratio']}:1")
    
    #fetch historical data for technical analysis
    print("\nfetching historical data...")
    df = fetch_historical_data(symbol, period='60d')
    
    if df.empty:
        print("no historical data available")
        return
    
    #calculate indicators
    print("\ncalculating technical indicators...")
    df['rsi'] = calculate_rsi(df['Close'])
    macd = calculate_macd(df['Close'])
    df['macd'] = macd['macd']
    df['macd_signal'] = macd['signal']
    df['macd_hist'] = macd['histogram']
    df['sma_20'] = calculate_sma(df['Close'], 20)
    df['sma_50'] = calculate_sma(df['Close'], 50)
    
    #get latest values
    latest = df.iloc[-1]
    
    print(f"rsi: {latest['rsi']:.2f}")
    print(f"macd histogram: {latest['macd_hist']:.4f}")
    print(f"sma 20: ${latest['sma_20']:.2f}")
    print(f"sma 50: ${latest['sma_50']:.2f}")
    
    #generate trading signal
    print("\ngenerating signal...")
    signal = generate_signal(
        latest['rsi'],
        latest['macd_hist'],
        clean_data['close'],
        latest['sma_20'],
        latest['sma_50']
    )
    
    print(f"direction: {signal['direction']}")
    print(f"strength: {signal['strength']}/3")
    print(f"confidence: {signal['confidence']*100:.1f}%")
    print(f"signals: {', '.join(signal['signals'])}")
    
    #calculate position size
    print("\ncalculating position size...")
    
    if signal['direction'] == 'bullish':
        entry = thresholds['bullish_entry_price']
        stop = thresholds['stop_loss']
        target = thresholds['take_profit']
    elif signal['direction'] == 'bearish':
        entry = thresholds['bearish_entry_price']
        stop = thresholds['take_profit']
        target = thresholds['stop_loss']
    else:
        print("\nno trade recommended (neutral signal)")
        return
    
    #validate trade
    validation = validate_trade(entry, stop, target)
    
    if not validation['valid']:
        print(f"\ntrade rejected: {validation['reason']}")
        return
    
    #calculate position
    position = calculate_position_size(account_size, risk_percent, entry, stop)
    
    print(f"\nposition size: {position['shares']} shares")
    print(f"position value: ${position['position_value']}")
    print(f"max risk: ${position['max_risk']} ({risk_percent}% of account)")
    
    #final recommendation
    print(f"\n{'='*60}")
    print(f"recommendation: {signal['direction'].upper()}")
    print(f"{'='*60}")
    print(f"entry: ${entry}")
    print(f"stop loss: ${stop}")
    print(f"take profit: ${target}")
    print(f"risk/reward: {validation['risk_reward']}:1")
    print(f"confidence: {signal['confidence']*100:.1f}%")
    print(f"{'='*60}\n")

#example usage
def main():
    #analyze single stock (your original workflow)
    analyze_stock('AAPL', account_size=10000, risk_percent=2.0)
    
    #analyze multiple stocks
    # symbols = ['AAPL', 'MSFT', 'TSLA', 'NVDA']
    # for symbol in symbols:
    #     analyze_stock(symbol)

if __name__ == "__main__":
    main()
