# AI Trading Assistant

langraph-powered day trading assistant with real-time market scanning, technical analysis, and automated trade recommendations. integrates yfinance, alpha vantage, fred, and finnhub for comprehensive market data.

## system architecture

```
trading_assistant/
├── config.py              # environment and api key management
├── data_fetching.py       # yfinance, alpha vantage, fred integration
├── indicators.py          # rsi, macd, sma, bollinger bands
├── patterns.py            # doji, hammer, engulfing candlestick patterns
├── risk_management.py     # stop loss, position sizing, risk/reward
├── scanner.py             # real-time market scanner for top movers
├── agent.py               # langgraph orchestration
├── executor.py            # paper trading and order simulation
└── main.py                # main trading loop

strategies/                # custom trading strategies
backtests/                # historical backtest results
data/                     # cached market data
logs/                     # trade logs and performance
```

## what it does

**data collection:**
- fetches ohlc data from yfinance
- gets top gainers/losers from alpha vantage
- pulls economic indicators from fred
- retrieves company news from finnhub

**technical analysis:**
- rsi (14-period): overbought >70, oversold <30
- macd (12,26,9): trend and momentum
- sma crossovers (20/50): trend direction
- bollinger bands: volatility and mean reversion

**pattern recognition:**
- doji patterns: indecision, potential reversal
- hammer/inverted hammer: bullish reversal
- engulfing patterns: strong reversal signals

**signal generation:**
- combines multiple indicators for confidence score
- calculates entry price, stop loss, take profit
- assesses risk/reward ratio
- provides trade recommendations with reasoning

**real-time scanning:**
- monitors top gainers every 30 seconds
- filters by volume, price range, patterns
- alerts on high-confidence setups

## quick start

### from your notebook (original code):

```python
# 1. fetch ohlc data
info = fetch_stock_ohlc('AAPL')

# 2. transform to clean dict
clean_data = transform_ohlc_data1(info)

# 3. calculate trading thresholds
thresholds = set_trading_thresholds(clean_data)
print(thresholds)
# {'stop_loss': 147.23, 'take_profit': 153.89, ...}
```

### with complete system:

```python
from agent import create_trading_agent
from scanner import scan_market

# create agent
agent = create_trading_agent()

# scan for opportunities
opportunities = scan_market(min_confidence=0.7)

# get recommendation
result = agent.analyze_stock('AAPL', include_news=True)
print(result['recommendation'])
```

## technical indicators explained

### rsi (relative strength index)
- measures momentum on 0-100 scale
- <30 = oversold (potential buy)
- >70 = overbought (potential sell)
- 14-period standard
- best combined with price action

### macd (moving average convergence divergence)
- shows trend strength and direction
- macd line crosses above signal = bullish
- macd line crosses below signal = bearish
- histogram shows momentum strength
- good for catching early trends

### sma crossovers
- 20-period (short-term) vs 50-period (long-term)
- 20 crosses above 50 = golden cross (bullish)
- 20 crosses below 50 = death cross (bearish)
- price above both smas = strong uptrend
- simple but effective trend filter

### bollinger bands
- middle band = 20-period sma
- upper/lower = 2 standard deviations
- price touching lower band = oversold
- price touching upper band = overbought
- squeeze (narrow bands) = breakout coming
- expansion (wide bands) = high volatility

## doji pattern strategy

### what's a doji
- open and close prices nearly equal
- long wicks showing indecision
- signals potential trend reversal
- needs confirmation from next candle

### types implemented:
1. **neutral doji**: indecision, wait for confirmation
2. **dragonfly doji**: long lower wick, bullish reversal
3. **gravestone doji**: long upper wick, bearish reversal

### trading rules:
```python
# from your original code
def set_trading_thresholds(ohlc_data):
    volatility = high - low
    stop_loss = close - (volatility * 1.5)      # 1.5x risk
    take_profit = close + (volatility * 2.0)    # 2.0x reward
    bullish_entry = high + (volatility * 0.005) # break above
    bearish_entry = low - (volatility * 0.005)  # break below
```

**entry signals:**
- doji forms at support/resistance
- next candle breaks above high (bullish)
- or breaks below low (bearish)
- volume confirms breakout

**exit signals:**
- stop loss: 1.5x volatility below entry
- take profit: 2.0x volatility above entry
- risk/reward ratio: 1:1.33

## risk management

### position sizing
```python
account_size = 10000
risk_per_trade = 0.02  # 2%
max_risk = account_size * risk_per_trade  # $200

entry_price = 150
stop_loss = 147
risk_per_share = entry_price - stop_loss  # $3

position_size = max_risk / risk_per_share  # 66 shares
```

### rules enforced:
- maximum 2% risk per trade
- position size based on stop distance
- never risk more than account can afford
- minimum 1:2 risk/reward ratio

## real-time scanner

scans top gainers/losers every 30 seconds:

