import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# PAGE CONFIG
@st.cache_data(ttl=60)
def load_stock_data(symbol):
    data = yf.download(
        symbol,
        period="5d",
        interval="5m",
        auto_adjust=True,
        progress=False
    )

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data


@st.cache_data(ttl=3600)
def get_company_info(symbol):
    try:
        return yf.Ticker(symbol).info
    except:
        return {}
    
st.set_page_config(
    page_title="Real-Time Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

# AUTO REFRESH

st_autorefresh(
    interval=30000,
    key="refresh"
)

# TITLE

st.caption(
    "Live market analytics with technical indicators, portfolio tracking and interactive charts."
)



# SIDEBAR

st.sidebar.header("📊 Stock Selection")

stock_symbol = st.sidebar.selectbox(
    "Choose Stock",
    [
        "AAPL",
        "MSFT",
        "GOOG",
        "TSLA",
        "NVDA",
        "AMZN",
        "META",
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "SBIN.NS",
        "HDFCBANK.NS"
    ]
)

st.sidebar.markdown("---")

st.sidebar.header("💼 Portfolio Tracker")

shares = st.sidebar.number_input(
    "Number of Shares",
    min_value=1,
    value=10
)

buy_price = st.sidebar.number_input(
    "Buy Price",
    value=100.0
)

# DATA DOWNLOAD

data = load_stock_data(stock_symbol)

# COMPANY INFO
try:
    ticker = yf.Ticker(stock_symbol)

    info = ticker.info

    company_name = info.get(
        "longName",
        stock_symbol
    )

    market_cap = info.get(
        "marketCap",
        None
    )

    pe_ratio = info.get(
        "trailingPE",
        "N/A"
    )

except:
    company_name = stock_symbol
    market_cap = None
    pe_ratio = "N/A"
    info = {}

st.subheader(company_name)

# PRICE DATA

if len(data) >= 2:
    current_price = float(data["Close"].iloc[-1])
    previous_price = float(data["Close"].iloc[-2])
else:
    current_price = float(data["Close"].iloc[-1])
    previous_price = current_price

change = current_price - previous_price

percent_change = (
    (change / previous_price) * 100
)

# KPI CARDS

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Current Price",
        f"${current_price:.2f}"
    )

with col2:
    st.metric(
        "Daily Change",
        f"{percent_change:.2f}%"
    )

with col3:
    st.metric(
        "Day High",
        f"${float(data['High'].iloc[-1]):.2f}"
    )

with col4:
    st.metric(
        "Volume",
        f"{int(data['Volume'].iloc[-1]):,}"
    )

# COMPANY STATS



c1, c2, c3, c4 = st.columns(4)

with c1:

    if market_cap:

        st.metric(
            "Market Cap",
            f"${market_cap/1e9:.2f} B"
        )

    else:

        st.metric(
            "Market Cap",
            "N/A"
        )

with c2:

    st.metric(
        "PE Ratio",
        str(pe_ratio)
    )

with c3:

    st.metric(
        "52 Week High",
        f"${data['High'].max():.2f}"
    )

with c4:

    st.metric(
        "52 Week Low",
        f"${data['Low'].min():.2f}"
    )

st.markdown("---")

# PORTFOLIO PERFORMANCE

portfolio_value = shares * current_price

investment = shares * buy_price

profit = portfolio_value - investment

profit_pct = (
    (profit / investment) * 100
)

st.subheader("💼 Portfolio Performance")

p1, p2, p3 = st.columns(3)

with p1:
    st.metric(
        "Current Value",
        f"${portfolio_value:,.2f}"
    )

with p2:
    st.metric(
        "Profit / Loss",
        f"${profit:,.2f}"
    )

with p3:
    st.metric(
        "Return %",
        f"{profit_pct:.2f}%"
    )

st.markdown("---")

# TABS

tab1, tab2, tab3 = st.tabs(
    [
        "📊 Charts",
        "📈 Indicators",
        "📋 Data"
    ]
)

# CHART TAB

with tab1:

    st.subheader("Candlestick Chart")

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"]
            )
        ]
    )

    fig.update_layout(
    template="plotly_dark",
    height=700,
    xaxis_rangeslider_visible=False,
    uirevision=True
)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# INDICATORS TAB

with tab2:

    data["MA20"] = (
        data["Close"]
        .rolling(20)
        .mean()
    )

    data["MA50"] = (
        data["Close"]
        .rolling(50)
        .mean()
    )

    st.subheader(
        "Moving Average Analysis"
    )

    fig_ma = go.Figure()

    fig_ma.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Close"],
            name="Close Price"
        )
    )

    fig_ma.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA20"],
            name="20 Day MA"
        )
    )

    fig_ma.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA50"],
            name="50 Day MA"
        )
    )

    fig_ma.update_layout(
    template="plotly_dark",
    height=600,
    uirevision=True
)

    st.plotly_chart(
        fig_ma,
        use_container_width=True
    )

    # RSI

    delta = data["Close"].diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    avg_gain = gain.rolling(
        14
    ).mean()

    avg_loss = loss.rolling(
        14
    ).mean()

    rs = avg_gain / avg_loss

    data["RSI"] = (
        100 - (
            100 / (1 + rs)
        )
    )

    st.subheader(
        "RSI Indicator"
    )

    fig_rsi = go.Figure()

    fig_rsi.add_trace(
        go.Scatter(
            x=data.index,
            y=data["RSI"],
            name="RSI"
        )
    )

    fig_rsi.add_hline(y=70)
    fig_rsi.add_hline(y=30)

    fig_rsi.update_layout(
    template="plotly_dark",
    height=400,
    uirevision=True
)

    st.plotly_chart(
        fig_rsi,
        use_container_width=True
    )

    # SIGNAL

    st.subheader(
        "Trading Signal"
    )

    ma20 = data["MA20"].iloc[-1]
    ma50 = data["MA50"].iloc[-1]
if ma20 > ma50:
    st.success(
        "🟢 BUY SIGNAL - Short-term trend is stronger than long-term trend."
    )

elif ma20 < ma50:
    st.error(
        "🔴 SELL SIGNAL - Short-term trend is weaker than long-term trend."
    )

else:
    st.warning(
        "🟡 HOLD - Trend is neutral."
    )

# DATA TAB


with tab3:

    st.subheader(
        "Volume Analysis"
    )

    fig_vol = go.Figure()

    fig_vol.add_trace(
        go.Bar(
            x=data.index,
            y=data["Volume"],
            name="Volume"
        )
    )

    fig_vol.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(
        fig_vol,
        use_container_width=True
    )

    st.subheader(
        "Recent Market Data"
    )

    st.dataframe(
        data.tail(20),
        use_container_width=True
    )

    csv = data.to_csv().encode()

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"{stock_symbol}.csv",
        mime="text/csv"
    )

    st.subheader(
        "Statistical Summary"
    )

    st.dataframe(
        data.describe(),
        use_container_width=True
    )

