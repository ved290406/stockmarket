import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# ===============================
# 1. LOAD NSE STOCK LIST
# ===============================

try:
    # Read the CSV
    df = pd.read_csv("EQUITY_L.csv")
    
    # Strip any hidden spaces from column headers (Fixes the KeyError: 'SYMBOL')
    df.columns = df.columns.str.strip()
    
    # Extract symbols
    stocks = df['SYMBOL'].tolist()
    
    # Convert to Yahoo Finance format
    stocks = [str(stock).strip() + ".NS" for stock in stocks]
    print(f"✅ Successfully loaded {len(stocks)} stocks from EQUITY_L.csv")
    
except FileNotFoundError:
    print("⚠️ 'EQUITY_L.csv' not found. Using a default sample list of NSE stocks.")
    stocks = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
        "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "L&T.NS", "BAJFINANCE.NS"
    ]
except KeyError:
    print("\n❌ ERROR: Could not find the 'SYMBOL' column in the CSV.")
    print(f"Columns found in your CSV: {df.columns.tolist()}")
    print("Please ensure your CSV has a column exactly named 'SYMBOL'.")
    exit()

print("Sample:", stocks[:10])


# ===============================
# 2. ANALYZE SINGLE STOCK
# ===============================

def analyze_stock(stock_name):
    print(f"\nAnalyzing {stock_name}...\n")

    # Download data (progress=False prevents terminal spam)
    data = yf.download(stock_name, period="6mo", progress=False)

    if data.empty:
        print("❌ No data found. Please check the ticker symbol.")
        return

    # Handle multi-index columns from newer yfinance versions
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    # Calculate Moving Averages
    data['MA20'] = data['Close'].rolling(20).mean()
    data['MA50'] = data['Close'].rolling(50).mean()

    # Drop NaN values created by moving averages
    data.dropna(inplace=True)
    
    if data.empty:
        print("❌ Not enough data points to calculate Moving Averages.")
        return

    # Get the latest row of data
    latest = data.iloc[-1]

    # Safely extract values
    close_price = float(latest['Close'])
    ma20 = float(latest['MA20'])
    ma50 = float(latest['MA50'])
    volume = int(latest['Volume'])

    # Signal Logic
    if close_price > ma20 and ma20 > ma50:
        signal = "BUY 📈"
    elif close_price < ma20 and ma20 < ma50:
        signal = "SELL 📉"
    else:
        signal = "HOLD ⚖️"

    # Print details to console
    print(f"Price:  ₹{close_price:.2f}")
    print(f"MA20:   ₹{ma20:.2f}")
    print(f"MA50:   ₹{ma50:.2f}")
    print(f"Volume: {volume:,}")
    print(f"Signal: {signal}")

    # Plot (This opens the graphical window on your desktop)
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'], label="Close Price", color='blue', linewidth=1.5)
    plt.plot(data.index, data['MA20'], label="20-Day MA", color='orange', linestyle='--')
    plt.plot(data.index, data['MA50'], label="50-Day MA", color='red', linestyle='--')
    
    plt.title(f"{stock_name} - 6 Month Trend")
    plt.xlabel("Date")
    plt.ylabel("Price (INR)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Show the chart window
    plt.show()


# ===============================
# 3. SCAN MULTIPLE STOCKS
# ===============================

def scan_market(limit=50):
    print(f"\nScanning top {limit} stocks in the market...\n")

    results = []
    failed_stocks = 0

    for stock in stocks[:limit]:
        try:
            # Using Ticker().history() bypasses the yfinance Multi-Index bug
            ticker_obj = yf.Ticker(stock)
            data = ticker_obj.history(period="3mo")

            if data.empty:
                failed_stocks += 1
                continue

            # Calculate Moving Averages
            data['MA20'] = data['Close'].rolling(20).mean()
            data['MA50'] = data['Close'].rolling(50).mean()
            
            # Clean data
            data.dropna(inplace=True)
            if data.empty:
                continue

            # Get latest values
            latest = data.iloc[-1]
            close_price = float(latest['Close'])
            ma20 = float(latest['MA20'])
            ma50 = float(latest['MA50'])

            # Signal Logic
            if close_price > ma20 and ma20 > ma50:
                results.append((stock, "BUY 📈", close_price))
            elif close_price < ma20 and ma20 < ma50:
                results.append((stock, "SELL 📉", close_price))

        except Exception as e:
            # Print the error so it doesn't fail silently
            print(f"⚠️ Error scanning {stock}: {e}")
            failed_stocks += 1
            continue

    # Print Final Results
    print("\n🔥 TOP SIGNALS 🔥")
    if failed_stocks > 0:
        print(f"(Note: {failed_stocks} stocks were skipped due to missing data or network errors)\n")

    if not results:
        print("No strong trends detected in this batch. The market might be moving sideways.")
    else:
        print(f"{'SYMBOL':<15} | {'SIGNAL':<10} | {'PRICE'}")
        print("-" * 40)
        for r in results[:15]:  # Show top 15 results to keep the terminal clean
            print(f"{r[0]:<15} | {r[1]:<10} | ₹{r[2]:.2f}")


# ===============================
# 4. MAIN MENU
# ===============================

if __name__ == "__main__":
    while True:
        print("\n" + "="*30)
        print("   NSE STOCK ANALYZER   ")
        print("="*30)
        print("1. Analyze Single Stock (w/ Chart)")
        print("2. Scan Market (Find Top Signals)")
        print("3. Exit")

        choice = input("\nEnter your choice (1/2/3): ").strip()

        if choice == "1":
            stock = input("Enter stock symbol (e.g., RELIANCE): ").strip().upper()
            if not stock.endswith(".NS"):
                stock += ".NS"  # Auto-append .NS for Yahoo Finance
            analyze_stock(stock)

        elif choice == "2":
            # Change limit depending on how fast your PC/Internet is (e.g., 50, 100, 500)
            scan_market(limit=50) 

        elif choice == "3":
            print("\nExiting Analyzer. Goodbye!")
            break

        else:
            print("\n❌ Invalid choice, please select 1, 2, or 3.")