import time
from datetime import datetime
from data_fetching import fetch_top_gainers, fetch_historical_data
from patterns import detect_all_patterns
from indicators import calculate_rsi, generate_signal
from risk_management import set_trading_thresholds
import pandas as pd

#real-time market scanner
def scan_market(api_key: str, min_volume: int = 1000000, 
               min_price: float = 5.0, max_price: float = 500.0,
               min_confidence: float = 0.6) -> list:
    
    print(f"\nscanning market at {datetime.now().strftime('%H:%M:%S')}")
    
    #fetch top gainers
    gainers = fetch_top_gainers(api_key, limit=20)
    
    if not gainers:
        print("no gainers found")
        return []
    
    opportunities = []
    
    for stock in gainers:
        symbol = stock['symbol']
        price = stock['price']
        volume = stock['volume']
        
        #filter by criteria
        if volume < min_volume:
            continue
        if price < min_price or price > max_price:
            continue
        
        #fetch historical data
        df = fetch_historical_data(symbol, period='60d')
        
        if df.empty or len(df) < 20:
            continue
        
        #detect patterns
        patterns = detect_all_patterns(df)
        
        #calculate rsi
        df['rsi'] = calculate_rsi(df['Close'])
        latest_rsi = df['rsi'].iloc[-1]
        
        #check for doji at oversold
        if patterns.get('doji', {}).get('doji'):
            doji_type = patterns['doji']['doji_type']
            
            if doji_type == 'dragonfly' and latest_rsi < 35:
                #bullish setup
                latest = df.iloc[-1]
                clean_data = {
                    'open': latest['Open'],
                    'high': latest['High'],
                    'low': latest['Low'],
                    'close': latest['Close']
                }
                
                thresholds = set_trading_thresholds(clean_data)
                
                opportunities.append({
                    'symbol': symbol,
                    'price': price,
                    'volume': volume,
                    'pattern': 'dragonfly_doji',
                    'rsi': round(latest_rsi, 2),
                    'confidence': 0.8,
                    'entry': thresholds['bullish_entry_price'],
                    'stop_loss': thresholds['stop_loss'],
                    'take_profit': thresholds['take_profit'],
                    'risk_reward': thresholds['risk_reward_ratio']
                })
                
                print(f"  {symbol}: dragonfly doji + oversold rsi")
        
        #check for hammer
        if patterns.get('hammer') and latest_rsi < 40:
            latest = df.iloc[-1]
            clean_data = {
                'open': latest['Open'],
                'high': latest['High'],
                'low': latest['Low'],
                'close': latest['Close']
            }
            
            thresholds = set_trading_thresholds(clean_data)
            
            opportunities.append({
                'symbol': symbol,
                'price': price,
                'volume': volume,
                'pattern': 'hammer',
                'rsi': round(latest_rsi, 2),
                'confidence': 0.7,
                'entry': thresholds['bullish_entry_price'],
                'stop_loss': thresholds['stop_loss'],
                'take_profit': thresholds['take_profit'],
                'risk_reward': thresholds['risk_reward_ratio']
            })
            
            print(f"  {symbol}: hammer + rsi {latest_rsi:.1f}")
    
    #sort by confidence
    opportunities.sort(key=lambda x: x['confidence'], reverse=True)
    
    print(f"\nfound {len(opportunities)} opportunities")
    return opportunities

#continuous scanning loop
def stream_scan_realtime(api_key: str, interval: int = 30, max_iterations: int = None):
    iteration = 0
    
    print(f"starting continuous scan (interval: {interval}s)")
    
    while True:
        opportunities = scan_market(api_key)
        
        if opportunities:
            print(f"\ntop opportunity: {opportunities[0]['symbol']}")
            print(f"  pattern: {opportunities[0]['pattern']}")
            print(f"  entry: ${opportunities[0]['entry']}")
            print(f"  stop: ${opportunities[0]['stop_loss']}")
            print(f"  target: ${opportunities[0]['take_profit']}")
            print(f"  r/r: {opportunities[0]['risk_reward']}:1")
        
        iteration += 1
        if max_iterations and iteration >= max_iterations:
            break
        
        time.sleep(interval)
