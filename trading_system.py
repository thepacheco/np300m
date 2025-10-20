"""
LIVE TRADING ANALYSIS SYSTEM
Enhanced version built on backtest.py foundation
Adds: Predictions, Live Data, Sector Analysis, News Sentiment, Candlestick Patterns

pip install yfinance pandas numpy scipy flask flask-cors scikit-learn ta-lib newsapi-python requests beautifulsoup4 lxml
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# SECTOR DEFINITIONS - Top 50 stocks per sector
# ============================================================================

SECTORS = {
    'Technology': [
        'AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL', 'ADBE', 'CRM', 'AMD', 'CSCO', 'ACN',
        'TXN', 'QCOM', 'INTC', 'INTU', 'NOW', 'IBM', 'AMAT', 'MU', 'ADI', 'LRCX',
        'KLAC', 'SNPS', 'CDNS', 'MCHP', 'FTNT', 'PANW', 'CRWD', 'WDAY', 'TEAM', 'DDOG',
        'ZS', 'SNOW', 'NET', 'OKTA', 'DELL', 'HPQ', 'NTAP', 'STX', 'WDC', 'ON',
        'SWKS', 'NXPI', 'MRVL', 'MPWR', 'ENPH', 'SEDG', 'WOLF', 'FSLR', 'RUN', 'SMCI'
    ],
    'Healthcare': [
        'UNH', 'LLY', 'JNJ', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'AMGN',
        'BMY', 'ELV', 'CVS', 'MDT', 'GILD', 'CI', 'REGN', 'ISRG', 'VRTX', 'HCA',
        'BSX', 'ZTS', 'MCK', 'MRNA', 'SYK', 'BDX', 'EW', 'HUM', 'A', 'IDXX',
        'IQV', 'RMD', 'DXCM', 'CNC', 'COO', 'BIIB', 'ALGN', 'MTD', 'WST', 'HOLX',
        'PODD', 'TECH', 'INCY', 'EXAS', 'VTRS', 'MOH', 'DVA', 'HSIC', 'BAX', 'CTLT'
    ],
    'Financial': [
        'BRK.B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS', 'SPGI', 'AXP',
        'BLK', 'C', 'SCHW', 'CB', 'MMC', 'PGR', 'ICE', 'CME', 'AON', 'USB',
        'TFC', 'PNC', 'AIG', 'AFL', 'MET', 'ALL', 'PRU', 'TRV', 'AJG', 'MSCI',
        'BK', 'COF', 'DFS', 'TROW', 'BEN', 'NTRS', 'STT', 'WRB', 'CINF', 'L',
        'GL', 'AMP', 'AIZ', 'RJF', 'JKHY', 'CBOE', 'NDAQ', 'IVZ', 'MKTX', 'FDS'
    ],
    'Consumer_Cyclical': [
        'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'LOW', 'SBUX', 'TJX', 'BKNG', 'CMG',
        'MAR', 'ABNB', 'GM', 'F', 'HLT', 'ORLY', 'AZO', 'YUM', 'ROST', 'DHI',
        'LEN', 'RCL', 'CCL', 'NCLH', 'LVS', 'WYNN', 'MGM', 'POOL', 'DRI', 'QSR',
        'DPZ', 'ULTA', 'BBY', 'TSCO', 'GPC', 'AAP', 'KMX', 'AN', 'LAD', 'PAG',
        'AZO', 'WSM', 'DKS', 'FIVE', 'BURL', 'OLLI', 'BJ', 'COST', 'WMT', 'TGT'
    ],
    'Consumer_Defensive': [
        'PG', 'KO', 'PEP', 'COST', 'WMT', 'PM', 'MO', 'MDLZ', 'CL', 'GIS',
        'KMB', 'K', 'STZ', 'HSY', 'CPB', 'CAG', 'SJM', 'HRL', 'MKC', 'CHD',
        'CLX', 'TSN', 'TAP', 'BG', 'LW', 'POST', 'CPB', 'INGR', 'LANC', 'JBSS',
        'KDP', 'MNST', 'CELH', 'KR', 'SYY', 'USFD', 'PFGC', 'UNFI', 'SPTN', 'GO',
        'EL', 'COTY', 'KHC', 'SMPL', 'HAIN', 'BGS', 'FLO', 'SAM', 'FIZZ', 'COKE'
    ],
    'Energy': [
        'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'WMB', 'OXY',
        'HES', 'KMI', 'BKR', 'HAL', 'DVN', 'FANG', 'TRGP', 'EQT', 'LNG', 'OKE',
        'MRO', 'CTRA', 'APA', 'CHK', 'MTDR', 'PR', 'NOG', 'RRC', 'AR', 'SM',
        'MGY', 'CRK', 'CIVI', 'VTLE', 'NOV', 'HP', 'RIG', 'VAL', 'PTEN', 'LBRT',
        'TDW', 'WHD', 'WTTR', 'NINE', 'NBR', 'CLB', 'PUMP', 'ACDC', 'NE', 'REI'
    ],
    'Industrials': [
        'UPS', 'CAT', 'RTX', 'BA', 'HON', 'UNP', 'GE', 'LMT', 'DE', 'MMM',
        'ETN', 'ITW', 'CSX', 'WM', 'NSC', 'EMR', 'GD', 'NOC', 'CARR', 'PCAR',
        'TDG', 'JCI', 'FDX', 'PH', 'OTIS', 'CTAS', 'CMI', 'EMR', 'ROK', 'AME',
        'FAST', 'VRSK', 'ODFL', 'IR', 'SNA', 'DAL', 'UAL', 'LUV', 'AAL', 'JBLU',
        'WCN', 'RSG', 'URI', 'PWR', 'J', 'HUBB', 'BLDR', 'FTV', 'XYL', 'IEX'
    ],
    'Materials': [
        'LIN', 'APD', 'SHW', 'ECL', 'FCX', 'NEM', 'CTVA', 'DD', 'NUE', 'DOW',
        'VMC', 'MLM', 'PPG', 'STLD', 'CF', 'MOS', 'ALB', 'EMN', 'FMC', 'IFF',
        'CE', 'BALL', 'AVY', 'AMCR', 'PKG', 'IP', 'SEE', 'WRK', 'CCK', 'SON',
        'SLGN', 'SMG', 'HWKN', 'KWR', 'SCCO', 'HUN', 'NEU', 'OLN', 'RGLD', 'WPM',
        'AEM', 'GOLD', 'FNV', 'AGI', 'HL', 'CDE', 'PAAS', 'EGO', 'KGC', 'BTG'
    ],
    'Real_Estate': [
        'PLD', 'AMT', 'EQIX', 'PSA', 'CCI', 'WELL', 'DLR', 'O', 'CBRE', 'SPG',
        'AVB', 'EQR', 'VICI', 'VTR', 'EXR', 'SBAC', 'WY', 'INVH', 'ARE', 'MAA',
        'ESS', 'KIM', 'DOC', 'UDR', 'CPT', 'HST', 'REG', 'BXP', 'FRT', 'VNO',
        'SLG', 'PEAK', 'AIV', 'AMH', 'IRM', 'CUBE', 'LSI', 'ELS', 'SUI', 'REXR',
        'FR', 'STAG', 'TRNO', 'NSA', 'PSB', 'PLYM', 'SAFE', 'DEI', 'CUZ', 'ALEX'
    ],
    'Utilities': [
        'NEE', 'SO', 'DUK', 'CEG', 'SRE', 'AEP', 'D', 'PCG', 'EXC', 'XEL',
        'ED', 'WEC', 'ES', 'AWK', 'DTE', 'PPL', 'EIX', 'AEE', 'FE', 'CMS',
        'CNP', 'ETR', 'ATO', 'PEG', 'NI', 'LNT', 'EVRG', 'AES', 'VST', 'NRG',
        'PNW', 'OGE', 'IDA', 'SWX', 'SR', 'MDU', 'AVA', 'AGR', 'OTTR', 'NWE',
        'CPK', 'UGI', 'BKH', 'NWN', 'SJW', 'MSEX', 'YORW', 'AWR', 'CWT', 'WTRG'
    ]
}

# ============================================================================
# REGIME DETECTOR (from your backtest.py)
# ============================================================================

class RegimeDetector:
    """Detect market regime from SPY data"""
    
    @staticmethod
    def detect_regime(spy_data: pd.DataFrame) -> dict:
        if len(spy_data) < 100:
            return {'regime': 'unknown', 'confidence': 0, 'volatility': 0}
        
        price = float(spy_data['Close'].iloc[-1])
        ma20 = float(spy_data['Close'].rolling(20).mean().iloc[-1])
        ma50 = float(spy_data['Close'].rolling(50).mean().iloc[-1])
        ma100 = float(spy_data['Close'].rolling(100).mean().iloc[-1])
        
        returns = spy_data['Close'].pct_change()
        vol20 = float(returns.rolling(20).std().iloc[-1] * np.sqrt(252))
        
        mom_3m = float((price / spy_data['Close'].iloc[-60] - 1)) if len(spy_data) >= 60 else 0.0
        
        if price > ma20 > ma50 > ma100 and mom_3m > 0.05:
            regime = 'strong_bull'
        elif price > ma50 and mom_3m > 0:
            regime = 'bull'
        elif price < ma20 < ma50 < ma100 and mom_3m < -0.05:
            regime = 'strong_bear'
        elif price < ma50 and mom_3m < 0:
            regime = 'bear'
        elif vol20 > 0.30:
            regime = 'volatile'
        else:
            regime = 'sideways'
        
        return {'regime': regime, 'volatility': vol20}

# ============================================================================
# MULTI-FACTOR ANALYZER (from your backtest.py + enhancements)
# ============================================================================

class MultiFactorAnalyzer:
    """Multi-factor analysis with enhancements"""
    
    @staticmethod
    def calculate_factors(data: pd.DataFrame, symbol: str) -> dict:
        if len(data) < 60:
            return None
        
        try:
            price = float(data['Close'].iloc[-1])
            returns = data['Close'].pct_change()
            
            # Momentum
            mom_1m = float((price / data['Close'].iloc[-20] - 1)) if len(data) >= 20 else 0.0
            mom_3m = float((price / data['Close'].iloc[-60] - 1)) if len(data) >= 60 else 0.0
            
            # Volatility
            vol_20d = float(returns.rolling(20).std().iloc[-1] * np.sqrt(252))
            
            # Trend
            ma10 = float(data['Close'].rolling(10).mean().iloc[-1])
            ma20 = float(data['Close'].rolling(20).mean().iloc[-1])
            ma50 = float(data['Close'].rolling(50).mean().iloc[-1])
            
            trend_score = 0
            if price > ma10: trend_score += 1
            if price > ma20: trend_score += 1
            if price > ma50: trend_score += 1
            if ma10 > ma20: trend_score += 1
            if ma20 > ma50: trend_score += 1
            trend_score = trend_score / 5.0
            
            # Volume
            avg_volume = float(data['Volume'].tail(20).mean())
            recent_volume = float(data['Volume'].iloc[-1])
            volume_surge = recent_volume / avg_volume if avg_volume > 0 else 1.0
            
            # RSI calculation
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
            
            # MACD calculation
            ema12 = data['Close'].ewm(span=12, adjust=False).mean()
            ema26 = data['Close'].ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_histogram = macd_line - signal_line
            
            current_macd = float(macd_line.iloc[-1])
            current_signal = float(signal_line.iloc[-1])
            current_histogram = float(macd_histogram.iloc[-1])
            macd_crossover = 'bullish' if current_macd > current_signal and macd_histogram.iloc[-2] <= 0 else \
                            'bearish' if current_macd < current_signal and macd_histogram.iloc[-2] >= 0 else \
                            'neutral'
            
            # Bollinger Bands calculation
            bb_period = 20
            bb_std = 2
            bb_middle = data['Close'].rolling(window=bb_period).mean()
            bb_std_dev = data['Close'].rolling(window=bb_period).std()
            bb_upper = bb_middle + (bb_std_dev * bb_std)
            bb_lower = bb_middle - (bb_std_dev * bb_std)
            
            current_bb_upper = float(bb_upper.iloc[-1])
            current_bb_middle = float(bb_middle.iloc[-1])
            current_bb_lower = float(bb_lower.iloc[-1])
            bb_position = ((price - current_bb_lower) / (current_bb_upper - current_bb_lower)) * 100
            
            bb_signal = 'oversold' if bb_position < 20 else \
                       'overbought' if bb_position > 80 else \
                       'neutral'
            
            # Support/Resistance levels
            high_52w = float(data['High'].tail(252).max()) if len(data) >= 252 else float(data['High'].max())
            low_52w = float(data['Low'].tail(252).min()) if len(data) >= 252 else float(data['Low'].min())
            
            # Calculate scores
            momentum_score = 50 + (mom_1m * 100)
            volatility_score = max(0, min(100, 100 - vol_20d * 100))
            trend_score_final = trend_score * 100
            volume_score = min(100, max(0, 50 + (volume_surge - 1) * 50))
            
            return {
                'momentum': {
                    '1m': mom_1m,
                    '3m': mom_3m,
                    'score': momentum_score
                },
                'volatility': {
                    '20d': vol_20d,
                    'score': volatility_score
                },
                'trend': {
                    'score': trend_score_final,
                    'ma10': ma10,
                    'ma20': ma20,
                    'ma50': ma50
                },
                'volume': {
                    'surge': volume_surge,
                    'score': volume_score
                },
                'rsi': current_rsi,
                'macd': {
                    'value': current_macd,
                    'signal': current_signal,
                    'histogram': current_histogram,
                    'crossover': macd_crossover
                },
                'bollinger': {
                    'upper': current_bb_upper,
                    'middle': current_bb_middle,
                    'lower': current_bb_lower,
                    'position': bb_position,
                    'signal': bb_signal
                },
                'price_levels': {
                    'current': price,
                    'high_52w': high_52w,
                    'low_52w': low_52w,
                    'distance_from_high': ((price - high_52w) / high_52w) * 100,
                    'distance_from_low': ((price - low_52w) / low_52w) * 100
                }
            }
        except Exception as e:
            print(f"Error calculating factors for {symbol}: {e}")
            return None
    
    @staticmethod
    def composite_score(factors: dict, regime: str) -> float:
        if not factors:
            return 0
        
        weights = {
            'momentum': 0.35,
            'volatility': 0.20,
            'trend': 0.30,
            'volume': 0.15
        }
        
        # Adjust for regime
        if regime in ['strong_bull', 'bull']:
            weights['momentum'] = 0.45
            weights['trend'] = 0.30
        elif regime in ['strong_bear', 'bear']:
            weights['volatility'] = 0.35
            weights['momentum'] = 0.20
        
        score = sum(factors[f]['score'] * w for f, w in weights.items())
        return score

# ============================================================================
# CANDLESTICK PATTERN DETECTOR
# ============================================================================

class CandlestickPatternDetector:
    """Detect candlestick patterns"""
    
    @staticmethod
    def detect_patterns(data: pd.DataFrame) -> list:
        patterns = []
        
        if len(data) < 3:
            return patterns
        
        # Get last 3 candles
        c0 = data.iloc[-1]  # Current
        c1 = data.iloc[-2]  # Previous
        c2 = data.iloc[-3]  # 2 days ago
        
        # Bullish patterns
        if CandlestickPatternDetector._is_hammer(c0):
            patterns.append({'pattern': 'Hammer', 'signal': 'bullish', 'strength': 'medium'})
        
        if CandlestickPatternDetector._is_bullish_engulfing(c1, c0):
            patterns.append({'pattern': 'Bullish Engulfing', 'signal': 'bullish', 'strength': 'strong'})
        
        if CandlestickPatternDetector._is_morning_star(c2, c1, c0):
            patterns.append({'pattern': 'Morning Star', 'signal': 'bullish', 'strength': 'strong'})
        
        # Bearish patterns
        if CandlestickPatternDetector._is_shooting_star(c0):
            patterns.append({'pattern': 'Shooting Star', 'signal': 'bearish', 'strength': 'medium'})
        
        if CandlestickPatternDetector._is_bearish_engulfing(c1, c0):
            patterns.append({'pattern': 'Bearish Engulfing', 'signal': 'bearish', 'strength': 'strong'})
        
        if CandlestickPatternDetector._is_evening_star(c2, c1, c0):
            patterns.append({'pattern': 'Evening Star', 'signal': 'bearish', 'strength': 'strong'})
        
        # Neutral patterns
        if CandlestickPatternDetector._is_doji(c0):
            patterns.append({'pattern': 'Doji', 'signal': 'neutral', 'strength': 'weak'})
        
        return patterns
    
    @staticmethod
    def _is_hammer(candle):
        body = abs(candle['Close'] - candle['Open'])
        lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
        upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
        
        return (lower_shadow > body * 2 and 
                upper_shadow < body * 0.3 and
                candle['Close'] > candle['Open'])
    
    @staticmethod
    def _is_shooting_star(candle):
        body = abs(candle['Close'] - candle['Open'])
        upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
        lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
        
        return (upper_shadow > body * 2 and 
                lower_shadow < body * 0.3 and
                candle['Close'] < candle['Open'])
    
    @staticmethod
    def _is_doji(candle):
        body = abs(candle['Close'] - candle['Open'])
        total_range = candle['High'] - candle['Low']
        
        return body < total_range * 0.1 if total_range > 0 else False
    
    @staticmethod
    def _is_bullish_engulfing(prev, curr):
        return (prev['Close'] < prev['Open'] and  # Previous red
                curr['Close'] > curr['Open'] and  # Current green
                curr['Open'] < prev['Close'] and  # Opens below prev close
                curr['Close'] > prev['Open'])     # Closes above prev open
    
    @staticmethod
    def _is_bearish_engulfing(prev, curr):
        return (prev['Close'] > prev['Open'] and  # Previous green
                curr['Close'] < curr['Open'] and  # Current red
                curr['Open'] > prev['Close'] and  # Opens above prev close
                curr['Close'] < prev['Open'])     # Closes below prev open
    
    @staticmethod
    def _is_morning_star(c2, c1, c0):
        return (c2['Close'] < c2['Open'] and  # First candle red
                abs(c1['Close'] - c1['Open']) < (c2['High'] - c2['Low']) * 0.3 and  # Small body
                c0['Close'] > c0['Open'] and  # Third candle green
                c0['Close'] > (c2['Open'] + c2['Close']) / 2)  # Closes above midpoint
    
    @staticmethod
    def _is_evening_star(c2, c1, c0):
        return (c2['Close'] > c2['Open'] and  # First candle green
                abs(c1['Close'] - c1['Open']) < (c2['High'] - c2['Low']) * 0.3 and  # Small body
                c0['Close'] < c0['Open'] and  # Third candle red
                c0['Close'] < (c2['Open'] + c2['Close']) / 2)  # Closes below midpoint

# ============================================================================
# NEWS SENTIMENT ANALYZER (Simple version using Yahoo Finance news)
# ============================================================================

class NewsSentimentAnalyzer:
    """Analyze news sentiment for stocks"""
    
    @staticmethod
    def get_sentiment(symbol: str) -> dict:
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                return {'sentiment': 'neutral', 'score': 0, 'news_count': 0}
            
            # Simple sentiment based on title keywords
            positive_words = ['surge', 'jump', 'gain', 'rally', 'soar', 'beat', 'exceed', 'upgrade', 'buy']
            negative_words = ['plunge', 'drop', 'fall', 'decline', 'miss', 'downgrade', 'sell', 'warning']
            
            score = 0
            for article in news[:5]:  # Last 5 articles
                title = article.get('title', '').lower()
                for word in positive_words:
                    if word in title:
                        score += 1
                for word in negative_words:
                    if word in title:
                        score -= 1
            
            sentiment = 'positive' if score > 0 else 'negative' if score < 0 else 'neutral'
            
            return {
                'sentiment': sentiment,
                'score': score,
                'news_count': len(news),
                'recent_headlines': [n.get('title', '') for n in news[:3]]
            }
        except Exception as e:
            return {'sentiment': 'neutral', 'score': 0, 'news_count': 0, 'error': str(e)}

# ============================================================================
# PREDICTION ENGINE
# ============================================================================

class PredictionEngine:
    """Generate price predictions using technical analysis and momentum"""
    
    @staticmethod
    def predict_targets(data: pd.DataFrame, factors: dict, regime: str) -> dict:
        """Predict price targets for multiple timeframes"""
        
        if len(data) < 60 or not factors:
            return None
        
        current_price = float(data['Close'].iloc[-1])
        volatility = factors['volatility']['20d']
        momentum_1m = factors['momentum']['1m']
        rsi = factors['rsi']
        
        # Calculate ATR (Average True Range) for realistic price movement
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        
        # DAMPENED predictions - more conservative
        # Cap momentum to prevent unrealistic extrapolation
        dampened_momentum = momentum_1m * 0.3  # Reduce by 70%
        if dampened_momentum > 0.15:
            dampened_momentum = 0.15  # Cap at 15% monthly
        elif dampened_momentum < -0.15:
            dampened_momentum = -0.15
        
        # Base predictions on momentum and volatility
        predictions = {}
        
        # Today (intraday) - NOW INCLUDES LOW TARGET
        intraday_range = atr * 0.5
        if momentum_1m > 0:
            predictions['today'] = {
                'target_high': current_price + intraday_range,
                'target_low': current_price - (intraday_range * 0.3),  # Entry point
                'recommendation': 'bullish_bias',
                'entry_zone': current_price - (intraday_range * 0.2)  # Best entry
            }
        else:
            predictions['today'] = {
                'target_high': current_price + (intraday_range * 0.3),
                'target_low': current_price - intraday_range,  # Entry point
                'recommendation': 'bearish_bias',
                'entry_zone': current_price + (intraday_range * 0.2)  # Entry for shorts
            }
        
        # Tomorrow - very conservative
        daily_momentum = dampened_momentum * 0.05  # ~1.5% max for next day
        predictions['tomorrow'] = {
            'target': current_price * (1 + daily_momentum),
            'range_high': current_price * (1 + daily_momentum + volatility * 0.05),
            'range_low': current_price * (1 + daily_momentum - volatility * 0.05)
        }
        
        # 1 Week - conservative
        weekly_momentum = dampened_momentum * 0.25  # ~3.75% max for week
        predictions['week'] = {
            'target': current_price * (1 + weekly_momentum),
            'range_high': current_price * (1 + weekly_momentum + volatility * 0.15),
            'range_low': current_price * (1 + weekly_momentum - volatility * 0.15)
        }
        
        # 1 Month - still conservative but less dampened
        monthly_momentum = dampened_momentum  # 15% max monthly
        predictions['month'] = {
            'target': current_price * (1 + monthly_momentum),
            'range_high': current_price * (1 + monthly_momentum + volatility * 0.25),
            'range_low': current_price * (1 + monthly_momentum - volatility * 0.25)
        }
        
        # Entry/Exit recommendations with DETAILED reasoning
        reasoning_parts = []
        prediction_explanation = []
        
        if rsi < 30 and momentum_1m > -0.05:
            action = 'BUY'
            reasoning_parts.append('Oversold RSI with recovering momentum')
        elif rsi > 70 and momentum_1m < 0.05:
            action = 'SELL'
            reasoning_parts.append('Overbought RSI with weakening momentum')
        elif factors['trend']['score'] > 60 and momentum_1m > 0.02:
            action = 'BUY'
            reasoning_parts.append('Strong uptrend with positive momentum')
        elif factors['trend']['score'] < 40 and momentum_1m < -0.02:
            action = 'SELL'
            reasoning_parts.append('Weak downtrend with negative momentum')
        else:
            action = 'HOLD'
            reasoning_parts.append('Neutral signals, wait for clearer setup')
        
        # Add MACD insight
        if factors.get('macd'):
            macd_data = factors['macd']
            if macd_data['crossover'] == 'bullish':
                reasoning_parts.append('MACD bullish crossover (momentum building)')
            elif macd_data['crossover'] == 'bearish':
                reasoning_parts.append('MACD bearish crossover (momentum fading)')
        
        # Add Bollinger Band insight
        if factors.get('bollinger'):
            bb_data = factors['bollinger']
            if bb_data['signal'] == 'oversold':
                reasoning_parts.append(f'Near lower Bollinger Band (${bb_data["lower"]:.2f}) - potential bounce')
            elif bb_data['signal'] == 'overbought':
                reasoning_parts.append(f'Near upper Bollinger Band (${bb_data["upper"]:.2f}) - potential pullback')
        
        # Explain prediction methodology
        prediction_explanation.append(f"**How we calculated targets:**")
        prediction_explanation.append(f"• Current price: ${current_price:.2f}")
        prediction_explanation.append(f"• Recent momentum: {momentum_1m*100:.1f}% (last month)")
        prediction_explanation.append(f"• Dampened to: {dampened_momentum*100:.1f}% (to be conservative)")
        prediction_explanation.append(f"• ATR (daily range): ${atr:.2f}")
        prediction_explanation.append(f"• Volatility: {volatility*100:.1f}%")
        
        # Explain TODAY targets
        if momentum_1m > 0:
            prediction_explanation.append(f"\n**TODAY:** Bullish bias, watching for dip to entry zone")
            prediction_explanation.append(f"• Entry Zone ${predictions['today']['entry_zone']:.2f}: Best price to buy (near support)")
            prediction_explanation.append(f"• Low ${predictions['today']['target_low']:.2f}: Support level")
            prediction_explanation.append(f"• High ${predictions['today']['target_high']:.2f}: Resistance, could test today")
        else:
            prediction_explanation.append(f"\n**TODAY:** Bearish bias, wait for stabilization")
            prediction_explanation.append(f"• High ${predictions['today']['target_high']:.2f}: Resistance")
            prediction_explanation.append(f"• Low ${predictions['today']['target_low']:.2f}: Could drop here")
        
        # Explain WEEK target
        week_gain = ((predictions['week']['target'] - current_price) / current_price) * 100
        prediction_explanation.append(f"\n**1 WEEK:** Target ${predictions['week']['target']:.2f} ({week_gain:+.1f}%)")
        prediction_explanation.append(f"• Based on {dampened_momentum*0.25*100:.1f}% weekly momentum")
        prediction_explanation.append(f"• Range: ${predictions['week']['range_low']:.2f} - ${predictions['week']['range_high']:.2f}")
        if week_gain > 5:
            prediction_explanation.append(f"• Could reach ${predictions['week']['target']:.2f} by midweek if momentum holds")
        elif week_gain < -5:
            prediction_explanation.append(f"• May drop to ${predictions['week']['target']:.2f} by Thursday if selling continues")
        else:
            prediction_explanation.append(f"• Likely gradual move to ${predictions['week']['target']:.2f} throughout week")
        
        # Explain MONTH target
        month_gain = ((predictions['month']['target'] - current_price) / current_price) * 100
        prediction_explanation.append(f"\n**1 MONTH:** Target ${predictions['month']['target']:.2f} ({month_gain:+.1f}%)")
        prediction_explanation.append(f"• Based on {dampened_momentum*100:.1f}% dampened monthly momentum")
        prediction_explanation.append(f"• Conservative estimate - capped at 15% max")
        if month_gain > 8:
            prediction_explanation.append(f"• Strong setup, could reach target in 3-4 weeks")
        elif month_gain < -8:
            prediction_explanation.append(f"• Weak setup, may take full month or longer")
        else:
            prediction_explanation.append(f"• Moderate setup, expect steady progress toward target")
        
        reasoning = ' | '.join(reasoning_parts)
        
        return {
            'current_price': current_price,
            'predictions': predictions,
            'action': action,
            'reasoning': reasoning,
            'confidence': 'medium' if abs(dampened_momentum) > 0.05 else 'low',
            'detailed_explanation': '\n'.join(prediction_explanation)
        }

# ============================================================================
# LIVE TRADING ANALYZER (Main Engine)
# ============================================================================

class LiveTradingAnalyzer:
    """Main analysis engine for live trading"""
    
    def __init__(self, config):
        self.config = config
        self.regime_detector = RegimeDetector()
        self.factor_analyzer = MultiFactorAnalyzer()
        self.pattern_detector = CandlestickPatternDetector()
        self.news_analyzer = NewsSentimentAnalyzer()
        self.prediction_engine = PredictionEngine()
        
    def get_sector_stocks(self, enabled_sectors=None):
        """Get stocks from enabled sectors"""
        if enabled_sectors is None:
            enabled_sectors = list(SECTORS.keys())
        
        stocks = {}
        for sector in enabled_sectors:
            if sector in SECTORS:
                stocks[sector] = SECTORS[sector]
        
        return stocks
    
    def analyze_stock(self, symbol: str, spy_regime: dict) -> dict:
        """Complete analysis for a single stock"""
        
        try:
            # Download data
            stock = yf.Ticker(symbol)
            data = stock.history(period='1y')
            
            if len(data) < 60:
                return None
            
            # Calculate factors
            factors = self.factor_analyzer.calculate_factors(data, symbol)
            if not factors:
                return None
            
            # Composite score
            score = self.factor_analyzer.composite_score(factors, spy_regime['regime'])
            
            # Candlestick patterns
            patterns = self.pattern_detector.detect_patterns(data)
            
            # News sentiment
            news = self.news_analyzer.get_sentiment(symbol)
            
            # Predictions
            predictions = self.prediction_engine.predict_targets(data, factors, spy_regime['regime'])
            
            # Get company info
            info = stock.info
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'current_price': float(data['Close'].iloc[-1]),
                'score': score,
                'factors': factors,
                'patterns': patterns,
                'news': news,
                'predictions': predictions,
                'regime': spy_regime['regime']
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def run_analysis(self, enabled_sectors=None, top_n=10):
        """Run analysis on all stocks and return top opportunities"""
        
        print("🔄 Analyzing market regime...")
        
        # Get SPY data for regime detection
        spy = yf.Ticker('SPY')
        spy_data = spy.history(period='1y')
        spy_regime = self.regime_detector.detect_regime(spy_data)
        
        print(f"📊 Market Regime: {spy_regime['regime'].upper()}")
        print(f"🌊 Volatility: {spy_regime['volatility']:.1%}\n")
        
        # Get stocks to analyze
        sector_stocks = self.get_sector_stocks(enabled_sectors)
        
        all_analyses = []
        total_stocks = sum(len(stocks) for stocks in sector_stocks.values())
        
        print(f"🔍 Analyzing {total_stocks} stocks across {len(sector_stocks)} sectors...\n")
        
        for sector, stocks in sector_stocks.items():
            print(f"  Analyzing {sector}... ({len(stocks)} stocks)")
            
            for symbol in stocks[:50]:  # Top 50 per sector
                analysis = self.analyze_stock(symbol, spy_regime)
                if analysis:
                    all_analyses.append(analysis)
        
        # Sort by score
        all_analyses.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'market_regime': spy_regime,
            'total_analyzed': len(all_analyses),
            'top_opportunities': all_analyses[:top_n],
            'all_stocks': all_analyses,
            'timestamp': datetime.now().isoformat()
        }
    
    def format_recommendation(self, analysis: dict, capital: float) -> dict:
        """Format a trading recommendation with position sizing"""
        
        predictions = analysis['predictions']
        current_price = analysis['current_price']
        
        # Position size (configurable % of capital)
        position_pct = self.config.get('position_size_pct', 10) / 100
        position_value = capital * position_pct
        shares = int(position_value / current_price)
        
        if shares == 0:
            shares = 1  # Minimum 1 share
        
        actual_position = shares * current_price
        
        # Stop loss and take profit
        stop_loss_pct = self.config.get('stop_loss_pct', 5) / 100
        take_profit_pct = self.config.get('take_profit_pct', 10) / 100
        
        stop_loss = current_price * (1 - stop_loss_pct)
        take_profit = current_price * (1 + take_profit_pct)
        
        # Build reasoning
        reasoning_parts = [predictions['reasoning']]
        
        # Add pattern info
        if analysis['patterns']:
            pattern_names = [p['pattern'] for p in analysis['patterns']]
            reasoning_parts.append(f"Patterns: {', '.join(pattern_names)}")
        
        # Add news sentiment
        if analysis['news']['sentiment'] != 'neutral':
            reasoning_parts.append(f"News sentiment: {analysis['news']['sentiment']}")
        
        # Add price levels
        factors = analysis['factors']
        dist_from_high = factors['price_levels']['distance_from_high']
        dist_from_low = factors['price_levels']['distance_from_low']
        reasoning_parts.append(f"52w High: {dist_from_high:+.1f}%, 52w Low: {dist_from_low:+.1f}%")
        
        return {
            'symbol': analysis['symbol'],
            'company': analysis['company_name'],
            'action': predictions['action'],
            'current_price': current_price,
            'shares': shares,
            'position_value': actual_position,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'targets': {
                'today_high': predictions['predictions']['today']['target_high'],
                'today_low': predictions['predictions']['today']['target_low'],
                'tomorrow': predictions['predictions']['tomorrow']['target'],
                'week': predictions['predictions']['week']['target'],
                'month': predictions['predictions']['month']['target']
            },
            'score': analysis['score'],
            'rsi': factors['rsi'],
            'momentum_1m': factors['momentum']['1m'],
            'patterns': [p['pattern'] for p in analysis['patterns']],
            'news_sentiment': analysis['news']['sentiment'],
            'reasoning': ' | '.join(reasoning_parts),
            'regime': analysis['regime']
        }

# ============================================================================
# CONFIGURATION
# ============================================================================

def load_config():
    """Load or create default configuration"""
    
    default_config = {
        'capital': 2400,
        'position_size_pct': 10,
        'stop_loss_pct': 5,
        'take_profit_pct': 10,
        'enabled_sectors': list(SECTORS.keys()),
        'top_opportunities': 20,
        'min_score': 50
    }
    
    config_file = 'trading_config.json'
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        # Merge with defaults for any missing keys
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        return config
    else:
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

def save_config(config):
    """Save configuration"""
    with open('trading_config.json', 'w') as f:
        json.dump(config, f, indent=4)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LIVE TRADING ANALYSIS SYSTEM                              ║
║                                                                              ║
║  Features:                                                                   ║
║  ✓ Multi-sector stock screening (Top 50 per sector)                        ║
║  ✓ Technical analysis (Momentum, Trend, Volume, Volatility)                ║
║  ✓ Candlestick pattern detection                                           ║
║  ✓ News sentiment analysis                                                 ║
║  ✓ Price predictions (Today, Tomorrow, Week, Month)                        ║
║  ✓ Position sizing and risk management                                     ║
║  ✓ Market regime detection                                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    config = load_config()
    analyzer = LiveTradingAnalyzer(config)
    
    print(f"💰 Capital: ${config['capital']}")
    print(f"📊 Position Size: {config['position_size_pct']}% (${config['capital'] * config['position_size_pct'] / 100:.0f} per trade)")
    print(f"🎯 Sectors Enabled: {len(config['enabled_sectors'])}")
    print(f"\nStarting analysis...\n")
    
    results = analyzer.run_analysis(config['enabled_sectors'], config['top_opportunities'])
    
    print(f"\n{'='*80}")
    print(f"📈 TOP {len(results['top_opportunities'])} OPPORTUNITIES")
    print(f"{'='*80}\n")
    
    for i, stock in enumerate(results['top_opportunities'], 1):
        rec = analyzer.format_recommendation(stock, config['capital'])
        
        print(f"{i}. {rec['symbol']} - {rec['company']}")
        print(f"   Action: {rec['action']} | Score: {rec['score']:.1f} | RSI: {rec['rsi']:.0f}")
        print(f"   Price: ${rec['current_price']:.2f}")
        print(f"   Position: {rec['shares']} shares = ${rec['position_value']:.2f}")
        print(f"   Stop Loss: ${rec['stop_loss']:.2f} | Take Profit: ${rec['take_profit']:.2f}")
        print(f"   Targets: Today ${rec['targets']['today_high']:.2f}, Week ${rec['targets']['week']:.2f}, Month ${rec['targets']['month']:.2f}")
        print(f"   Reasoning: {rec['reasoning']}")
        print()
    
    # Save results
    output_file = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"✅ Results saved to {output_file}")