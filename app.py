import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
import re

# --- 1. 頁面配置與強勢 CSS 覆蓋 (工業暗黑風) ---
st.set_page_config(page_title="鑫龍工程內部系統", layout="centered", page_icon="🚧")

st.markdown("""
    <style>
    /* 隱藏預設浮水印 */
    #MainMenu, footer, header {visibility: hidden;}

    /* 強制替換整個 App 背景：深鋼鐵灰 */
    [data-testid="stAppViewContainer"] { background-color: #1A1C20 !important; }

    /* 全域字體顏色：亮灰白 */
    h1, h2, h3, p, span, label { color: #E0E0E0 !important; font-family: 'Helvetica Neue', 'Noto Sans TC', sans-serif !important; }

    /* 卡片設計：深色底 + 粗獷的工程橘左邊框 */
    div[data-testid="stForm"] {
        background-color: #25282D !important;
        border-radius: 4px !important;
        border: 1px solid #36393E !important;
        border-left: 6px solid #F5A623 !important; /* 工程橘 */
        box-shadow: 0 10px 20px rgba(0,0,0,0.5) !important;
        padding: 2.5rem !important;
    }

    /* 輸入框工業風：暗底亮框 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1A1C20 !important;
        color: #FFFFFF !important;
        border: 1px solid #42464D !important;
        border-radius: 4px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #F5A623 !important;
        box-shadow: 0 0 0 1px #F5A623 !important;
    }

    /* 動作按鈕：高對比工程橘 */
    div.stButton > button {
        background-color: #F5A623 !important;
        color: #1A1C20 !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 900 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #FFB732 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(245, 166, 35, 0.4) !important;
    }

    /* 數據表格底色 */
    [data-testid="stDataFrame"] { border: 1px solid #42464D !important; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化 Session State (登入狀態與歷史資料) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. 安全登入頁面攔截 ---
if not st.session_state.logged_in:
    st.markdown("<br><br><h1 style='text-align: center; color: #F5A623 !important;'>🚧 鑫龍工程行</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>內部資料管理系統 - 請先驗證身分</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("管理員帳號", placeholder="輸入帳號")
        password = st.text_input("系統密碼", type="password", placeholder="輸入密碼")
        submit_login = st.form_submit_button("登 入 系 統")
        
        if submit_login:
            # 🔴 呈紘注意：在這裡修改你的帳號跟密碼！
            if username == "admin" and password == "xinlong888":
                st.session_state.logged_in = True
                st.rerun() # 驗證成功，重新整理頁面進入系統
            else:
                st.error("❌ 拒絕存取：帳號或密碼錯誤！")
    st.stop() # 如果沒登入，程式會停在這裡，不載入下面的機密代碼

# ================= 以下為登入後才會顯示的系統核心 =================

# --- 4. 側邊欄登出按鈕 ---
st.sidebar.markdown("### 👨‍🔧 系統管理員")
if st.sidebar.button("🚪 登出系統"):
    st.session_state.logged_in = False
    st.rerun()

# --- 5. PDF 產生引擎 ---
class ModernPDF(FPDF):
    def header(self):
        self.set_fill_color(30, 33, 36) # 暗灰色
        self.rect(0, 0, 210, 10, 'F')
    def footer(self):
        self.set_y(-15)
        self.set_font("CustomFont", "", 9) if os.path.exists("font.ttf") else self.set_font("helvetica", "", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "內部機密系統生成 - 鑫龍工程", align='C')

def create_pdf(rec):
    pdf = ModernPDF()
    pdf.add_page()
    if os.path.exists("font.ttf"):
        pdf.add_font("CustomFont", "", "font.ttf")
        pdf.set_font("CustomFont", "", 12)
    else:
        pdf.set_font("helvetica", "", 12)

    pdf.ln(12)
    pdf.set_font_size(30); pdf.set_text_color(30, 33, 36)
    pdf.cell(0, 20, "鑫 龍 工 程 行", ln=True, align='C')
    pdf.set_font_size(16); pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "工 程 保 固 證 明 書", ln=True, align='C')
    
    pdf.ln(12)
    pdf.set_fill_color(245, 245, 245); pdf.set_draw_color(200, 200, 200)
    def add_row(label, value):
        pdf.set_x(30); pdf.set_text_color(80, 80, 80)
        pdf.cell(40, 14, f" {label}", border=1, fill=True)
        pdf.set_text_color(30, 33, 36)
        pdf.cell(110, 14, f" {value}", border=1, ln=True)

    y_year = datetime.now().year - 1911
    add_row("業主名稱", rec['客戶'])
    add_row("施作地址", rec['地址'])
    add_row("工程項目", f"{rec['項目']} 工程")
    add_row("保固年限", f"自完工日起算 {rec['保固']} 年")
    add_row("生效日期", f"民國 {y_year} 年 {datetime.now().month} 月 {datetime.now().day} 日")

    pdf.ln(8); pdf.set_x(30); pdf.set_font_size(9); pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(150, 6, "備註：保固期間內若因本公司施工導致之異常，由本公司負責無償修復。若因人為破壞、天災或建物結構本身等不可抗力因素，則不在保固範圍內。", align='L')

    pdf.ln(20); pdf.set_x(120); pdf.set_font_size(14); pdf.set_text_color(30, 33, 36)
    pdf.cell(60, 8, "承 包 商：鑫龍工程行", ln=True)
    pdf.set_x(120); pdf.set_text_color(220, 53, 69) # 紅色
    pdf.cell(60, 8, "負 責 人：劉建成 (蓋章)", ln=True)
    pdf.set_x(120); pdf.set_text_color(30, 33, 36)
    pdf.cell(60, 8, "連絡電話：0917256229", ln=True)
    
    return bytes(pdf.output())

# --- 6. 內部主操作介面 ---
st.markdown("<h1 style='text-align: center; color: #F5A623 !important;'>🏗️ 鑫龍工程操作面板</h1>", unsafe_allow_html=True)

with st.form("clean_form", clear_on_submit=True):
    st.markdown("<h3 style='margin-bottom: 1rem;'>[ 建立工程檔案 ]</h3>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    name = c1.text_input("客戶姓名", placeholder="例如：張先生")
    phone = c2.text_input("聯絡電話", placeholder="例如：0912345678")
    address = st.text_input("施工地址", placeholder="請填寫完整地址")
    
    st.markdown("<hr style='border-color: #42464D; margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    ca, cb, cc = st.columns(3)
    items = {"頂樓天台": 3500, "浴室防水": 2800, "外牆滲漏": 2200, "壁癌處理": 2500, "油漆工程": 1200, "追加項目": 0}
    p_item = ca.selectbox("工程項目", list(items.keys()))
    p_size = cb.number_input("施作坪數", min_value=0.0, step=0.1)
    p_price = cc.number_input("單價 (NT$)", value=items[p_item])
    
    warranty = st.slider("保固期限 (年)", 0, 10, 3)
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.form_submit_button("💾 儲存寫入資料庫")

if submit:
    if not name or not address or not re.match(r'^[0-9-]{8,12}$', phone):
        st.error("🚨 系統阻擋：請確認姓名、地址與電話格式。")
    elif p_size <= 0:
        st.warning("⚠️ 系統阻擋：坪數必須大於 0。")
    else:
        st.session_state.history.append({
            "日期": datetime.now().strftime("%Y/%m/%d"),
            "客戶": name, "電話": phone, "地址": address,
            "項目": p_item, "坪數": p_size, "單價": p_price,
            "總價": int(p_size * p_price), "保固": warranty
        })
        st.success(f"✨ 寫入成功！業主 [{name}] 資料已建檔。")

# --- 7. 管理紀錄與匯出 ---
if st.session_state.history:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3>[ 數據庫總覽 ]</h3>", unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state.history)
    
    col_rev, col_count = st.columns(2)
    col_rev.metric("💰 結算總金額", f"NT$ {df['總價'].sum():,}")
    col_count.metric("📝 歸檔案件數", f"{len(df)} 件")
    
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    st.markdown("<br>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns(2)
    
    # Excel 輸出
    excel_buffer = io.BytesIO()
    edited_df.to_excel(excel_buffer, index=False, engine='openpyxl')
    c_btn1.download_button("📊 輸出 EXCEL 報表", data=excel_buffer.getvalue(), file_name="鑫龍系統_月報表.xlsx", use_container_width=True)
    
    # PDF 輸出
    last_record = edited_df.iloc[-1]
    pdf_out = create_pdf(last_record)
    c_btn2.download_button(f"📄 輸出 {last_record['客戶']} 保固書", data=pdf_out, file_name=f"{last_record['客戶']}_保固證明.pdf", use_container_width=True)