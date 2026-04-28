import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
import re

# --- 1. 頁面配置與 CSS (明亮工業風強化版) ---
st.set_page_config(page_title="鑫龍工程行", layout="centered", page_icon="🏗️")

st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}

    /* 背景：淺水泥灰 */
    [data-testid="stAppViewContainer"] { background-color: #E2E8F0 !important; }

    /* 文字：深碳黑 */
    h1, h2, h3, p, span, label { color: #1E293B !important; font-family: 'Inter', 'Noto Sans TC', sans-serif !important; }

    /* 卡片設計：增加陰影與橘色頂條 */
    div[data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border-radius: 4px !important;
        border: none !important;
        border-top: 10px solid #EA580C !important; /* 強調工程橘 */
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        padding: 2.5rem !important;
    }

    /* 輸入框邊框加深 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #F8FAFC !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* 按鈕：工業級對比 */
    div.stButton > button {
        background-color: #EA580C !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 2px !important;
        font-weight: 800 !important;
        height: 3.5rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:hover {
        background-color: #C2410C !important;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.3) !important;
    }

    /* 指標數據顏色 */
    [data-testid="stMetricValue"] { color: #EA580C !important; font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Session State ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. 登入畫面 ---
if not st.session_state.logged_in:
    st.markdown("<br><br><h1 style='text-align: center;'>🏗️ 鑫龍工程內部系統</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        u = st.text_input("帳號")
        p = st.text_input("密碼", type="password")
        if st.form_submit_button("進入系統"):
            if u == "admin" and p == "xinlong888":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("密碼不正確")
    st.stop()

# --- 4. PDF 生成引擎 (依要求負責人留空 + 移除紅字) ---
class ModernPDF(FPDF):
    def header(self):
        self.set_fill_color(30, 41, 59) # 深灰裝飾條
        self.rect(0, 0, 210, 8, 'F')
    def footer(self):
        self.set_y(-15)
        self.set_font("CustomFont", "", 9) if os.path.exists("font.ttf") else self.set_font("helvetica", "", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "鑫龍工程行 - 保固證明文件系統生成", align='C')

def create_pdf(rec):
    pdf = ModernPDF()
    pdf.add_page()
    if os.path.exists("font.ttf"):
        pdf.add_font("CustomFont", "", "font.ttf")
        pdf.set_font("CustomFont", "", 12)
    else:
        pdf.set_font("helvetica", "", 12)

    # 標題
    pdf.ln(15)
    pdf.set_font_size(28); pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 20, "鑫 龍 工 程 行", ln=True, align='C')
    pdf.set_font_size(16); pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 10, "工 程 保 固 證 明 書", ln=True, align='C')
    
    pdf.ln(12)
    pdf.set_fill_color(248, 250, 252); pdf.set_draw_color(203, 213, 225)
    
    def add_row(label, value):
        pdf.set_x(30); pdf.set_text_color(100, 116, 139)
        pdf.cell(40, 15, f" {label}", border=1, fill=True)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(110, 15, f" {value}", border=1, ln=True)

    y_year = datetime.now().year - 1911
    add_row("業主名稱", rec['客戶'])
    add_row("施工地址", rec['地址'])
    add_row("工程項目", f"{rec['項目']} 工程")
    add_row("保固期限", f"自完工日起算 {rec['保固']} 年")
    add_row("生效日期", f"民國 {y_year} 年 {datetime.now().month} 月 {datetime.now().day} 日")

    # 簽章區塊 (依要求：去紅字、負責人名留空)
    pdf.ln(25); pdf.set_x(110); pdf.set_font_size(14); pdf.set_text_color(30, 41, 59)
    pdf.cell(70, 10, "承 包 商：鑫龍工程行", ln=True)
    pdf.ln(2)
    pdf.set_x(110)
    pdf.cell(70, 10, "負 責 人：________________ (簽名/蓋章)", ln=True) # 留空供手寫
    pdf.ln(2)
    pdf.set_x(110)
    pdf.cell(70, 10, "電    話：0917256229", ln=True)
    
    return bytes(pdf.output())

# --- 5. 操作介面 ---
st.sidebar.markdown("### 👨‍🔧 帳戶管理")
if st.sidebar.button("🚪 登出系統"):
    st.session_state.logged_in = False
    st.rerun()

st.title("🚧 鑫龍工程操作面板")

with st.form("main_form", clear_on_submit=True):
    st.subheader("📋 紀錄登錄")
    c1, c2 = st.columns(2)
    name = c1.text_input("客戶姓名", placeholder="王先生")
    phone = c2.text_input("聯絡電話", placeholder="09xx-xxx-xxx")
    addr = st.text_input("施工地址")
    
    st.markdown("<hr style='border: 1px solid #CBD5E1;'>", unsafe_allow_html=True)
    ca, cb, cc = st.columns(3)
    items = {"頂樓天台": 3500, "浴室防水": 2800, "外牆滲漏": 2200, "壁癌處理": 2500, "油漆工程": 1200, "追加項目": 0}
    p_item = ca.selectbox("施作項目", list(items.keys()))
    sq = cb.number_input("坪數", min_value=0.0, step=0.1)
    pr = cc.number_input("單價", value=items[p_item])
    
    w_years = st.slider("保固年限", 0, 10, 3)
    submit = st.form_submit_button("💾 儲存並寫入紀錄")

if submit:
    if name and addr and re.match(r'^[0-9-]{8,12}$', phone):
        st.session_state.history.append({
            "日期": datetime.now().strftime("%Y/%m/%d"),
            "客戶": name, "電話": phone, "地址": addr,
            "項目": p_item, "坪數": sq, "單價": pr,
            "總價": int(sq * pr), "保固": w_years
        })
        st.success(f"業主 {name} 資料已儲存")
    else:
        st.error("請檢查欄位是否填寫完整")

# --- 6. 數據看板 ---
if st.session_state.history:
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("📊 歷史數據庫")
    df = pd.DataFrame(st.session_state.history)
    
    m1, m2 = st.columns(2)
    m1.metric("💰 累計預計營收", f"NT$ {df['總價'].sum():,}")
    m2.metric("📝 案量統計", f"{len(df)} 件")
    
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    st.markdown("<br>", unsafe_allow_html=True)
    btn_c1, btn_c2 = st.columns(2)
    
    # Excel
    ex_buf = io.BytesIO()
    edited_df.to_excel(ex_buf, index=False, engine='openpyxl')
    btn_c1.download_button("📊 匯出 Excel 報表", data=ex_buf.getvalue(), file_name="鑫龍報表.xlsx", use_container_width=True)
    
    # PDF
    last = edited_df.iloc[-1]
    pdf_out = create_pdf(last)
    btn_c2.download_button(f"📄 下載 {last['客戶']} 保固書 (空白簽章版)", data=pdf_out, file_name=f"{last['客戶']}_保固證明.pdf", use_container_width=True)