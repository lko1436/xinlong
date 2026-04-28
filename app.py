import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
import re

# --- 1. 頁面配置與現代化 CSS 注入 ---
st.set_page_config(page_title="鑫龍工程管理系統", layout="centered", page_icon="🏗️")

st.markdown("""
    <style>
    /* 隱藏預設選單與 Footer，提升 App 質感 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 全域背景色微調為極淺灰，凸顯白色卡片 */
    .stApp { background-color: #F8FAFC; }

    /* 標題字體與顏色 */
    h1, h2, h3 {
        color: #0F172A;
        font-family: 'Helvetica Neue', Helvetica, Arial, 'Microsoft JhengHei', sans-serif;
        font-weight: 700;
    }

    /* 表單卡片美化 (加上陰影與圓角) */
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }

    /* 輸入框視覺優化 */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 1px solid #CBD5E1;
        padding: 0.5rem;
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 1px #3B82F6;
    }

    /* 主要按鈕 (Call to Action) 美化 */
    div.stButton > button:first-child {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.2s ease-in-out;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transform: translateY(-2px);
    }

    /* 營收數字美化 */
    [data-testid="stMetricValue"] {
        color: #0F172A;
        font-size: 2.2rem;
        font-weight: 800;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #64748B;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化 Session ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. PDF 格式修正 (高質感極簡表格) ---
class ModernPDF(FPDF):
    def header(self):
        # 頂部企業識別色帶
        self.set_fill_color(15, 23, 42) # 深海藍 #0F172A
        self.rect(0, 0, 210, 12, 'F')
    
    def footer(self):
        self.set_y(-15)
        self.set_font("CustomFont", "", 9) if os.path.exists("font.ttf") else self.set_font("helvetica", "", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "本證明書由 鑫龍工程管理系統 自動生成", align='C')

def create_pdf(rec):
    pdf = ModernPDF()
    pdf.add_page()
    
    # 強烈建議使用思源黑體 (Noto Sans TC) 避免跑字
    font_path = "font.ttf"
    if os.path.exists(font_path):
        pdf.add_font("CustomFont", "", font_path)
        pdf.set_font("CustomFont", "", 12)
    else:
        pdf.set_font("helvetica", "", 12)

    # --- 標題區 ---
    pdf.ln(12)
    pdf.set_font_size(28)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 20, "鑫龍工程行", ln=True, align='C')
    
    pdf.set_font_size(16)
    pdf.set_text_color(100, 116, 139) # Slate 500
    pdf.cell(0, 10, "工 程 保 固 證 明 書", ln=True, align='C')
    pdf.ln(8)

    # --- 現代化表格設計 (解決字體對齊問題) ---
    pdf.set_fill_color(248, 250, 252) # 極淺藍灰
    pdf.set_draw_color(203, 213, 225) # 邊框淺灰
    pdf.set_line_width(0.3)
    
    def add_row(label, value):
        pdf.set_font_size(12)
        pdf.set_x(25)
        pdf.set_text_color(71, 85, 105) # 標題字體顏色
        pdf.cell(35, 14, f" {label}", border=1, fill=True, align='L')
        pdf.set_text_color(15, 23, 42) # 內容字體顏色
        pdf.cell(125, 14, f" {value}", border=1, ln=True, align='L')

    y_year = datetime.now().year - 1911
    
    add_row("業主名稱", rec['客戶'])
    add_row("施工地址", rec['地址'])
    add_row("施工項目", f"{rec['項目']}工程")
    add_row("保固期限", f"自完工日起算 {rec['保固']} 年")
    add_row("生效日期", f"民國 {y_year} 年 {datetime.now().month} 月 {datetime.now().day} 日")

    # --- 補充條款 (增加專業度) ---
    pdf.ln(8)
    pdf.set_x(25)
    pdf.set_font_size(9)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(160, 6, "備註：保固期間內若因本公司施工品質導致之異常，由本公司負責無償修復。若因人為破壞、天災 (如地震、颱風) 或建物結構本身龜裂等不可抗力因素所致，則不在保固範圍內。", align='L')

    # --- 簽章區 (俐落排版) ---
    pdf.ln(20)
    pdf.set_font_size(14)
    pdf.set_text_color(15, 23, 42)
    
    # 將簽章區靠右對齊
    pdf.set_x(120)
    pdf.cell(70, 8, "承 包 商：鑫龍工程行", ln=True)
    pdf.set_x(120)
    pdf.set_text_color(220, 38, 38) # 紅色
    pdf.cell(70, 8, "負 責 人：劉建成 (蓋章)", ln=True)
    pdf.set_x(120)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(70, 8, "連絡電話：0917256229", ln=True)
    
    return bytes(pdf.output())

# --- 4. 網頁 UI 結構 ---
st.markdown("<h1>🏗️ 鑫龍工程管理系統</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748B; margin-bottom: 2rem;'>專業、高效的防水工程紀錄與保固書生成工具</p>", unsafe_allow_html=True)

with st.form("modern_form", clear_on_submit=True):
    st.markdown("<h3>📋 新增工程紀錄</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    name = c1.text_input("客戶姓名", placeholder="請輸入業主名稱")
    phone = c2.text_input("聯絡電話", placeholder="例如：0912345678")
    address = st.text_input("施工地址", placeholder="請輸入詳細地址")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    ca, cb, cc = st.columns(3)
    items = {"頂樓天台": 3500, "浴室防水": 2800, "外牆滲漏": 2200, "壁癌處理": 2500, "油漆工程": 1200, "追加項目": 0}
    project_item = ca.selectbox("工程項目", list(items.keys()))
    size = cb.number_input("施作坪數", min_value=0.0, step=0.1)
    price = cc.number_input("每坪單價 (NT$)", value=items[project_item])
    
    warranty = st.slider("保固設定 (年)", 0, 10, 3)
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.form_submit_button("建立紀錄並存檔")

# --- 5. 防呆與邏輯 ---
if submit:
    if not name or not address or not re.match(r'^[0-9-]{8,12}$', phone):
        st.error("🚨 驗證失敗：請正確填寫姓名、地址，並確認電話格式。")
    elif size <= 0:
        st.warning("⚠️ 提醒：坪數必須大於 0。")
    else:
        st.session_state.history.append({
            "日期": datetime.now().strftime("%Y/%m/%d"),
            "客戶": name, "電話": phone, "地址": address,
            "項目": project_item, "坪數": size, "單價": price,
            "總價": int(size * price), "保固": warranty
        })
        st.success(f"✅ 成功！業主 **{name}** 的資料已安全儲存。")

# --- 6. 紀錄展示區 ---
if st.session_state.history:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3>📊 本月營收與紀錄管理</h3>", unsafe_allow_html=True)
    
    df = pd.DataFrame(st.session_state.history)
    
    col_metric, col_excel = st.columns([2, 1])
    col_metric.metric("累積營收", f"NT$ {df['總價'].sum():,}")
    
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, engine='openpyxl')
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_excel.download_button("📥 匯出 Excel 月報表", data=towrite.getvalue(), file_name="鑫龍工程_月報表.xlsx", use_container_width=True)

    st.data_editor(df, use_container_width=True, num_rows="dynamic")

    st.markdown("<hr style='margin: 2rem 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown("<h3>📄 輸出文件</h3>", unsafe_allow_html=True)
    
    if st.button("準備最後一筆資料之 PDF"):
        pdf_bytes = create_pdf(st.session_state.history[-1])
        st.download_button(
            label=f"💾 下載 {st.session_state.history[-1]['客戶']} 的保固證明書",
            data=pdf_bytes,
            file_name=f"{st.session_state.history[-1]['客戶']}_保固書.pdf",
            mime="application/pdf"
        )