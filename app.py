import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="Pro Investor Tool", layout="wide")
st.title("📈 Smart Investing Tool (Pro)")

# 2. Search Section (Main Screen par)
st.subheader("Stock Search")
col_a, col_b = st.columns([3, 1])

with col_a:
    ticker_input = st.text_input("Enter Stock Ticker (e.g. ITC, RELIANCE, TCS):", "ITC")
with col_b:
    # Neeche spacing ke liye empty text
    st.write("##") 
    search_button = st.button('Search 🔍')

# 3. Sidebar for Settings
days_limit = st.sidebar.slider("Historical Data (Days)", 30, 365, 180)
st.sidebar.info("Tip: Indian stocks ke liye default .NS (NSE) add ho jayega.")

# 4. Main Logic Execution
if search_button or ticker_input:
    ticker_symbol = ticker_input.upper().strip()
    
    # Auto-add .NS if not present
    if not (ticker_symbol.endswith(".NS") or ticker_symbol.endswith(".BO")):
        ticker_symbol = f"{ticker_symbol}.NS"

    try:
        # Data fetching
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period=f"{days_limit}d")
        info = stock.info

        if df.empty:
            st.error(f"Maaf kijiye, '{ticker_symbol}' ka data nahi mil paya. Ticker sahi se check karein.")
        else:
            # --- RSI Calculation ---
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            current_rsi = df['RSI'].iloc[-1]

            # --- Display Results ---
            st.divider()
            st.header(f"Analysis: {info.get('longName', ticker_symbol)}")
            
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            
            curr_price = info.get('currentPrice', 0)
            m1.metric("Current Price", f"₹{curr_price}")

            # RSI Logic
            rsi_text = "Neutral"
            if current_rsi < 30: rsi_text = "Sasta (Oversold)"
            elif current_rsi > 70: rsi_text = "Mehenga (Overbought)"
            m2.metric("RSI (14)", f"{current_rsi:.2f}", rsi_text)

            # Dividend
            div = info.get('dividendYield', 0)
            m3.metric("Dividend Yield", f"{div*100:.2f}%" if div else "0%")

            # Market Cap
            m_cap = info.get('marketCap', 0) / 10**7
            m4.metric("Market Cap", f"{m_cap:.2f} Cr")

            # --- Graham Number Analysis ---
            eps = info.get('trailingEps', 0)
            bv = info.get('bookValue', 0)
            if eps > 0 and bv > 0:
                graham = (22.5 * eps * bv)**0.5
                st.info(f"💡 **Graham Fair Value:** ₹{graham:.2f}")
                if curr_price < graham:
                    st.success("Yeh stock apni fair value se niche hai (Value Buy potential).")

            # --- Chart ---
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Price'))
            fig.update_layout(title=f"{ticker_symbol} Price Trend", height=450)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Kuch galat hua: {e}")
        
