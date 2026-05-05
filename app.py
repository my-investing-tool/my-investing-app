import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="Investing Pro - Smart Analysis", layout="wide")
st.title("🚀 Investing Pro: Advanced Stock Analyzer")

# 2. Sidebar - Global Settings
st.sidebar.header("Pro Settings")
days_limit = st.sidebar.slider("Historical Data (Days)", 30, 2000, 730)
st.sidebar.info("Pro Tip: 730+ days data helps in better Moving Average analysis.")

# 3. Search Section
col_a, col_b = st.columns([5, 1])
with col_a:
    ticker_input = st.text_input("Enter Stock Ticker (e.g. RELIANCE, HDFCBANK, TCS):", "ITC")
with col_b:
    st.write("##")
    search_button = st.button("Pro Analysis ✨")

if search_button or ticker_input:
    ticker_symbol = ticker_input.upper().strip()
    if not (ticker_symbol.endswith(".NS") or ticker_symbol.endswith(".BO")):
        ticker_symbol = f"{ticker_symbol}.NS"

    try:
        with st.spinner('Pro AI Data fetching in progress...'):
            stock = yf.Ticker(ticker_symbol)
            df = stock.history(period=f"{days_limit}d")
            info = stock.info

        if df.empty:
            st.error("Data nahi mila. Ticker check karein.")
        else:
            # --- PRO CALCULATIONS ---
            # 1. RSI Calculation
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # 2. Moving Averages
            df['MA50'] = df['Close'].rolling(window=50).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()

            # 3. Pro Feature: Volatility & Risk
            returns = df['Close'].pct_change()
            volatility = returns.std() * np.sqrt(252) * 100 # Annualized Volatility

            # --- HEADER SECTION ---
            st.header(f"{info.get('longName', ticker_symbol)} Analysis")
            
            # Key Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            curr_price = info.get('currentPrice') or df['Close'].iloc[-1]
            m1.metric("Current Price", f"₹{curr_price:,.2f}")
            
            # RSI Pro Labeling
            cur_rsi = df['RSI'].iloc[-1]
            rsi_label = "Neutral"
            if cur_rsi < 35: rsi_label = "🔥 Oversold (Buy Zone)"
            elif cur_rsi > 65: rsi_label = "⚠️ Overbought (Sell Zone)"
            m2.metric("RSI (14)", f"{cur_rsi:.2f}", rsi_label)

            # Risk Meter
            risk_label = "Low" if volatility < 20 else "Medium" if volatility < 35 else "High"
            m3.metric("Risk Level", risk_label, f"{volatility:.1f}% Vol")

            # Dividend Yield
            div = info.get('dividendYield', 0)
            m4.metric("Dividend Yield", f"{(div*100) if div else 0:.2f}%")

            # --- PRO FEATURE: HEALTH SCORE ---
            st.divider()
            st.subheader("📊 Financial Health Score (Pro)")
            
            # Logic for scoring
            score = 0
            reasons = []
            
            # Check 1: Price vs MA200
            if curr_price > df['MA200'].iloc[-1]: 
                score += 25
                reasons.append("✅ Stock is in a long-term uptrend (Above 200 DMA).")
            # Check 2: RSI Buy Zone
            if cur_rsi < 45: 
                score += 25
                reasons.append("✅ RSI suggesting value entry zone.")
            # Check 3: Profitability (ROE)
            roe = info.get('returnOnEquity', 0)
            if roe and roe > 0.15: 
                score += 25
                reasons.append(f"✅ Strong Profitability (ROE: {roe*100:.1f}%).")
            # Check 4: Debt to Equity
            debt_ratio = info.get('debtToEquity', 100)
            if debt_ratio < 100:
                score += 25
                reasons.append("✅ Healthy Debt-to-Equity ratio.")

            # Display Score
            s_col1, s_col2 = st.columns([1, 2])
            s_col1.metric("Overall Score", f"{score}/100")
            with s_col2:
                for r in reasons: st.write(r)

            # --- PRO FEATURE: INTRINSIC VALUE ---
            st.divider()
            st.subheader("💎 Intrinsic Value Analysis")
            eps = info.get('trailingEps', 0)
            bv = info.get('bookValue', 0)
            
            if eps and bv and eps > 0:
                graham = (22.5 * eps * bv)**0.5
                diff = ((graham - curr_price) / curr_price) * 100
                
                c1, c2 = st.columns(2)
                c1.write(f"**Graham Number:** ₹{graham:.2f}")
                if diff > 0:
                    c2.success(f"Stock is Underpriced by {diff:.1f}%")
                else:
                    c2.warning(f"Stock is Overpriced by {abs(diff):.1f}%")
            else:
                st.info("Intrinsic value calculate karne ke liye data insufficient hai.")

            # --- PRO CHARTING ---
            st.subheader("Price & Smart Trendlines")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Market Price'))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='Short Term (50 DMA)', line=dict(color='orange', width=1.2)))
            fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='Long Term (200 DMA)', line=dict(color='cyan', width=2)))
            
            fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # --- SECTOR INFO ---
            with st.expander("Company Profile & Sector"):
                st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                st.write(info.get('longBusinessSummary', 'No summary available.'))

    except Exception as e:
        st.error(f"Analysis failed: {e}")
        
