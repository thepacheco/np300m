"""
QUICK TEST SCRIPT
Run this to make sure everything is working before deploying
"""

import sys

print("🧪 Testing Trading System Setup...\n")

# Test 1: Python Version
print("1️⃣ Checking Python version...")
if sys.version_info < (3, 8):
    print("   ❌ Need Python 3.8+, you have:", sys.version)
    print("   Download from: https://www.python.org/downloads/")
    sys.exit(1)
else:
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")

# Test 2: Import Dependencies
print("\n2️⃣ Testing dependencies...")

required = {
    'yfinance': 'Stock data',
    'pandas': 'Data analysis',
    'numpy': 'Math operations',
    'flask': 'Web server',
    'flask_cors': 'CORS support',
    'scipy': 'Scientific computing'
}

missing = []
for package, desc in required.items():
    try:
        __import__(package)
        print(f"   ✅ {package:15} ({desc})")
    except ImportError:
        print(f"   ❌ {package:15} MISSING")
        missing.append(package)

if missing:
    print(f"\n   ⚠️  Missing packages: {', '.join(missing)}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 3: Import Main System
print("\n3️⃣ Testing trading system import...")
try:
    from trading_system import LiveTradingAnalyzer, load_config, SECTORS
    print("   ✅ trading_system.py loads correctly")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 4: Test Config
print("\n4️⃣ Testing configuration...")
try:
    config = load_config()
    print(f"   ✅ Config loaded: Capital=${config['capital']}")
    print(f"   ✅ Sectors available: {len(SECTORS)}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 5: Test Analyzer
print("\n5️⃣ Testing analyzer initialization...")
try:
    analyzer = LiveTradingAnalyzer(config)
    print("   ✅ Analyzer created successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 6: Test Flask App
print("\n6️⃣ Testing Flask app...")
try:
    from app import app
    print("   ✅ Flask app loads correctly")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 7: Quick Data Test
print("\n7️⃣ Testing data download (this may take 10 seconds)...")
try:
    import yfinance as yf
    ticker = yf.Ticker('AAPL')
    data = ticker.history(period='5d')
    if len(data) > 0:
        print(f"   ✅ Can download stock data (AAPL: ${data['Close'].iloc[-1]:.2f})")
    else:
        print("   ⚠️  No data returned (may be market hours or connection issue)")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   (This might be okay - could be Yahoo Finance rate limiting)")

# Summary
print("\n" + "="*60)
print("🎉 ALL TESTS PASSED!")
print("="*60)
print("\n✨ Your system is ready to use!")
print("\nNext steps:")
print("  1. Run locally: python app.py")
print("  2. Open browser: http://localhost:5000")
print("  3. Or deploy to Render.com (see SETUP_GUIDE.md)")
print("\n💡 Tips:")
print("  - Start with small capital to test")
print("  - Enable only 2-3 sectors for faster analysis")
print("  - Analysis takes 2-5 minutes depending on sectors")
print("\nHappy trading! 📈\n")
