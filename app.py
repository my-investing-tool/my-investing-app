import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="Pro Investor Tool", layout="wide")
st.title("📈 Smart Investing Tool (Pro)")

# 2. Sidebar Settings
st.sidebar.header("Settings")
days_limit = st.sidebar.slider("Historical Data (Days)", 30, 1000, 365)
st.sidebar.info("Tip: Indian stocks ke liye default .NS add ho jayega.")

# 3. Search Section
col_a, col_b = st.columns([5, 1])

with col_a:
    ticker_input = st.text_input("Enter Stock Ticker (e.g. ITC, RELIANCE, TCS):", "ITC")

with col_b:
    st.write("##") # Spacing
    search_button = st.button("Search 🔍")

if search_button or ticker_input:
    ticker_symbol = ticker_input.upper().strip()
    
    # Auto-add .NS if not present (Indian Stocks)
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
            # --- Technical Indicators Calculation ---
            # 1. RSI (Standard Wilder's Smoothing)
            window = 14
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            current_rsi = df['RSI'].iloc[-1]

            # 2. Moving Averages
            df['MA50'] = df['Close'].rolling(window=50).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()

            # --- Display Results ---
            st.header(f"Analysis: {info.get('longName', ticker_symbol)}")
            
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            
            curr_price = info.get('currentPrice') or info.get('regularMarketPrice') or df['Close'].iloc[-1]
            m1.metric("Current Price", f"₹{curr_price:,.2f}")

            # RSI Logic
            rsi_status = "Neutral"
            if current_rsi < 30: rsi_status = "Sasta (Oversold)"
            elif current_rsi > 70: rsi_status = "Mehenga (Overbought)"
            m2.metric("RSI (14)", f"{current_rsi:.2f}", rsi_status)

            # Dividend Yield
            div = info.get('dividendYield', 0)
            div_val = (div * 100) if div else 0
            m3.metric("Dividend Yield", f"{div_val:.2f}%")

            # Market Cap
            m_cap = info.get('marketCap', 0)
            m_cap_cr = (m_cap / 10**7) if m_cap else 0
            m_cap_text = f"{m_cap_cr:,.2f} Cr" if m_cap_cr < 10000 else f"{(m_cap_cr/100):,.2f} Lk Cr"
            m_cap_label = "Market Cap (Cr)" if m_cap_cr < 10000 else "Market Cap (Lakh Cr)"
            m4.metric(m_cap_label, m_cap_text)

            # --- Fundamental Analysis (Graham Number) ---
            st.divider()
            eps = info.get('trailingEps', 0)
            bv = info.get('bookValue', 0)
            
            if eps and bv and eps > 0 and bv > 0:
                graham = (22.5 * eps * bv)**0.5
                st.subheader("Fundamental Check")
                st.write(f"**Graham Number (Fair Value):** ₹{graham:.2f}")
                if curr_price < graham:
                    st.success("✅ Yeh stock apni fair value se niche hai (Value Buy potential).")
                else:
                    st.warning("⚠️ Yeh stock apni fair value se upar trade kar raha hai.")

            # --- Interactive Candlestick Chart ---
            st.subheader("Price Trend & Moving Averages")
            fig = go.Figure()

            # Candlestick
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name='Price'
            ))

            # Add Moving Averages
            fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='50 DMA', line=dict(color='orange', width=1.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='200 DMA', line=dict(color='red', width=1.5)))

            fig.update_layout(
                height=600,
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- Data Table ---
            with st.expander("Raw Data Dekhein"):
                st.dataframe(df.tail(10))

    except Exception as e:
        st.error(f"Kuch galat hua: {e}")
