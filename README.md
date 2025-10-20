# 📊 Live Trading Analysis System

Smart IRA trading analysis tool with AI-powered insights, sector screening, and multi-timeframe predictions.

## 🎯 Features

- **3-Button Interface**: UPDATE → ANALYZE → RESULTS
- **Multi-Sector Analysis**: Screen top 50 stocks across 10 sectors
- **Technical Analysis**: Momentum, Trend, Volume, Volatility, RSI
- **Candlestick Patterns**: Hammer, Engulfing, Doji, Morning/Evening Star, etc.
- **News Sentiment**: Analyzes recent headlines for each stock
- **Price Predictions**: Today, Tomorrow, 1 Week, 1 Month targets
- **Position Sizing**: Automatic calculation based on your capital
- **Risk Management**: Stop loss and take profit recommendations
- **Market Regime Detection**: Adapts to bull/bear/sideways markets
- **iPad Optimized**: Beautiful responsive interface

## 🚀 Quick Start

### 1. Local Testing (Your Computer)

```bash
# Install Python 3.8+ if not already installed

# Clone or download this repository
cd trading-system

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

# Open in browser
http://localhost:5000
```

### 2. Deploy to Render.com (Recommended for iPad Access)

**Why Render?**
- ✅ Free tier available
- ✅ Auto-deploys from GitHub
- ✅ Runs 24/7
- ✅ Gets you a public URL for iPad access
- ✅ Easy setup

## 📱 How to Use

### Button 1: UPDATE
- Refreshes your configuration
- Updates stock lists
- Syncs latest settings

### Button 2: ANALYZE
- Scans all enabled sectors
- Runs technical analysis
- Detects patterns and sentiment
- Generates predictions
- Takes 2-5 minutes depending on sectors enabled

### Button 3: RESULTS
- Shows top trading opportunities ranked by score
- Displays price targets for multiple timeframes
- Provides detailed reasoning for each recommendation
- Shows position sizing based on your capital

### Settings Panel
- **Capital**: Your total investment amount ($2,400 default)
- **Position Size**: % of capital per trade (10% default = $240 per stock)
- **Stop Loss**: % below entry to cut losses (5% default)
- **Take Profit**: % above entry to take profits (10% default)
- **Top Opportunities**: How many stocks to show (20 default)
- **Min Score**: Minimum score threshold (50 default)
- **Sectors**: Enable/disable specific sectors

## 🎓 Understanding the Analysis

### Score (0-100)
- **70+**: Strong opportunity
- **50-70**: Moderate opportunity
- **<50**: Weak opportunity

### Actions
- **BUY**: Strong bullish signals, good entry point
- **SELL**: Bearish signals or overbought
- **HOLD**: Neutral, wait for clearer setup

### RSI (Relative Strength Index)
- **<30**: Oversold (potential buying opportunity)
- **30-70**: Normal range
- **>70**: Overbought (potential selling opportunity)

### Patterns
- **Bullish**: Hammer, Bullish Engulfing, Morning Star
- **Bearish**: Shooting Star, Bearish Engulfing, Evening Star
- **Neutral**: Doji (indecision)

## ⚙️ Configuration

Edit `trading_config.json` directly or use the web interface:

```json
{
  "capital": 2400,
  "position_size_pct": 10,
  "stop_loss_pct": 5,
  "take_profit_pct": 10,
  "enabled_sectors": ["Technology", "Healthcare", "Financial"],
  "top_opportunities": 20,
  "min_score": 50
}
```

## 🏗️ Architecture

```
trading_system.py    - Core analysis engine
app.py              - Flask web server
requirements.txt    - Python dependencies
trading_config.json - User settings (auto-created)
```

## 📊 Available Sectors

1. **Technology**: AAPL, MSFT, NVDA, AVGO, etc.
2. **Healthcare**: UNH, LLY, JNJ, ABBV, etc.
3. **Financial**: BRK.B, JPM, V, MA, BAC, etc.
4. **Consumer Cyclical**: AMZN, TSLA, HD, MCD, etc.
5. **Consumer Defensive**: PG, KO, PEP, COST, etc.
6. **Energy**: XOM, CVX, COP, SLB, etc.
7. **Industrials**: UPS, CAT, RTX, BA, etc.
8. **Materials**: LIN, APD, SHW, ECL, etc.
9. **Real Estate**: PLD, AMT, EQIX, PSA, etc.
10. **Utilities**: NEE, SO, DUK, CEG, etc.

## ⚠️ Important Disclaimers

### IRA Trading Rules
- **Pattern Day Trading**: Avoid 4+ trades in 5 days
- **Settlement**: Wait for trades to settle (T+2)
- **Free Riding**: Don't buy/sell same stock before payment settles
- This tool is for **swing trading** (holding 3+ days), NOT day trading

### Trading Risks
- **No Guarantees**: Past performance ≠ future results
- **You Can Lose Money**: Only trade what you can afford to lose
- **Not Financial Advice**: This is a tool, not a financial advisor
- **Do Your Research**: Always verify before trading
- **Paper Trade First**: Test strategies before risking real money

### Realistic Expectations
- **Good Annual Return**: 10-25%
- **Viable Win Rate**: 55-65%
- **Bad Expectation**: Getting rich quick or guaranteed daily profits

## 🔧 Troubleshooting

### "No module named 'yfinance'"
```bash
pip install -r requirements.txt
```

### "Analysis taking too long"
- Disable some sectors in settings
- Reduce "Top Opportunities" number
- Yahoo Finance API sometimes rate limits

### "Can't access from iPad"
- Make sure you deployed to Render.com or similar
- Check firewall settings if running locally
- Use network IP instead of localhost

## 📈 Tips for Success

1. **Start Small**: Begin with paper trading or small positions
2. **Diversify**: Don't put all capital in one stock
3. **Set Alerts**: Use your broker's alert system for target prices
4. **Be Patient**: Wait for high-score opportunities (70+)
5. **Follow Your Plan**: Don't chase trades outside your settings
6. **Check News**: Verify major news isn't missing from sentiment
7. **Track Performance**: Keep a trading journal

## 🤝 Support

For issues or questions:
- Check the code comments for detailed explanations
- Review the backtesting version in `backtest.py`
- Test with paper money first!

## 📜 License

This is a personal trading tool. Use at your own risk.

---

**Built with**: Python, Flask, yfinance, pandas, numpy
**Best used for**: IRA swing trading (3-7 day holds)
**Not for**: Day trading or guaranteed profits 😊
