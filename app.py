import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
import re

# --- 1. 頁面配置與 CSS (明亮工業風) ---
st.set_page_config(page_title="鑫龍工程維護系統", layout="centered", page_icon="🏗️")

st.markdown("""
    <style>
    /* 隱藏預設元件 */
    #MainMenu, footer, header {visibility: hidden;}

    /* 背景：質感水泥淺灰 */
    [data-testid="stAppViewContainer"] { background-color: #E5E7EB !important; }

    /* 文字：石墨深灰 */
    h1, h2, h3, p, span, label { color: #1F2937 !important; font-family: 'Inter', 'Noto Sans TC', sans-serif !important; }

    /* 卡片設計：純白背景 + 亮橘頂部飾條 */
    div[data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
        border-top: 8px solid #F59E0B !important; /* 工程亮橘 */
        box-shadow: 0 4px 20px rgba(0,0,0,0.08) !important;
        padding: 2.5rem !important;
    }

    /* 輸入框美化 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #F9FAFB !important;
        border-radius: 4px !important;
        border: 1px solid #D1D5DB !important;
    }

    /* 按鈕：工程亮橘 */
    div.stButton > button {
        background-color: #F59E0B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        height: 3rem !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #D97706 !important;
        transform: translateY(-2px) !important;
    }

    /* 數據表格 */
    [data-testid="stDataFrame"] { border-radius: 8px; border: 1px solid #D1D5DB; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Session State 初始化 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. 登入機制 ---
if not st.session_state.logged_in:
    st.markdown("<br><br><h1 style='text-align: center;'>🏗️ 鑫龍工程行</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280 !important;'>內部管理系統 - 請登入以繼續</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        u = st.text_input("帳號")
        p = st.text_input("密碼", type="password")
        if st.form_submit_button("登入系統"):
            if u == "admin" and p == "xinlong888": # 你可以自己改密碼
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("帳號或密碼錯誤")
    st.stop()

# --- 4. PDF 生成器 ---
class ModernPDF(FPDF):
    def header(self):
        self.set_fill_color(31, 41, 55)
        self.rect(0, 0, 210, 10, 'F')
    def footer(self):
        self.set_y(-15)
        self.set_font("CustomFont", "", 9) if os.path.exists("font.ttf") else self.set_font("helvetica", "", 9)
        self.cell(0, 10, "鑫龍工程行 - 官方證明文件", align='C')

def create_pdf(rec):
    pdf = ModernPDF()
    pdf.add_page()
    if os.path.exists("font.ttf"):
        pdf.add_font("CustomFont", "", "font.ttf")
        pdf.set_font("CustomFont", "", 12)
    else:
        pdf.set_font("helvetica", "", 12)

    pdf.ln(12)
    pdf.set_font_size(30); pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 20, "鑫 龍 工 程 行", ln=True, align='C')
    pdf.set_font_size(16); pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 10, "工 程 保 固 證 明 書", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_fill_color(249, 250, 251); pdf.set_draw_color(209, 213, 219)
    def add_row(label, value):
        pdf.set_x(30); pdf.set_text_color(75, 85, 99)
        pdf.cell(40, 14, f" {label}", border=1, fill=True)
        pdf.set_text_color(17, 24, 39)
        pdf.cell(110, 14, f" {value}", border=1, ln=True)

    y_year = datetime.now().year - 1911
    add_row("業主名稱", rec['客戶'])
    add_row("施工地址", rec['地址'])
    add_row("工程項目", f"{rec['項目']} 工程")
    add_row("保固期限", f"{rec['保固']} 年")
    add_row("生效日期", f"民國 {y_year} 年 {datetime.now().month} 月 {datetime.now().day} 日")

    pdf.ln(30); pdf.set_x(120); pdf.set_font_size(14)
    pdf.cell(60, 8, "承 包 商：鑫龍工程行", ln=True)
    pdf.set_text_color(220, 38, 38)
    pdf.set_x(120); pdf.cell(60, 8, "負 責 人：劉建成 (蓋章)", ln=True)
    pdf.set_text_color(17, 24, 39)
    pdf.set_x(120); pdf.cell(60, 8, "電    話：0917256229", ln=True)
    
    return bytes(pdf.output())

# --- 5. 主操作介面 ---
st.sidebar.markdown("### 👨‍🔧 系統管理")
if st.sidebar.button("🚪 登出"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🚧 工程報表操作面板")

with st.form("main_form", clear_on_submit=True):
    st.subheader("📋 建立新紀錄")
    c1, c2 = st.columns(2)
    name = c1.text_input("客戶姓名")
    phone = c2.text_input("聯絡電話")
    addr = st.text_input("施工地址")
    
    st.divider()
    ca, cb, cc = st.columns(3)
    items = {"頂樓天台": 3500, "浴室防水": 2800, "外牆滲漏": 2200, "壁癌處理": 2500, "油漆工程": 1200, "追加項目": 0}
    p_item = ca.selectbox("項目", list(items.keys()))
    sq = cb.number_input("坪數", min_value=0.0, step=0.1)
    pr = cc.number_input("單價", value=items[p_item])
    
    w_years = st.slider("保固年限", 0, 10, 3)
    submit = st.form_submit_button("✅ 儲存資料")

if submit:
    if name and addr and re.match(r'^[0-9-]{8,12}$', phone):
        st.session_state.history.append({
            "日期": datetime.now().strftime("%Y/%m/%d"),
            "客戶": name, "電話": phone, "地址": addr,
            "項目": p_item, "坪數": sq, "單價": pr,
            "總價": int(sq * pr), "保固": w_years
        })
        st.success(f"業主 {name} 資料已存檔")
    else:
        st.error("填寫不完整或電話格式錯誤")

# --- 6. 管理與匯出 ---
if st.session_state.history:
    st.divider()
    st.header("📊 本月數據總覽")
    df = pd.DataFrame(st.session_state.history)
    
    col_metric, col_count = st.columns(2)
    col_metric.metric("累積營收", f"NT$ {df['總價'].sum():,}")
    col_count.metric("案件總數", f"{len(df)} 件")
    
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    c_btn1, c_btn2 = st.columns(2)
    
    buf = io.BytesIO()
    edited_df.to_excel(buf, index=False, engine='openpyxl')
    c_btn1.download_button("📊 匯出 Excel", data=buf.getvalue(), file_name="鑫龍月報.xlsx", use_container_width=True)
    
    last = edited_df.iloc[-1]
    pdf_out = create_pdf(last)
    c_btn2.download_button(f"📄 下載 {last['客戶']} 保固書", data=pdf_out, file_name=f"{last['客戶']}_保固證明.pdf", use_container_width=True)