import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
import re

# --- 1. 精品級 UI/UX 樣式注入 ---
st.set_page_config(page_title="鑫龍工程行", layout="centered", page_icon="🏗️")

st.markdown("""
    <style>
    /* 隱藏 Streamlit 預設雜項 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 全域背景色：高雅燕麥奶灰白 */
    .stApp { background-color: #F5F5F0; font-family: 'Helvetica Neue', Arial, 'Noto Sans TC', sans-serif; }

    /* 標題與文字顏色：深石板灰 */
    h1, h2, h3, p, span { color: #2C3539; }

    /* 表單卡片美化：純白背景、柔和陰影、頂部古銅金飾條 */
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        padding: 2.5rem;
        border-radius: 12px;
        border: none;
        border-top: 5px solid #C19A6B; /* 香檳古銅金 */
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
    }

    /* 輸入框視覺優化 */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 6px;
        border: 1px solid #E0E0E0;
        background-color: #FAFAFA;
        padding: 0.6rem;
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
        border-color: #C19A6B;
        box-shadow: 0 0 0 1px #C19A6B;
    }

    /* 精品按鈕設計 */
    div.stButton > button {
        background-color: #2C3539; /* 深石板灰 */
        color: #FFFFFF;
        border-radius: 6px;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 500;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #C19A6B; /* 懸停變成香檳金 */
        color: #FFFFFF;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(193, 154, 107, 0.3);
    }

    /* 數據表格外框圓角 */
    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #EAEAEA; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化 Session State ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. PDF 格式核心 (完美對齊版) ---
class ModernPDF(FPDF):
    def header(self):
        self.set_fill_color(44, 53, 57) # 深石板灰
        self.rect(0, 0, 210, 10, 'F')
    def footer(self):
        self.set_y(-15)
        self.set_font("CustomFont", "", 9) if os.path.exists("font.ttf") else self.set_font("helvetica", "", 9)
        self.set_text_color(180, 180, 180)
        self.cell(0, 10, "本證明書由 鑫龍工程自動生成", align='C')

def create_pdf(rec):
    pdf = ModernPDF()
    pdf.add_page()
    if os.path.exists("font.ttf"):
        pdf.add_font("CustomFont", "", "font.ttf")
        pdf.set_font("CustomFont", "", 12)
    else:
        pdf.set_font("helvetica", "", 12)

    pdf.ln(12)
    pdf.set_font_size(30); pdf.set_text_color(44, 53, 57)
    pdf.cell(0, 20, "鑫 龍 工 程 行", ln=True, align='C')
    pdf.set_font_size(16); pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 10, "工 程 保 固 證 明 書", ln=True, align='C')
    
    pdf.ln(12)
    pdf.set_fill_color(249, 249, 246); pdf.set_draw_color(210, 210, 210)
    def add_row(label, value):
        pdf.set_x(30); pdf.set_text_color(100, 100, 100)
        pdf.cell(40, 14, f" {label}", border=1, fill=True)
        pdf.set_text_color(44, 53, 57)
        pdf.cell(110, 14, f" {value}", border=1, ln=True)

    y_year = datetime.now().year - 1911
    add_row("業主名稱", rec['客戶'])
    add_row("施作地址", rec['地址'])
    add_row("工程項目", f"{rec['項目']} 工程")
    add_row("保固年限", f"完工日起算 {rec['保固']} 年")
    add_row("生效日期", f"民國 {y_year} 年 {datetime.now().month} 月 {datetime.now().day} 日")

    pdf.ln(8); pdf.set_x(30); pdf.set_font_size(9); pdf.set_text_color(130, 130, 130)
    pdf.multi_cell(150, 6, "備註：保固期間內若因本公司施工導致之異常，由本公司負責無償修復。若因人為破壞、天災或建物結構本身等不可抗力因素，則不在保固範圍內。", align='L')

    pdf.ln(20); pdf.set_x(120); pdf.set_font_size(14); pdf.set_text_color(44, 53, 57)
    pdf.cell(60, 8, "承 包 商：鑫龍工程行", ln=True)
    pdf.set_x(120); pdf.set_text_color(193, 154, 107) # 古銅金
    pdf.cell(60, 8, "負 責 人：劉建成 (蓋章)", ln=True)
    pdf.set_x(120); pdf.set_text_color(44, 53, 57)
    pdf.cell(60, 8, "連絡電話：0917256229", ln=True)
    
    return bytes(pdf.output())

# --- 4. 一頁式流暢介面 ---
st.markdown("<h1 style='text-align: center; font-size: 2.5rem; margin-top: 1rem;'>鑫龍工程行</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 1rem; margin-bottom: 2rem;'>防水工程專用紀錄與保固系統</p>", unsafe_allow_html=True)

# 填寫區塊 (卡片設計)
with st.form("clean_form", clear_on_submit=True):
    st.markdown("<h3 style='margin-bottom: 1rem;'>建立新紀錄</h3>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    name = c1.text_input("客戶姓名", placeholder="例如：張先生")
    phone = c2.text_input("聯絡電話", placeholder="例如：0912345678")
    address = st.text_input("施工地址", placeholder="請填寫完整地址")
    
    st.markdown("<hr style='border-color: #EEE; margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    ca, cb, cc = st.columns(3)
    items = {"頂樓天台": 3500, "浴室防水": 2800, "外牆滲漏": 2200, "壁癌處理": 2500, "油漆工程": 1200, "追加項目": 0}
    p_item = ca.selectbox("工程項目", list(items.keys()))
    p_size = cb.number_input("施作坪數", min_value=0.0, step=0.1)
    p_price = cc.number_input("單價 (NT$)", value=items[p_item])
    
    warranty = st.slider("保固期限 (年)", 0, 10, 3)
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.form_submit_button("＋ 儲存並建立檔案")

# 防呆邏輯
if submit:
    if not name or not address or not re.match(r'^[0-9-]{8,12}$', phone):
        st.error("🚨 請確認姓名、地址與電話格式正確。")
    elif p_size <= 0:
        st.warning("⚠️ 坪數必須大於 0。")
    else:
        st.session_state.history.append({
            "日期": datetime.now().strftime("%Y/%m/%d"),
            "客戶": name, "電話": phone, "地址": address,
            "項目": p_item, "坪數": p_size, "單價": p_price,
            "總價": int(p_size * p_price), "保固": warranty
        })
        st.success(f"✨ 業主 {name} 的資料已成功存檔。")

# --- 5. 管理區塊 (一頁式往下滑) ---
if st.session_state.history:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3>📂 工程紀錄一覽</h3>", unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state.history)
    
    # 簡約數據看板
    col_rev, col_count = st.columns(2)
    col_rev.metric("本月累積營收", f"NT$ {df['總價'].sum():,}")
    col_count.metric("已完成案件數", f"{len(df)} 件")
    
    # 表格
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    # 輸出區塊 (並排按鈕，簡潔有力)
    st.markdown("<br>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns(2)
    
    # Excel
    excel_buffer = io.BytesIO()
    edited_df.to_excel(excel_buffer, index=False, engine='openpyxl')
    c_btn1.download_button("📊 匯出 Excel 總表", data=excel_buffer.getvalue(), file_name="鑫龍月報.xlsx", use_container_width=True)
    
    # PDF
    last_record = edited_df.iloc[-1]
    pdf_out = create_pdf(last_record)
    c_btn2.download_button(f"📄 下載 {last_record['客戶']} 的保固書", data=pdf_out, file_name=f"{last_record['客戶']}_保固書.pdf", use_container_width=True)