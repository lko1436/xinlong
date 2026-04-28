import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
import re

# --- 1. 頁面配置與 CSS ---
st.set_page_config(page_title="鑫龍工程行", layout="centered", page_icon="🏗️")

st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stAppViewContainer"] { background-color: #E2E8F0 !important; }
    h1, h2, h3, p, span, label { color: #1E293B !important; font-family: 'Noto Sans TC', sans-serif !important; }
    div[data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        border-top: 10px solid #EA580C !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        padding: 2.5rem !important;
    }
    div.stButton > button {
        background-color: #EA580C !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        height: 3.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 登入系統 ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'history' not in st.session_state: st.session_state.history = []

if not st.session_state.logged_in:
    st.markdown("<br><h1 style='text-align: center;'>🏗️ 鑫龍工程內部系統</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        u = st.text_input("帳號")
        p = st.text_input("密碼", type="password")
        if st.form_submit_button("進入系統"):
            if u == "admin" and p == "xinlong888":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("密碼錯誤")
    st.stop()

# --- 3. PDF 生成引擎 ---
class ModernPDF(FPDF):
    def header(self):
        self.set_fill_color(30, 41, 59)
        self.rect(0, 0, 210, 8, 'F')
    def footer(self):
        self.set_y(-15)
        self.set_font("CustomFont", "", 9) if os.path.exists("font.ttf") else self.set_font("helvetica", "", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "鑫龍工程行 - 系統自動生成證明", align='C')

def create_pdf(rec):
    pdf = ModernPDF()
    pdf.add_page()
    if os.path.exists("font.ttf"):
        pdf.add_font("CustomFont", "", "font.ttf")
        pdf.set_font("CustomFont", "", 12)
    else:
        pdf.set_font("helvetica", "", 12)

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
    add_row("業主名稱", str(rec['客戶']))
    add_row("施工地址", str(rec['地址']))
    add_row("工程項目", f"{rec['項目']}工程")
    add_row("保固期限", f"{rec['保固']} 年")
    add_row("生效日期", f"民國 {y_year} 年 {datetime.now().month} 月 {datetime.now().day} 日")

    pdf.ln(25); pdf.set_x(110); pdf.set_font_size(14); pdf.set_text_color(30, 41, 59)
    pdf.cell(70, 10, "承 包 商：鑫龍工程行", ln=True)
    pdf.ln(2); pdf.set_x(110)
    pdf.cell(70, 10, "負 責 人：________________ (簽章)", ln=True)
    pdf.ln(2); pdf.set_x(110)
    pdf.cell(70, 10, "電    話：0917256229", ln=True)
    
    return bytes(pdf.output())

# --- 4. 主介面操作 ---
st.sidebar.button("🚪 登出", on_click=lambda: st.session_state.update({"logged_in": False}))
st.title("🚧 鑫龍工程操作面板")

with st.form("main_form", clear_on_submit=True):
    st.subheader("📋 紀錄登錄")
    c1, c2 = st.columns(2)
    name = c1.text_input("客戶姓名")
    phone = c2.text_input("聯絡電話")
    addr = st.text_input("施工地址")
    
    ca, cb, cc = st.columns(3)
    items = {"頂樓天台": 3500, "浴室防水": 2800, "外牆滲漏": 2200, "壁癌處理": 2500, "油漆工程": 1200, "追加項目": 0}
    p_item = ca.selectbox("施作項目", list(items.keys()))
    sq = cb.number_input("坪數", min_value=0.0, step=0.1)
    pr = cc.number_input("單價", value=items[p_item])
    w_years = st.slider("保固年限", 0, 10, 3)
    submit = st.form_submit_button("💾 儲存紀錄")

if submit and name and addr:
    st.session_state.history.append({
        "日期": datetime.now().strftime("%Y/%m/%d"), "客戶": name, "電話": phone,
        "地址": addr, "項目": p_item, "坪數": sq, "單價": pr,
        "總價": int(sq * pr), "保固": w_years
    })
    st.success("存檔成功")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.metric("💰 累計金額", f"NT$ {df['總價'].sum():,}")
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    
    c_ex, c_pdf = st.columns(2)
    # Excel
    ex_buf = io.BytesIO()
    edited_df.to_excel(ex_buf, index=False)
    c_ex.download_button("📊 匯出 Excel", data=ex_buf.getvalue(), file_name="月報.xlsx", use_container_width=True)
    
    # PDF (移除按鈕上的括號文字)
    last = edited_df.iloc[-1]
    pdf_out = create_pdf(last)
    c_pdf.download_button(f"📄 下載 {last['客戶']} 保固書", data=pdf_out, file_name=f"{last['客戶']}_保固.pdf", use_container_width=True)