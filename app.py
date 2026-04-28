import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
import re

# --- 1. 網頁現代化 CSS 美化 ---
st.set_page_config(page_title="鑫龍工程維護系統", layout="centered", page_icon="🏗️")

st.markdown("""
    <style>
    /* 全域字體與背景 */
    .main { background-color: #f8f9fa; }
    
    /* 標題美化 */
    h1 { color: #003366; font-family: 'Microsoft JhengHei'; font-weight: 800; }
    
    /* 卡片式容器 */
    div.stForm {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: none;
    }
    
    /* 按鈕美化 */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #003366;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00509e;
        border-color: #00509e;
        transform: translateY(-2px);
    }
    
    /* Metric 數值美化 */
    [data-testid="stMetricValue"] { color: #003366; font-size: 1.8rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化 Session ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. PDF 格式重塑 (解決跑版問題) ---
class ModernPDF(FPDF):
    def header(self):
        # 頁首裝飾
        self.set_fill_color(0, 51, 102)
        self.rect(0, 0, 210, 15, 'F')
    
    def footer(self):
        self.set_y(-15)
        self.set_font("CustomFont", "", 9) if os.path.exists("font.ttf") else self.set_font("helvetica", "", 9)
        self.cell(0, 10, "本證明書由 鑫龍工程管理系統 自動生成", align='C')

def create_pdf(rec):
    pdf = ModernPDF()
    pdf.add_page()
    
    font_path = "font.ttf"
    if os.path.exists(font_path):
        pdf.add_font("CustomFont", "", font_path)
        pdf.set_font("CustomFont", "", 12)
    else:
        pdf.set_font("helvetica", "", 12)

    # --- 頂部標題 ---
    pdf.ln(10)
    pdf.set_font_size(32)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 25, "鑫 龍 工 程 行", ln=True, align='C')
    
    pdf.set_font_size(18)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 15, "工 程 保 固 證 明 書", ln=True, align='C')
    pdf.ln(5)

    # --- 質感表格區 (解決對齊跑版) ---
    pdf.set_fill_color(245, 245, 245)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    
    def add_table_row(label, value):
        pdf.set_font_size(13)
        pdf.set_x(25)
        # 標題格 (固定寬度確保對齊)
        pdf.cell(40, 15, f" {label}", border=1, fill=True)
        # 內容格
        pdf.cell(120, 15, f" {value}", border=1, ln=True)

    y_year = datetime.now().year - 1911
    add_table_row("業主名稱", rec['客戶'])
    add_table_row("施工地址", rec['地址'])
    add_table_row("施工項目", f"{rec['項目']} 工程")
    add_table_row("保固期限", f"自完工日起算 {rec['保固']} 年")
    add_table_row("生效日期", f"民國 {y_year} 年 {datetime.now().month} 月 {datetime.now().day} 日")

    # --- 中間條款 ---
    pdf.ln(10)
    pdf.set_x(25)
    pdf.set_font_size(10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(160, 6, "備註：保固期間內若因施工品質導致之滲漏，本公司負責無償修復。若因人為破壞、天災、建物結構體龜裂、地震等不可抗力因素，則不在保固範圍內。", align='L')

    # --- 簽章區 (右側對齊美化) ---
    pdf.ln(25)
    pdf.set_font_size(15)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(110)
    pdf.cell(75, 10, "承 包 商：鑫龍工程行", ln=True)
    pdf.set_x(110)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(75, 10, "負 責 人：劉建成 (蓋章)", ln=True)
    pdf.set_x(110)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(75, 10, "電    話：0917256229", ln=True)
    
    return bytes(pdf.output())

# --- 4. 網頁介面設計 ---
st.title("🏗️ 鑫龍工程管理系統")
st.write("Professional Engineering Management System")

with st.form("modern_form"):
    st.subheader("📋 建立新工程存檔")
    c1, c2 = st.columns(2)
    name = c1.text_input("客戶姓名*", placeholder="請輸入業主名稱")
    phone = c2.text_input("聯絡電話*", placeholder="請輸入 10 位數號碼")
    
    address = st.text_input("施工地址*", placeholder="請輸入詳細地址")
    
    st.divider()
    
    ca, cb, cc = st.columns(3)
    items = {"頂樓天台": 3500, "浴室防水": 2800, "外牆滲漏": 2200, "壁癌處理": 2500, "油漆工程": 1200, "追加項目": 0}
    project_item = ca.selectbox("工程項目", list(items.keys()))
    size = cb.number_input("坪數", min_value=0.0, step=0.1)
    price = cc.number_input("單價 (NT$)", value=items[project_item])
    
    warranty = st.slider("保固設定 (年)", 0, 10, 3)
    
    submit = st.form_submit_button("🚀 確認存檔並產生紀錄")

# --- 5. 存檔防呆 ---
if submit:
    if not name or not address or not re.match(r'^[0-9-]{8,12}$', phone):
        st.error("🚨 請正確填寫所有必填欄位 (姓名、地址、正確電話格式)！")
    elif size <= 0:
        st.warning("⚠️ 坪數必須大於 0 才能進行金額結算。")
    else:
        st.session_state.history.append({
            "日期": datetime.now().strftime("%Y/%m/%d"),
            "客戶": name, "電話": phone, "地址": address,
            "項目": project_item, "坪數": size, "單價": price,
            "總價": int(size * price), "保固": warranty
        })
        st.success(f"✅ 已成功存檔！業主 {name} 的資料已紀錄。")

# --- 6. 紀錄展示區 ---
if st.session_state.history:
    st.divider()
    st.header("📊 本月紀錄管理")
    df = pd.DataFrame(st.session_state.history)
    
    # 營收看版
    col_metric, col_excel = st.columns([2, 1])
    col_metric.metric("本月累計營收", f"NT$ {df['總價'].sum():,} 元")
    
    # Excel 下載
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, engine='openpyxl')
    col_excel.download_button("🟢 匯出 Excel", data=towrite.getvalue(), file_name="鑫龍月報.xlsx", use_container_width=True)

    # 數據編輯器
    st.data_editor(df, use_container_width=True, num_rows="dynamic")

    # --- 7. PDF 下載 ---
    st.subheader("📄 PDF 保固證明書生成")
    if st.button("準備最後一筆資料之 PDF"):
        pdf_bytes = create_pdf(st.session_state.history[-1])
        st.download_button(
            label=f"📥 點此下載 {st.session_state.history[-1]['客戶']} 的保固證明書",
            data=pdf_bytes,
            file_name=f"{st.session_state.history[-1]['客戶']}_保固書.pdf",
            mime="application/pdf"
        )
else:
    st.info("💡 目前尚無紀錄，請於上方輸入資料並提交。")