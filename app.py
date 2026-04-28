import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
import re

# --- 1. 專業 UI/UX 樣式注入 (SaaS 旗艦風格) ---
st.set_page_config(page_title="鑫龍工程維護系統", layout="wide", page_icon="🏗️")

st.markdown("""
    <style>
    /* 全域字體與背景 - 採用現代 Slate 灰色系 */
    .stApp { background-color: #F1F5F9; font-family: 'Inter', 'Noto Sans TC', sans-serif; }
    
    /* 隱藏預設元件提升沉浸感 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 頂部導航欄裝飾 */
    .nav-bar { background-color: #1E293B; height: 5px; width: 100%; position: fixed; top: 0; left: 0; z-index: 999; }

    /* 卡片容器設計 - 增加柔和陰影與邊框 */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #64748B;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #FFFFFF !important; color: #0F172A !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }

    /* 專業按鈕樣式 */
    .stButton > button {
        border-radius: 10px;
        background-color: #2563EB;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        transition: all 0.2s ease;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3); background-color: #1D4ED8; }

    /* 數據表格美化 */
    div[data-testid="stDataFrame"] { border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden; }
    </style>
    <div class="nav-bar"></div>
    """, unsafe_allow_html=True)

# --- 2. 初始化 Session State ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. PDF 格式核心 (已修正 bytes 轉檔) ---
class ModernPDF(FPDF):
    def header(self):
        self.set_fill_color(30, 41, 59)
        self.rect(0, 0, 210, 10, 'F')
    def footer(self):
        self.set_y(-15)
        self.set_font("CustomFont", "", 9) if os.path.exists("font.ttf") else self.set_font("helvetica", "", 9)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, "Xin-Long Engineering Management System - Official Document", align='C')

def create_pdf(rec):
    pdf = ModernPDF()
    pdf.add_page()
    if os.path.exists("font.ttf"):
        pdf.add_font("CustomFont", "", "font.ttf")
        pdf.set_font("CustomFont", "", 12)
    else:
        pdf.set_font("helvetica", "", 12)

    pdf.ln(10)
    pdf.set_font_size(28); pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 20, "鑫 龍 工 程 行", ln=True, align='C')
    pdf.set_font_size(16); pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 10, "工 程 保 固 證 明 書", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_fill_color(248, 250, 252); pdf.set_draw_color(226, 232, 240)
    def add_row(label, value):
        pdf.set_x(30); pdf.set_text_color(100, 116, 139)
        pdf.cell(40, 14, f" {label}", border=1, fill=True)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(110, 14, f" {value}", border=1, ln=True)

    y_year = datetime.now().year - 1911
    add_row("業主名稱", rec['客戶'])
    add_row("施作地址", rec['地址'])
    add_row("工程項目", f"{rec['項目']} 工程")
    add_row("保固年限", f"完工日起算 {rec['保固']} 年")
    add_row("生效日期", f"民國 {y_year} 年 {datetime.now().month} 月 {datetime.now().day} 日")

    pdf.ln(25); pdf.set_x(120); pdf.set_font_size(14)
    pdf.cell(60, 8, "承 包 商：鑫龍工程行", ln=True)
    pdf.set_x(120); pdf.set_text_color(220, 38, 38)
    pdf.cell(60, 8, "負 責 人：劉建成 (蓋章)", ln=True)
    pdf.set_x(120); pdf.set_text_color(30, 41, 59)
    pdf.cell(60, 8, "電    話：0917256229", ln=True)
    
    return bytes(pdf.output())

# --- 4. 系統導航分頁 ---
st.title("🏗️ 鑫龍工程維護系統")
tab1, tab2, tab3 = st.tabs(["📋 新增工程紀錄", "📊 數據中心", "💡 營運概況"])

# --- TAB 1: 新增紀錄 ---
with tab1:
    with st.form("pro_form"):
        st.markdown("### 📝 工程明細登錄")
        c1, c2 = st.columns(2)
        name = c1.text_input("業主名稱*", placeholder="張小姐")
        phone = c2.text_input("聯絡電話*", placeholder="0912-345-678")
        addr = st.text_input("施工地址*", placeholder="請輸入完整施工地址")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns(3)
        items = {"頂樓天台": 3500, "浴室防水": 2800, "外牆滲漏": 2200, "壁癌處理": 2500, "油漆工程": 1200, "追加項目": 0}
        p_item = col_a.selectbox("工程項目", list(items.keys()))
        p_size = col_b.number_input("坪數", min_value=0.0, step=0.1)
        p_price = col_c.number_input("單價 (NT$)", value=items[p_item])
        
        w_years = st.slider("保固期限 (年)", 0, 10, 3)
        submit = st.form_submit_button("🚀 確認並存檔")

    if submit:
        if not name or not addr or not re.match(r'^[0-9-]{8,12}$', phone):
            st.error("🚨 請檢查必填欄位或電話格式！")
        else:
            st.session_state.history.append({
                "ID": datetime.now().strftime("%y%m%d%H%M"),
                "日期": datetime.now().strftime("%Y/%m/%d"),
                "客戶": name, "電話": phone, "地址": addr,
                "項目": p_item, "坪數": p_size, "單價": p_price,
                "總價": int(p_size * p_price), "保固": w_years
            })
            st.toast("✅ 紀錄已成功存檔", icon='🎉')

# --- TAB 2: 數據中心 ---
with tab2:
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        
        # 快捷指標
        m1, m2, m3 = st.columns(3)
        m1.metric("本月總案量", f"{len(df)} 件")
        m2.metric("累計預計營收", f"NT$ {df['總價'].sum():,}")
        m3.metric("平均客單價", f"NT$ {int(df['總價'].mean()):,}")

        st.markdown("### 📊 歷史紀錄編輯器")
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="main_editor")
        
        c_ex, c_pdf = st.columns(2)
        # Excel 匯出
        excel_buffer = io.BytesIO()
        edited_df.to_excel(excel_buffer, index=False, engine='openpyxl')
        c_ex.download_button("🟢 匯出 Excel 完整報表", data=excel_buffer.getvalue(), file_name="鑫龍工程月報.xlsx", use_container_width=True)

        # PDF 保固書
        if c_pdf.button("📄 準備最後一筆 PDF 保固書", use_container_width=True):
            pdf_out = create_pdf(edited_df.iloc[-1])
            st.download_button(f"📥 下載 {edited_df.iloc[-1]['客戶']} 的證明書", data=pdf_out, file_name=f"{edited_df.iloc[-1]['客戶']}_保固書.pdf", use_container_width=True)
    else:
        st.info("💡 目前尚無紀錄，請先至「新增工程紀錄」分頁輸入資料。")

# --- TAB 3: 營運概況 (視覺化分析) ---
with tab3:
    if st.session_state.history:
        st.markdown("### 💡 工程分佈分析")
        df_chart = pd.DataFrame(st.session_state.history)
        item_counts = df_chart.groupby('項目')['總價'].sum().reset_index()
        
        # 使用 Streamlit 內建圖表展示專業感
        st.bar_chart(item_counts.set_index('項目'))
        st.caption("工程項目營收佔比分析")
    else:
        st.info("數據累積後，這裡會顯示營運分析圖表。")