```python
criteria = {
    'min_volume': 1000000,      # 1M+ shares
    'min_price': 5.0,           # $5+
    'max_price': 500.0,         # under $500
    'min_volatility': 2.0,      # $2+ range
    'patterns': ['doji', 'hammer'],
    'rsi_range': (25, 35),      # oversold
}

# returns ranked opportunities
opportunities = scan_market(criteria)
```

## api usage

**alpha vantage:**
- top gainers/losers: `TOP_GAINERS_LOSERS`
- intraday data: `TIME_SERIES_INTRADAY`
- technical indicators: `RSI`, `MACD`, `SMA`
- limit: 5 calls/minute (free tier)

**yfinance:**
- historical ohlc data
- real-time quotes
- company info and fundamentals
- unlimited (unofficial api)

**fred (federal reserve):**
- economic indicators
- interest rates, gdp, unemployment
- macro context for trading decisions

**finnhub:**
- company news and sentiment
- earnings calendar
- insider transactions
- 60 calls/minute (free tier)

## example workflow

```python
# 1. morning scan
gainers = fetch_top_gainers(limit=20)

# 2. filter by criteria
filtered = [
    stock for stock in gainers
    if stock['volume'] > 1000000
    and 5 < stock['price'] < 100
]

# 3. technical analysis
for stock in filtered:
    df = fetch_ohlc(stock['symbol'], period='60d')
    
    # calculate indicators
    df['rsi'] = calculate_rsi(df['close'])
    macd = calculate_macd(df['close'])
    df['sma_20'] = calculate_sma(df['close'], 20)
    df['sma_50'] = calculate_sma(df['close'], 50)
    
    # check for patterns
    latest = df.iloc[-1]
    if is_doji(latest) and latest['rsi'] < 35:
        # potential buy setup
        thresholds = calculate_thresholds(latest)
        log_opportunity(stock['symbol'], thresholds)

# 4. monitor and execute
watch_list = get_opportunities()
for opp in watch_list:
    current_price = get_realtime_price(opp['symbol'])
    if current_price > opp['entry_price']:
        execute_trade(opp)
```

## trading signals

**bullish signals (buy):**
- rsi < 30 (oversold)
- macd histogram positive and increasing
- price crosses above sma_20
- dragonfly doji at support
- hammer pattern with volume

**bearish signals (sell):**
- rsi > 70 (overbought)
- macd histogram negative and decreasing
- price crosses below sma_20
- gravestone doji at resistance
- engulfing bearish pattern

**neutral (wait):**
- rsi between 40-60
- macd histogram near zero
- price between sma_20 and sma_50
- low volume, choppy price action

## performance tracking

```python
trade_log = {
    'symbol': 'AAPL',
    'entry_time': '2025-01-15 09:35:00',
    'entry_price': 150.25,
    'stop_loss': 147.50,
    'take_profit': 155.75,
    'exit_time': '2025-01-15 14:22:00',
    'exit_price': 155.50,
    'profit_loss': 5.25,
    'pct_return': 3.49,
    'outcome': 'win',
    'notes': 'doji breakout confirmed on volume'
}
```

**metrics calculated:**
- win rate: wins / total trades
- average win: sum(wins) / num_wins
- average loss: sum(losses) / num_losses
- profit factor: gross_profit / gross_loss
- sharpe ratio: risk-adjusted returns

## notes and gotchas

- **paper trading first**: never trade real money without backtesting
- **slippage**: actual execution price may differ from signals
- **commission costs**: subtract from profit calculations
- **market hours**: us markets 9:30am-4pm est only
- **gap risk**: overnight price changes bypass stop losses
- **api limits**: alpha vantage 5/min, finnhub 60/min
- **data delays**: yfinance has ~15min delay on free tier
- **false signals**: indicators lag price, expect whipsaws
- **overtrading**: quality over quantity, be selective

## legal disclaimer

this system is for educational purposes only. not financial advice. trading stocks involves substantial risk of loss. past performance does not guarantee future results. always paper trade before risking real capital. consult licensed financial advisors for investment decisions.

## original notebook code preserved

your original functions are implemented in:
- `fetch_stock_ohlc()` → `data_fetching.py`
- `transform_ohlc_data1()` → `data_fetching.py`
- `set_trading_thresholds()` → `risk_management.py`

all your threshold calculations (stop loss, take profit, entry prices) are maintained with the same risk/reward ratios you defined.

## next steps

1. backtest doji strategy on historical data
2. implement real broker api (alpaca, interactive brokers)
3. add machine learning price predictions
4. build web dashboard for monitoring
5. create alerts system (email/sms/discord)
6. optimize indicator parameters
7. add more candlestick patterns
8. implement options strategies

## resources

- technical analysis: https://www.investopedia.com/technical-analysis
- candlestick patterns: https://www.candlesticker.com/
- risk management: https://www.babypips.com/learn/forex/money-management
- alpha vantage docs: https://www.alphavantage.co/documentation/
- yfinance: https://pypi.org/project/yfinance/
