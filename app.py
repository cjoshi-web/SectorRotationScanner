import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import logging
import sys
import os
import io
import time
from datetime import datetime

# --- Setup ---
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")
sys.stderr = open(os.devnull, 'w')

# =============================================================
# PAGE CONFIG & CUSTOM CSS
# =============================================================
st.set_page_config(
    page_title="Ultimate ETF Scanner",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern look
st.markdown("""
<style>
    /* Global styles */
    .main {
        background: #f0f2f6;
        padding: 0px;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Card style */
    .css-1r6slb0 {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        padding: 20px;
        margin-bottom: 20px;
    }
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        padding: 1.2rem;
        text-align: center;
        border-left: 5px solid #4CAF50;
    }
    .metric-card .label {
        font-size: 0.9rem;
        color: #666;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-top: 0.2rem;
        color: #1a1a1a;
    }
    /* Header */
    .app-header {
        background: linear-gradient(135deg, #1e2a6b, #3b4a8f);
        padding: 1.5rem 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .app-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .app-header .subtitle {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    /* Dataframe */
    .dataframe-container {
        background: white;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        overflow-x: auto;
    }
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
    }
    /* Buttons */
    .stButton button {
        border-radius: 25px;
        font-weight: 600;
        background: #1e2a6b;
        color: white;
        border: none;
        transition: 0.2s;
    }
    .stButton button:hover {
        background: #3b4a8f;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# =============================================================
# 1. STATIC ETF LIST & MAPPING (EXACT ORIGINAL)
# =============================================================
ETF_LIST = [
    "LIQUIDCASE", "GROWWLIQID", "NIFTYBEES", "MOSMALL250", "SMALLCAP",
    "MIDCAPETF", "NEXT50IETF", "TOP100CASE", "MONIFTY500", "AONETOTAL",
    "MIDSMALL", "SENSEXETF", "PVTBANIETF", "PSUBNKBEES", "BANKBEES",
    "FINIETF", "TATSILV", "TATAGOLD", "ITBEES", "PHARMABEES",
    "METALIETF", "GROWWPOWER", "FMCGIETF", "CPSEETF", "AUTOIETF",
    "MOREALTY", "OILIETF", "ENERGY", "HEALTHY", "CONSUMBEES",
    "ABSLPSE", "INFRAIETF", "MANUFGBEES", "MON100", "HNGSNGBEES",
    "ALPHA", "MOMENTUM30", "ALPL30IETF", "HDFCGROWTH", "LOWVOLIETF",
    "MOMENTUM50", "VAL30IETF", "NV20IETF", "ALPHAETF", "MULTICAP",
    "FLEXIADD", "QUAL30IETF", "DIVOPPBEES", "MODEFENCE", "GROWWRAIL",
    "EVINDIA", "TNIDETF", "GROWWCHEM", "INTERNET"
]

ETF_SECTOR_MAP = {
    "LIQUIDCASE": "Liquid", "GROWWLIQID": "Liquid",
    "NIFTYBEES": "Nifty 50", "MOSMALL250": "Smallcap 250",
    "SMALLCAP": "Smallcap", "MIDCAPETF": "Midcap 150",
    "NEXT50IETF": "Next 50", "TOP100CASE": "Nifty 100",
    "MONIFTY500": "Nifty 500", "AONETOTAL": "Total Market",
    "MIDSMALL": "Mid & Small", "SENSEXETF": "Sensex",
    "PVTBANIETF": "Banks-Pvt", "PSUBNKBEES": "Banks-Govt",
    "BANKBEES": "Banks-Ovrl", "FINIETF": "Fin Services",
    "TATSILV": "Silver", "TATAGOLD": "Gold",
    "ITBEES": "IT", "PHARMABEES": "Pharma",
    "METALIETF": "Metal", "GROWWPOWER": "Power",
    "FMCGIETF": "FMCG", "CPSEETF": "Govt Sector",
    "AUTOIETF": "Auto", "MOREALTY": "Real Estate",
    "OILIETF": "Oil & Gas", "ENERGY": "Energy",
    "HEALTHY": "Health", "CONSUMBEES": "Consumer",
    "ABSLPSE": "PSU", "INFRAIETF": "Infra",
    "MANUFGBEES": "Manufacturing", "MON100": "US Market",
    "HNGSNGBEES": "China Market", "ALPHA": "Alpha",
    "MOMENTUM30": "Mom 30", "ALPL30IETF": "Alpha Low Vol",
    "HDFCGROWTH": "Growth", "LOWVOLIETF": "Low Vol",
    "MOMENTUM50": "Mom 50", "VAL30IETF": "Value",
    "NV20IETF": "NV20", "ALPHAETF": "Alpha Str",
    "MULTICAP": "Multi Cap", "FLEXIADD": "Flexi Cap",
    "QUAL30IETF": "Quality", "DIVOPPBEES": "Dividend",
    "MODEFENCE": "Defence", "GROWWRAIL": "Railway",
    "EVINDIA": "EV", "TNIDETF": "Digital",
    "GROWWCHEM": "Chemicals", "INTERNET": "Internet"
}

MACRO_SECTOR_MAP = {
    "LIQUIDCASE": "Liquid / Cash",
    "GROWWLIQID": "Liquid / Cash",
    "NIFTYBEES": "Broad Market",
    "MOSMALL250": "Broad Market",
    "SMALLCAP": "Broad Market",
    "MIDCAPETF": "Broad Market",
    "NEXT50IETF": "Broad Market",
    "TOP100CASE": "Broad Market",
    "MONIFTY500": "Broad Market",
    "AONETOTAL": "Broad Market",
    "MIDSMALL": "Broad Market",
    "SENSEXETF": "Broad Market",
    "PVTBANIETF": "Financial Services",
    "PSUBNKBEES": "Financial Services",
    "BANKBEES": "Financial Services",
    "FINIETF": "Financial Services",
    "TATSILV": "Commodities",
    "TATAGOLD": "Commodities",
    "ITBEES": "Information Technology",
    "PHARMABEES": "Healthcare",
    "METALIETF": "Commodities",
    "GROWWPOWER": "Utilities",
    "FMCGIETF": "Consumer Staples",
    "CPSEETF": "Utilities",
    "AUTOIETF": "Consumer Discretionary",
    "MOREALTY": "Real Estate",
    "OILIETF": "Energy",
    "ENERGY": "Energy",
    "HEALTHY": "Healthcare",
    "CONSUMBEES": "Consumer Discretionary",
    "ABSLPSE": "Thematic / Special",
    "INFRAIETF": "Industrials",
    "MANUFGBEES": "Thematic / Special",
    "MON100": "Global Indices",
    "HNGSNGBEES": "Global Indices",
    "ALPHA": "Factor / Strategy",
    "MOMENTUM30": "Factor / Strategy",
    "ALPL30IETF": "Factor / Strategy",
    "HDFCGROWTH": "Factor / Strategy",
    "LOWVOLIETF": "Factor / Strategy",
    "MOMENTUM50": "Factor / Strategy",
    "VAL30IETF": "Factor / Strategy",
    "NV20IETF": "Factor / Strategy",
    "ALPHAETF": "Factor / Strategy",
    "MULTICAP": "Broad Market",
    "FLEXIADD": "Factor / Strategy",
    "QUAL30IETF": "Factor / Strategy",
    "DIVOPPBEES": "Factor / Strategy",
    "MODEFENCE": "Thematic / Special",
    "GROWWRAIL": "Thematic / Special",
    "EVINDIA": "Thematic / Special",
    "TNIDETF": "Thematic / Special",
    "GROWWCHEM": "Commodities",
    "INTERNET": "Thematic / Special"
}

SCAN_ETFS = [e for e in ETF_LIST if e not in ["LIQUIDCASE", "GROWWLIQID"]]

# =============================================================
# 2. HELPER FUNCTIONS (EXACT ORIGINAL)
# =============================================================
def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def supertrend(high, low, close, period=10, multiplier=3):
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    hl2 = (high + low) / 2
    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr
    trend = pd.Series(1, index=close.index)
    for i in range(1, len(close)):
        if close.iloc[i] > upper.iloc[i-1]: trend.iloc[i] = 1
        elif close.iloc[i] < lower.iloc[i-1]: trend.iloc[i] = -1
        else: trend.iloc[i] = trend.iloc[i-1]
    return trend

def get_obv(close, volume):
    return (np.sign(close.diff()) * volume).cumsum()

def calculate_cvd(open_, high, low, close, volume):
    range_ = high - low
    range_ = range_.replace(0, 1)
    return volume * (close - open_) / range_

def check_car(close):
    if len(close) < 60: return False
    car = close.expanding().mean()
    if len(car) < 10: return False
    return all(car.iloc[-10:].diff().dropna() > 0)

def calculate_macd(close):
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    return exp1 - exp2

def calculate_adx(high, low, close, period=14):
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(span=period, min_periods=period).mean()
    plus_di = 100 * (plus_dm.ewm(span=period, min_periods=period).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(span=period, min_periods=period).mean() / atr)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.ewm(span=period, min_periods=period).mean()
    return adx

def vol_surge_rising(close, high, low, volume, open_):
    if len(volume) < 20: return False
    avg_20 = volume.rolling(20).mean().iloc[-1]
    if avg_20 == 0: return False
    surge = volume.iloc[-1] / avg_20
    rising = (volume.iloc[-5:].mean() / volume.iloc[-20:].mean()) > 1.0
    return (surge > 1.2) and rising

def up_down_ratio(close, high, low, volume, open_):
    if len(volume) < 5: return False
    up_vol = volume[(close - open_) > 0].iloc[-5:].mean() if len(volume[(close - open_) > 0]) > 0 else 0
    down_vol = volume[(close - open_) < 0].iloc[-5:].mean() if len(volume[(close - open_) < 0]) > 0 else 0
    return up_vol > down_vol

def obv_slope(close, high, low, volume, open_):
    if len(close) < 5: return False
    obv = get_obv(close, volume)
    return obv.iloc[-1] > obv.iloc[-5]

def cvd_positive(close, high, low, volume, open_):
    if len(close) < 5: return False
    cvd = calculate_cvd(open_, high, low, close, volume)
    return cvd.iloc[-5:].sum() > 0

# =============================================================
# 3. MAIN SCAN FUNCTION (with caching)
# =============================================================
@st.cache_data(ttl=3600)  # cache for 1 hour
def run_scan_cached():
    """Run the scan and return results and macro_avg."""
    results = []
    total_etfs = len(SCAN_ETFS)
    warning_messages = []
    
    # Load Nifty
    try:
        nifty_df = yf.download("^NSEI", period="2y", progress=False)
        if isinstance(nifty_df.columns, pd.MultiIndex):
            nifty_df.columns = nifty_df.columns.get_level_values(0)
        nifty_close = nifty_df['Close'].dropna()
        if nifty_close.empty:
            raise ValueError("Nifty data is empty")
    except:
        nifty_close = pd.Series([1.0] * 500, 
                                index=pd.date_range(end=pd.Timestamp.today(), periods=500, freq='D'))
        warning_messages.append("⚠️ Nifty 50 not available, using fallback benchmark.")
    
    for idx, etf_base in enumerate(SCAN_ETFS):
        # For progress tracking we use a global progress bar outside this function
        # We'll just update a variable
        try:
            symbol = etf_base + ".NS"
            df = yf.download(symbol, period="max", progress=False)
            if df.empty:
                warning_messages.append(f"⚠️ {etf_base}: No data.")
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            if 'Close' not in df.columns:
                if 'Adj Close' in df.columns:
                    df['Close'] = df['Adj Close']
                else:
                    warning_messages.append(f"⚠️ {etf_base}: No close.")
                    continue

            for col in ['Open', 'High', 'Low']:
                if col not in df.columns:
                    df[col] = df['Close']
            
            if 'Volume' not in df.columns or df['Volume'].isnull().all():
                df['Volume'] = 1
            
            df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
            if len(df) < 20:
                warning_messages.append(f"⚠️ {etf_base}: Only {len(df)} days.")
                continue

            close = df['Close']; high = df['High']; low = df['Low']; open_ = df['Open']; volume = df['Volume']
            common = close.index.intersection(high.index).intersection(low.index).intersection(volume.index)
            if len(common) < 20: continue
            close = close.loc[common]; high = high.loc[common]; low = low.loc[common]; open_ = open_.loc[common]; volume = volume.loc[common]

            # Resample with 'ME' for month end
            w_df = df.resample('W').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
            m_df = df.resample('ME').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
            if len(w_df) < 10 or len(m_df) < 3: continue

            w_close = w_df['Close']; w_high = w_df['High']; w_low = w_df['Low']; w_vol = w_df['Volume']; w_open = w_df['Open']
            m_close = m_df['Close']; m_high = m_df['High']; m_low = m_df['Low']; m_vol = m_df['Volume']; m_open = m_df['Open']

            # RRG
            rs_ratio = close / nifty_close.reindex(close.index, method='ffill')
            rs_ratio_norm = rs_ratio / rs_ratio.rolling(100, min_periods=10).mean()
            rs_mom = rs_ratio / rs_ratio.shift(20) - 1
            current_rs = rs_ratio_norm.iloc[-1] if len(rs_ratio_norm) > 0 else 1
            current_rs_mom = rs_mom.iloc[-1] if len(rs_mom) > 0 else 0

            if current_rs > 1 and current_rs_mom > 0:
                rrg_text = "Bullish (Leading)"; rrg_improving = False
            elif current_rs < 1 and current_rs_mom > 0:
                rrg_text = "Entering a bull market (Improving)"; rrg_improving = True
            elif current_rs < 1 and current_rs_mom < 0:
                rrg_text = "Bearish (Lagging)"; rrg_improving = False
            elif current_rs > 1 and current_rs_mom < 0:
                rrg_text = "Entering a bear market (Weakening)"; rrg_improving = False
            else:
                rrg_text = "Neutral"; rrg_improving = False

            f2_rv = False
            if len(rs_ratio) > 200:
                if rs_ratio.iloc[-1] < rs_ratio.rolling(200).mean().iloc[-1]:
                    f2_rv = True
            rv_text = "Low Price Compared to Nifty" if f2_rv else "High Price Compared to Nifty"

            w_rsi = calculate_rsi(w_close).iloc[-1] if len(w_close) >= 15 else 50
            m_rsi = calculate_rsi(m_close).iloc[-1] if len(m_close) >= 12 else 50
            f3 = w_rsi > 50
            f4 = 50 < m_rsi < 55
            f5 = supertrend(w_high, w_low, w_close).iloc[-1] == 1 if len(close) >= 75 else False
            f6 = supertrend(m_high, m_low, m_close).iloc[-1] == 1 if len(close) >= 250 else False
            ret_1m = ((close.iloc[-1] / close.iloc[-22]) - 1) * 100 if len(close) >= 22 else np.nan
            ret_3m = ((close.iloc[-1] / close.iloc[-66]) - 1) * 100 if len(close) >= 66 else np.nan
            f7 = ret_1m > 0 if not np.isnan(ret_1m) else False
            f8 = ret_3m > 0 if not np.isnan(ret_3m) else False

            accel = (ret_1m - ret_3m) if not np.isnan(ret_1m) and not np.isnan(ret_3m) else np.nan
            f9_accel = accel > 2 if not np.isnan(accel) else False
            macd_w = calculate_macd(w_close).iloc[-1] if len(w_close) > 26 else 0
            f9_macd_w = macd_w > 0
            macd_m = calculate_macd(m_close).iloc[-1] if len(m_close) > 26 else 0
            f9_macd_m = macd_m > 0
            adx_w = calculate_adx(w_high, w_low, w_close).iloc[-1] if len(w_close) > 14 else 0
            f9_adx_w = adx_w > 25 if not np.isnan(adx_w) else False
            adx_m = calculate_adx(m_high, m_low, m_close).iloc[-1] if len(m_close) > 14 else 0
            f9_adx_m = adx_m > 25 if not np.isnan(adx_m) else False

            f10 = all([w_close.iloc[-1] > w_close.rolling(20).mean().iloc[-1],
                       w_close.iloc[-1] > w_close.rolling(50).mean().iloc[-1],
                       w_close.iloc[-1] > w_close.rolling(100).mean().iloc[-1]]) if len(w_close) >= 100 else False
            f11 = all([m_close.iloc[-1] > m_close.rolling(20).mean().iloc[-1],
                       m_close.iloc[-1] > m_close.rolling(50).mean().iloc[-1],
                       m_close.iloc[-1] > m_close.rolling(100).mean().iloc[-1]]) if len(m_close) >= 100 else False
            f12 = (close.iloc[-1] > close.rolling(120).max().iloc[-1] * 0.97 and
                   close.iloc[-1] > close.rolling(20).mean().iloc[-1]) if len(close) >= 120 else False

            f13_d = vol_surge_rising(close, high, low, volume, open_)
            f13_w = vol_surge_rising(w_close, w_high, w_low, w_vol, w_open)
            f13_m = vol_surge_rising(m_close, m_high, m_low, m_vol, m_open)
            f14 = up_down_ratio(close, high, low, volume, open_) and \
                  up_down_ratio(w_close, w_high, w_low, w_vol, w_open) and \
                  up_down_ratio(m_close, m_high, m_low, m_vol, m_open)
            f15 = obv_slope(close, high, low, volume, open_) and \
                  obv_slope(w_close, w_high, w_low, w_vol, w_open) and \
                  obv_slope(m_close, m_high, m_low, m_vol, m_open)
            f16 = cvd_positive(close, high, low, volume, open_) and \
                  cvd_positive(w_close, w_high, w_low, w_vol, w_open) and \
                  cvd_positive(m_close, m_high, m_low, m_vol, m_open)

            f17 = False
            if len(close) >= 90:
                price_flat = abs((close.iloc[-1] / close.iloc[-60]) - 1) < 0.05
                obv = get_obv(close, volume)
                vol_rising = (volume.iloc[-5:].mean() / volume.iloc[-30:-5].mean()) > 1.2
                if price_flat and obv.iloc[-1] > obv.iloc[-60] and vol_rising:
                    f17 = True

            f18 = check_car(close)
            f19 = check_car(w_close) if len(w_close) >= 60 else False
            f20 = check_car(m_close) if len(m_close) >= 60 else False

            filters_list = [f3, f4, f5, f6, f7, f8,
                            f9_accel, f9_macd_w, f9_macd_m, f9_adx_w, f9_adx_m,
                            f10, f11, f12,
                            f13_d, f13_w, f13_m,
                            f14, f15, f16, f17,
                            f18, f19, f20]
            total_score = sum(filters_list)

            sector = ETF_SECTOR_MAP.get(etf_base, etf_base)
            macro_sector = MACRO_SECTOR_MAP.get(etf_base, "Other")
            results.append({
                'ETF': etf_base, 'Sector': sector, 'Macro_Sector': macro_sector,
                'RRG_Text': rrg_text, 'RV_Text': rv_text,
                'RRG_Improving': rrg_improving, 'RV_Undervalued': f2_rv,
                'Total_Score': total_score,
                'F3': f3, 'F4': f4, 'F5': f5, 'F6': f6,
                'F7': f7, 'F8': f8,
                'F9_Accel': f9_accel, 'F9_MACD_W': f9_macd_w, 'F9_MACD_M': f9_macd_m,
                'F9_ADX_W': f9_adx_w, 'F9_ADX_M': f9_adx_m,
                'F10': f10, 'F11': f11, 'F12': f12,
                'F13_D': f13_d, 'F13_W': f13_w, 'F13_M': f13_m,
                'F14': f14, 'F15': f15, 'F16': f16, 'F17': f17,
                'F18': f18, 'F19': f19, 'F20': f20,
                'RS_Ratio': current_rs, 'RS_Momentum': current_rs_mom,
                'W_RSI_Val': round(w_rsi,1), 'M_RSI_Val': round(m_rsi,1),
                '1M_Ret': round(ret_1m, 2) if not np.isnan(ret_1m) else np.nan,
                '3M_Ret': round(ret_3m, 2) if not np.isnan(ret_3m) else np.nan,
                'Accel_Val': round(accel, 2) if not np.isnan(accel) else np.nan,
                'Risk': 'Near Top' if (close.iloc[-1] / close.rolling(252).max().iloc[-1]) > 0.95 else 'Safe'
            })
        except Exception as e:
            warning_messages.append(f"❌ Error in {etf_base}: {str(e)[:100]}")

    if not results:
        return None, None, warning_messages

    # Build final dataframe
    df = pd.DataFrame(results)

    # Icons
    df['F3_Icon'] = df['F3'].apply(lambda x: '✅' if x else '❌')
    df['F4_Icon'] = df['F4'].apply(lambda x: '✅' if x else '❌')
    df['F7_Icon'] = df['F7'].apply(lambda x: '✅' if x else '❌')
    df['F8_Icon'] = df['F8'].apply(lambda x: '✅' if x else '❌')
    for col, icon_true, icon_false in [('F5', '🟢', '🔴'), ('F6', '🟢', '🔴'),
                                       ('F10', '🟢', '🔴'), ('F11', '🟢', '🔴'),
                                       ('F12', '🟢', '🔴'),
                                       ('F15', '🟢', '🔴'), ('F16', '🟢', '🔴'),
                                       ('F18', '🟢', '🔴'), ('F19', '🟢', '🔴'), ('F20', '🟢', '🔴')]:
        df[col+'_Icon'] = df[col].apply(lambda x: icon_true if x else icon_false)
    df['F9_Accel_Icon'] = df['F9_Accel'].apply(lambda x: '🚀' if x else '💤')
    df['F9_MACD_W_Icon'] = df['F9_MACD_W'].apply(lambda x: '🚀' if x else '💤')
    df['F9_MACD_M_Icon'] = df['F9_MACD_M'].apply(lambda x: '🚀' if x else '💤')
    df['F9_ADX_W_Icon'] = df['F9_ADX_W'].apply(lambda x: '🚀' if x else '💤')
    df['F9_ADX_M_Icon'] = df['F9_ADX_M'].apply(lambda x: '🚀' if x else '💤')
    df['F13_D_Icon'] = df['F13_D'].apply(lambda x: '✅' if x else '❌')
    df['F13_W_Icon'] = df['F13_W'].apply(lambda x: '✅' if x else '❌')
    df['F13_M_Icon'] = df['F13_M'].apply(lambda x: '✅' if x else '❌')
    df['F14_Icon'] = df['F14'].apply(lambda x: '✅' if x else '❌')
    df['F17_Icon'] = df['F17'].apply(lambda x: '✅' if x else '❌')

    # Sorting
    rrg_priority_map = {
        "Entering a bull market (Improving)": 1,
        "Bullish (Leading)": 2,
        "Entering a bear market (Weakening)": 3,
        "Bearish (Lagging)": 4,
        "Neutral": 5
    }
    df['RRG_Priority'] = df['RRG_Text'].map(rrg_priority_map).fillna(5)
    df['RV_Priority'] = df['RV_Text'].apply(lambda x: 1 if x == "Low Price Compared to Nifty" else 2)
    df = df.sort_values(['RRG_Priority', 'RV_Priority', 'Total_Score'], ascending=[True, True, False])
    df = df.reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = 'Sr. #'

    # Result columns
    df['Benchmark Result'] = df.apply(
        lambda row: "🏆 Golden Chance" if (row['RRG_Improving'] and row['RV_Undervalued']) else "-", axis=1
    )
    def trend_result(row):
        names, flags = ['RSI_W','RSI_M','ST_W','ST_M'], [row['F3'], row['F4'], row['F5'], row['F6']]
        true_names = [n for n, f in zip(names, flags) if f]
        return f"{len(true_names)}/4 True ({', '.join(true_names)})" if true_names else "0/4 True"
    df['Trend Result'] = df.apply(trend_result, axis=1)
    def momentum_result(row):
        names = ['Accel','MACD_W','MACD_M','ADX_W','ADX_M']
        flags = [row['F9_Accel'], row['F9_MACD_W'], row['F9_MACD_M'], row['F9_ADX_W'], row['F9_ADX_M']]
        true_names = [n for n, f in zip(names, flags) if f]
        return f"{len(true_names)}/5 True ({', '.join(true_names)})" if true_names else "0/5 True"
    df['Momentum Result'] = df.apply(momentum_result, axis=1)
    def structure_result(row):
        names, flags = ['SMA_W','SMA_M'], [row['F10'], row['F11']]
        true_names = [n for n, f in zip(names, flags) if f]
        return f"{len(true_names)}/2 True ({', '.join(true_names)})" if true_names else "0/2 True"
    df['Structure Result'] = df.apply(structure_result, axis=1)
    df['Breakout Result'] = df['F12'].apply(lambda x: "✅ True" if x else "-")
    def volume_result(row):
        names = ['Vol_D','Vol_W','Vol_M','Up/Dn','OBV','CVD','Accum']
        flags = [row['F13_D'], row['F13_W'], row['F13_M'], row['F14'], row['F15'], row['F16'], row['F17']]
        true_names = [n for n, f in zip(names, flags) if f]
        return f"{len(true_names)}/7 True ({', '.join(true_names)})" if true_names else "0/7 True"
    df['Volume Result'] = df.apply(volume_result, axis=1)
    df['Smart Money Result'] = df['F17'].apply(lambda x: "💰 Buying" if x else "-")
    def reversal_result(row):
        names, flags = ['CAR_D','CAR_W','CAR_M'], [row['F18'], row['F19'], row['F20']]
        true_names = [n for n, f in zip(names, flags) if f]
        return f"{len(true_names)}/3 True ({', '.join(true_names)})" if true_names else "0/3 True"
    df['Reversal Result'] = df.apply(reversal_result, axis=1)

    # Final columns
    rename_map = {
        'RRG_Text': 'RRG - (Sector v/s Nifty)',
        'RV_Text': 'RV (Sector v/s Nifty)',
        'Total_Score': 'Filter_Score',
        'F3_Icon': 'Trend_RSI_W > 50',
        'F4_Icon': 'Trend_RSI_M > 50-55',
        'F5_Icon': 'Trend_ST_W > Bull',
        'F6_Icon': 'Trend_ST_M > Bull',
        'F7_Icon': 'Trend_1M > 0',
        'F8_Icon': 'Trend_3M > 0',
        'F9_Accel_Icon': 'Momentum > 2% (1M%-3M%)',
        'F9_MACD_W_Icon': 'Momentum = MACD > 0 _W',
        'F9_MACD_M_Icon': 'Momentum = MACD > 0 _M',
        'F9_ADX_W_Icon': 'Momentum = ADX > 25_W',
        'F9_ADX_M_Icon': 'Momentum = ADX > 25_M',
        'F10_Icon': 'RGB_Price_W > 20,50,100 SMA',
        'F11_Icon': 'RGB_Price_M > 20,50,100 SMA',
        'F12_Icon': 'Breakout_Price_Of_6M',
        'F13_D_Icon': 'Institutional_Buying_Vol Surge_D',
        'F13_W_Icon': 'Institutional_Buying_Vol Surge_W',
        'F13_M_Icon': 'Institutional_Buying_Vol Surge_M',
        'F14_Icon': 'Buyers > Sellers - Up/Down Vol',
        'F15_Icon': 'Whale Accumulation_OBV Slope',
        'F16_Icon': 'Buyers > Sellers - CVD',
        'F17_Icon': 'Volume Result (OBV)',
        'F18_Icon': 'Trend_Reversal_CAR_D',
        'F19_Icon': 'Trend_Reversal_CAR_W',
        'F20_Icon': 'Trend_Reversal_CAR_M'
    }
    display_df = df.rename(columns=rename_map)
    final_cols = [
        'ETF', 'Sector',
        'RRG - (Sector v/s Nifty)',
        'RV (Sector v/s Nifty)',
        'Filter_Score',
        'Trend_RSI_W > 50',
        'Trend_RSI_M > 50-55',
        'Trend_ST_W > Bull',
        'Trend_ST_M > Bull',
        'Trend_1M > 0',
        'Trend_3M > 0',
        'Momentum > 2% (1M%-3M%)',
        'Momentum = MACD > 0 _W',
        'Momentum = MACD > 0 _M',
        'Momentum = ADX > 25_W',
        'Momentum = ADX > 25_M',
        'RGB_Price_W > 20,50,100 SMA',
        'RGB_Price_M > 20,50,100 SMA',
        'Breakout_Price_Of_6M',
        'Institutional_Buying_Vol Surge_D',
        'Institutional_Buying_Vol Surge_W',
        'Institutional_Buying_Vol Surge_M',
        'Buyers > Sellers - Up/Down Vol',
        'Whale Accumulation_OBV Slope',
        'Buyers > Sellers - CVD',
        'Volume Result (OBV)',
        'Trend_Reversal_CAR_D',
        'Trend_Reversal_CAR_W',
        'Trend_Reversal_CAR_M',
        'Benchmark Result',
        'Trend Result',
        'Momentum Result',
        'Structure Result',
        'Breakout Result',
        'Volume Result',
        'Smart Money Result',
        'Reversal Result'
    ]
    for col in final_cols:
        if col not in display_df.columns:
            display_df[col] = '-'
    display_df = display_df[final_cols]

    # Macro avg
    macro_avg = df.groupby('Macro_Sector').agg({
        'RS_Ratio': 'mean',
        'RS_Momentum': 'mean'
    }).reset_index()

    return display_df, macro_avg, warning_messages

# =============================================================
# 4. AUTO-RUN LOGIC
# =============================================================
# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.display_df = None
    st.session_state.macro_avg = None
    st.session_state.warnings = []

# If data not loaded, run scan automatically
if not st.session_state.data_loaded:
    with st.spinner("🚀 Scanning all ETFs... This may take 30-60 seconds."):
        display_df, macro_avg, warnings_list = run_scan_cached()
        if display_df is not None:
            st.session_state.display_df = display_df
            st.session_state.macro_avg = macro_avg
            st.session_state.warnings = warnings_list
            st.session_state.data_loaded = True
            st.rerun()
        else:
            st.error("❌ No data found. Please check your internet connection or try again later.")
            st.stop()

# =============================================================
# 5. DISPLAY MODERN UI
# =============================================================
display_df = st.session_state.display_df
macro_avg = st.session_state.macro_avg
warnings_list = st.session_state.warnings

# Header
st.markdown("""
<div class="app-header">
    <div>
        <h1>📈 Ultimate ETF Scanner</h1>
        <div class="subtitle">23 Filters + Macro Sector RRG • Auto-updated daily</div>
    </div>
    <div style="font-size: 0.9rem; opacity: 0.8;">
        Last scan: {}
    </div>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #4CAF50;">
        <div class="label">Total ETFs Scanned</div>
        <div class="value">{len(display_df)}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    avg_score = display_df['Filter_Score'].mean()
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #2196F3;">
        <div class="label">Average Filter Score</div>
        <div class="value">{avg_score:.1f}/23</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    top_score = display_df['Filter_Score'].max()
    top_etf = display_df[display_df['Filter_Score']==top_score]['ETF'].values[0] if top_score>0 else 'N/A'
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #FF9800;">
        <div class="label">Best Score</div>
        <div class="value">{top_score} <span style="font-size:1rem;">({top_etf})</span></div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    golden = len(display_df[display_df['Benchmark Result']=='🏆 Golden Chance'])
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #E91E63;">
        <div class="label">Golden Chances</div>
        <div class="value">{golden}</div>
    </div>
    """, unsafe_allow_html=True)

# Warnings (if any)
if warnings_list:
    with st.expander("⚠️ Warnings (click to expand)", expanded=False):
        for w in warnings_list[:20]:
            st.write(w)
        if len(warnings_list)>20:
            st.write(f"... and {len(warnings_list)-20} more.")

# Main Table
st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
st.dataframe(display_df, use_container_width=True, height=500)
st.markdown('</div>', unsafe_allow_html=True)

# Download button
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    display_df.to_excel(writer, sheet_name='ETF Ranking', index=True)
    if macro_avg is not None:
        macro_avg.to_excel(writer, sheet_name='Macro_RRG', index=False)
excel_buffer.seek(0)
st.download_button(
    label="⬇️ Download Excel Report",
    data=excel_buffer,
    file_name=f"ETF_Scan_{datetime.now().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

# RRG Chart
st.subheader("📊 RRG Chart – Macro Sector Averages")
st.caption("📌 દરેક Macro Sector (Broad Market, Financial Services, Commodities, વગેરે) માટે તેના બધા ETF નો સરેરાશ RS-Ratio અને RS-Momentum પ્લોટ થયેલ છે.")

if macro_avg is not None and not macro_avg.empty:
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax.axvline(x=1, color='black', linestyle='-', linewidth=1)

    ax.text(1.25, 0.08, '🏆 LEADING', fontsize=16, weight='bold', color='green',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='green', alpha=0.7))
    ax.text(0.75, 0.08, '🟢 IMPROVING', fontsize=16, weight='bold', color='blue',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='blue', alpha=0.7))
    ax.text(0.75, -0.15, '🔴 LAGGING', fontsize=16, weight='bold', color='red',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='red', alpha=0.7))
    ax.text(1.25, -0.15, '🟡 WEAKENING', fontsize=16, weight='bold', color='orange',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='orange', alpha=0.7))

    for idx, row in macro_avg.iterrows():
        x = row['RS_Ratio']
        y = row['RS_Momentum']
        sector = row['Macro_Sector']
        if x > 1 and y > 0:
            color, marker, edge = 'green', '^', 'darkgreen'
        elif x < 1 and y > 0:
            color, marker, edge = 'blue', 's', 'darkblue'
        elif x < 1 and y < 0:
            color, marker, edge = 'red', 'v', 'darkred'
        else:
            color, marker, edge = 'orange', 'o', 'darkorange'

        ax.scatter(x, y, color=color, s=300, marker=marker, edgecolors=edge, linewidth=2, zorder=5)
        ax.annotate(sector, (x, y), fontsize=11, weight='bold', xytext=(10, 10),
                    textcoords='offset points',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor='white', edgecolor='gray', alpha=0.9),
                    zorder=6)

    x_min = max(0.4, macro_avg['RS_Ratio'].min() - 0.15)
    x_max = min(1.6, macro_avg['RS_Ratio'].max() + 0.15)
    y_min = max(-0.4, macro_avg['RS_Momentum'].min() - 0.05)
    y_max = min(0.4, macro_avg['RS_Momentum'].max() + 0.05)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.set_title('📈 RRG (Relative Rotation Graph) – MACRO SECTOR AVERAGES', fontsize=18, weight='bold')
    ax.set_xlabel('Relative Strength (RS-Ratio) → 1 = Nifty Avg', fontsize=13)
    ax.set_ylabel('RS-Momentum (Speed of Change)', fontsize=13)
    ax.grid(True, linestyle='--', alpha=0.4)
    st.pyplot(fig)
else:
    st.info("No macro sector data available for RRG chart.")

# Refresh button (optional) – but not needed as auto runs on load
st.caption("🔄 Data is cached for 1 hour. Reload the page to refresh the scan.")
