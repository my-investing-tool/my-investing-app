import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Pro Investor Tool", layout="wide")
st.title("🚀 Smart Investing Tool (Pro)")

ticker_symbol = st.sidebar.text_input("Stock Ticker (e.g. ITC.NS, RELIANCE.NS)", "ITC.NS")
days_limit = st.sidebar.slider("Historical Data (Days)", 30, 365, 180)

if ticker_symbol:
    try:
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period=f"{days_limit}d")
        info = stock.info
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        current_rsi = df['RSI'].iloc[-1]
        st.subheader(f"Analysis: {info.get('longName', ticker_symbol)}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Price", f"₹{info.get('currentPrice', 'N/A')}")
        if current_rsi < 30: col2.metric("RSI (14)", f"{current_rsi:.2f}", "Sasta")
        elif current_rsi > 70: col2.metric("RSI (14)", f"{current_rsi:.2f}", "Mehenga")
        else: col2.metric("RSI (14)", f"{current_rsi:.2f}", "Neutral")
        col3.metric("Dividend Yield", f"{info.get('dividendYield', 0)*100:.2f}%")
        col4.metric("Market Cap", f"₹{info.get('marketCap', 0)//10**7} Cr")
        eps, bv = info.get('trailingEps', 0), info.get('bookValue', 0)
        if eps > 0 and bv > 0:
            graham = (22.5 * eps * bv)**0.5
            st.info(f"Graham Fair Value: ₹{graham:.2f}")
        st.plotly_chart(go.Figure(data=[go.Scatter(x=df.index, y=df['Close'])]), use_container_width=True)
    except: st.error("Ticker check karein (Ex: RELIANCE.NS)")
