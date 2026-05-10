import yfinance as yf
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, DateFormatter
import pandas as pd
import pytz  # Add this import for timezone handling

def fetch_stock_data():
    tickers = entry_tickers.get().upper().split(',')
    tickers = [ticker.strip() for ticker in tickers]

    if not tickers:
        messagebox.showerror("Input Error", "Please enter at least one stock ticker symbol.")
        return

    try:
        clear_previous_data()
        
        all_info = {}
        for ticker_symbol in tickers:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            
            if not info:
                messagebox.showerror("Data Error", f"No information available for {ticker_symbol}")
                continue

            all_info[ticker_symbol] = info
            # Plot stock data
            plot_stock_data(stock, ticker_symbol)
        
        # Display stock information
        display_comparison_info(all_info)
    except Exception as e:
        messagebox.showerror("Error", f"Error retrieving data: {e}")

def clear_previous_data():
    # Clear previous stock information
    text_info.config(state=tk.NORMAL)
    text_info.delete(1.0, tk.END)
    text_info.config(state=tk.DISABLED)
    
    # Clear previous plot
    for widget in frame_plot.winfo_children():
        widget.destroy()

def display_comparison_info(all_info):
    text_info.config(state=tk.NORMAL)
    text_info.delete(1.0, tk.END)
    
    header = f"{'Stock':<15} {'Current Price':<15} {'P/E Ratio':<15} {'52W High':<15} {'52W Low':<15} {'Dividend Yield':<20} {'Market Cap':<20}\n"
    text_info.insert(tk.END, header)
    text_info.insert(tk.END, '-'*105 + '\n')
    
    for ticker_symbol, info in all_info.items():
        company_name = info.get('longName', 'N/A')
        current_price = f"₹{info.get('currentPrice', 'N/A')}"
        pe_ratio = info.get('trailingPE', 'N/A')
        week_52_high = f"₹{info.get('fiftyTwoWeekHigh', 'N/A')}"
        week_52_low = f"₹{info.get('fiftyTwoWeekLow', 'N/A')}"
        dividend_yield = f"{info.get('dividendYield', 'N/A')*100 if info.get('dividendYield') else 'N/A'}%"
        market_cap = f"₹{info.get('marketCap', 'N/A'):,}"
        line = f"{company_name:<15} {current_price:<15} {pe_ratio:<15} {week_52_high:<15} {week_52_low:<15} {dividend_yield:<20} {market_cap:<20}\n"
        text_info.insert(tk.END, line)
    
    text_info.config(state=tk.DISABLED)

def plot_stock_data(stock, ticker_symbol):
    data = stock.history(period='1d', interval='1m')
    if data.empty:
        messagebox.showerror("Data Error", f"No historical data available for {ticker_symbol}")
        return

    # Convert timestamps to Indian Standard Time (IST)
    ist = pytz.timezone('Asia/Kolkata')
    data.index = data.index.tz_convert(ist)

    figure = plt.Figure(figsize=(12, 6), dpi=100)
    ax = figure.add_subplot(111)

    # Define custom colors
    plot_color = '#1f77b4'  # Blue
    grid_color = '#e0e0e0'  # Light Gray
    label_color = '#333333'  # Dark Gray
    title_color = '#ff5722'  # Orange

    ax.plot(data.index, data['Close'], label=f'{ticker_symbol} Close Price', color=plot_color, linestyle='-', linewidth=2)

    # Customize the plot
    ax.set_xlabel('Time', fontsize=12, color=label_color)
    ax.set_ylabel('Price (INR)', fontsize=12, color=label_color)
    ax.set_title(f'Historical Close Prices for {ticker_symbol}', fontsize=14, color=title_color)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color=grid_color)
    ax.tick_params(axis='both', colors=label_color)

    # Update the time scale
    locator = AutoDateLocator()
    formatter = DateFormatter('%Y-%m-%d %H:%M', tz=ist)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    # Rotate the date labels for better readability
    figure.autofmt_xdate()

    # Add plot to the tkinter frame
    canvas = FigureCanvasTkAgg(figure, frame_plot)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

def save_to_csv():
    tickers = entry_tickers.get().upper().split(',')
    tickers = [ticker.strip() for ticker in tickers]

    if not tickers:
        messagebox.showerror("Input Error", "Please enter at least one stock ticker symbol.")
        return
    
    try:
        all_data = []
        for ticker_symbol in tickers:
            stock = yf.Ticker(ticker_symbol)
            data = stock.history(period='1d', interval='1m')
            if not data.empty:
                data['Ticker'] = ticker_symbol
                all_data.append(data)
        
        if all_data:
            combined_data = pd.concat(all_data)
            combined_data.to_csv('stock_data.csv')
            messagebox.showinfo("Success", "Data saved to 'stock_data.csv'")
        else:
            messagebox.showwarning("No Data", "No data available to save.")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving data: {e}")

# Create the main window
root = tk.Tk()
root.title("Indian Stock Market Viewer")

# Apply a theme color to the main window
root.configure(bg='lightgrey')

# Create and place the widgets
frame_top = tk.Frame(root, bg='lightblue')
frame_top.pack(side=tk.TOP, fill=tk.X, pady=5)

label_tickers = tk.Label(frame_top, text="Enter Stock Ticker Symbols (comma-separated):", bg='lightblue', font=('Helvetica', 12))
label_tickers.pack(side=tk.LEFT, padx=10)

entry_tickers = tk.Entry(frame_top, width=50, font=('Helvetica', 12))
entry_tickers.pack(side=tk.LEFT, padx=10)

button_fetch = tk.Button(frame_top, text="Fetch Data", command=fetch_stock_data, bg='lightgreen', font=('Helvetica', 12))
button_fetch.pack(side=tk.LEFT, padx=10)

button_save = tk.Button(frame_top, text="Save Data", command=save_to_csv, bg='lightcoral', font=('Helvetica', 12))
button_save.pack(side=tk.LEFT, padx=10)

frame_info = tk.Frame(root)
frame_info.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

text_info = tk.Text(frame_info, height=15, state=tk.DISABLED, bg='white', font=('Helvetica', 12))
text_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

frame_plot = tk.Frame(root)
frame_plot.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Start the main event loop
root.mainloop()