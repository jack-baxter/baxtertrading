import yfinance as yf
import pandas as pd
import requests
import os
from datetime import datetime, timedelta

#fetch stock ohlc data (from your original notebook)
def fetch_stock_ohlc(symbol: str) -> dict:
    try:
        stock_data = yf.download(symbol, period="1d", progress=False)
        if stock_data.empty:
            return {"error": f"no data found for symbol '{symbol}'"}
        
        latest_data = stock_data.iloc[-1]
        return {
            "open": latest_data["Open"],
            "high": latest_data["High"],
            "low": latest_data["Low"],
            "close": latest_data["Close"]
        }
    except Exception as e:
        return {"error": str(e)}

#transform ohlc data to clean dict (from your original notebook)
def transform_ohlc_data1(ohlc_data: dict, decimals: int = 4) -> dict:
    ticker = list(ohlc_data['open'].index)[0] if hasattr(ohlc_data['open'], 'index') else None
    
    if ticker:
        return {key: round(float(ohlc_data[key][ticker]), decimals) for key in ohlc_data}
    else:
        return {key: round(float(ohlc_data[key]), decimals) for key in ohlc_data if key != 'error'}

#fetch historical data for technical analysis
def fetch_historical_data(symbol: str, period: str = "60d", interval: str = "1d") -> pd.DataFrame:
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        if df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        print(f"error fetching historical data: {e}")
        return pd.DataFrame()

#fetch top gainers from alpha vantage
def fetch_top_gainers(api_key: str, limit: int = 20) -> list:
    url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        gainers = data.get('top_gainers', [])[:limit]
        
        results = []
        for gainer in gainers:
            results.append({
                'symbol': gainer.get('ticker'),
                'price': float(gainer.get('price', 0)),
                'change_pct': float(gainer.get('change_percentage', '0').replace('%', '')),
                'volume': int(gainer.get('volume', 0))
            })
        
        return results
    
    except Exception as e:
        print(f"error fetching top gainers: {e}")
        return []

#fetch real-time quote
def fetch_realtime_quote(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'volume': info.get('volume', 0),
            'market_cap': info.get('marketCap', 0),
            'bid': info.get('bid', 0),
            'ask': info.get('ask', 0)
        }
    except Exception as e:
        return {'symbol': symbol, 'error': str(e)}

#fetch company news from finnhub
def fetch_company_news(symbol: str, api_key: str, days: int = 7) -> list:
    end = datetime.now()
    start = end - timedelta(days=days)
    
    url = f"https://finnhub.io/api/v1/company-news"
    params = {
        'symbol': symbol,
        'from': start.strftime('%Y-%m-%d'),
        'to': end.strftime('%Y-%m-%d'),
        'token': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        news = response.json()
        
        return [
            {
                'headline': item.get('headline'),
                'summary': item.get('summary'),
                'source': item.get('source'),
                'url': item.get('url'),
                'datetime': item.get('datetime')
            }
            for item in news[:10]
        ]
    except Exception as e:
        print(f"error fetching news: {e}")
        return []
