import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os
import re

# --- 1. 頁面配置與主題設定 ---
st.set_page_config(page_title="鑫龍工程管理系統", layout="centered", page_icon="🏗️")

# --- 2. 初始化資料紀錄 ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. PDF 生成核心函數 ---
def create_pdf(rec):
    # FPDF 實例
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # 字體處理 (確保 font.ttf 放在同資料夾)
    font_path = "font.ttf"
    if os.path.exists(font_path):
        pdf.add_font("CustomFont", "", font_path)
        pdf.set_font("CustomFont", "", 12)
    else:
        pdf.set_font("helvetica", "", 12)

    # --- 標題區 ---
    pdf.set_font_size(30)
    pdf.set_text_color(0, 51, 102) # 深藍色
    pdf.cell(0, 30, "鑫龍工程行", ln=True, align='C')
    
    pdf.set_font_size(20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 15, "工程保固證明書", ln=True, align='C')
    pdf.ln(10)

    # --- 內容區 ---
    pdf.set_font_size(15)
    pdf.set_fill_color(245, 245, 245) # 淺灰色背景
    
    # 建立內容列
    y_year = datetime.now().year - 1911
    details = [
        f"業主名稱：{rec['客戶']}",
        f"施工地址：{rec['地址']}",
        f"施工項目：{rec['項目']}工程",
        f"保固期限：{rec['保固']} 年",
        f"生效日期：民國 {y_year} 年 {datetime.now().month} 月 {datetime.now().day} 日"
    ]
    
    for detail in details:
        pdf.cell(0, 15, f"  {detail}", ln=True, border='B')
        pdf.ln(2)

    # --- 簽章區 (固定於右下方) ---
    pdf.ln(30)
    pdf.set_font_size(16)
    pdf.set_x(120)
    pdf.cell(0, 10, "承包商：鑫龍工程行", ln=True)
    pdf.set_x(120)
    pdf.set_text_color(200, 0, 0) # 紅色負責人
    pdf.cell(0, 10, "負責人：劉建成 (簽章)", ln=True)
    pdf.set_x(120)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "電話：0917256229", ln=True)
    
    return pdf.output()

# --- 4. 主介面 ---
st.title("🏗️ 鑫龍工程報表與保固系統")
st.markdown("---")

# 表單輸入區
with st.form("input_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        c_name = st.text_input("客戶姓名*", placeholder="例如：林小姐")
        c_phone = st.text_input("聯絡電話*", placeholder="0912345678")
    with col2:
        addr = st.text_input("施工地址*", placeholder="新北市...")
        w_years = st.number_input("保固年限 (年)", min_value=0, max_value=20, value=3)

    st.write("🔧 工程詳情")
    ca, cb, cc = st.columns(3)
    area_map = {"頂樓天台": 3500, "浴室防水": 2800, "外牆滲漏": 2200, "壁癌處理": 2500, "油漆工程": 1200, "追加項目": 0}
    a_type = ca.selectbox("工程項目", list(area_map.keys()))
    sqft = cb.number_input("坪數", min_value=0.0, step=0.1)
    u_price = cc.number_input("單價 (NT$)", value=area_map[a_type], min_value=0)
    
    submit = st.form_submit_button("🚀 儲存並生成紀錄")

# --- 5. 防呆與存檔邏輯 ---
if submit:
    phone_valid = re.match(r'^[0-9-]{8,12}$', c_phone)
    
    if not c_name or not addr:
        st.error("🚨 錯誤：姓名與地址為必填！")
    elif not phone_valid:
        st.error("🚨 錯誤：電話格式不正確，請輸入純數字！")
    elif sqft <= 0:
        st.warning("⚠️ 提醒：坪數必須大於 0 才能計算總價。")
    else:
        new_entry = {
            "日期": datetime.now().strftime("%Y/%m/%d"),
            "客戶": c_name,
            "電話": c_phone,
            "地址": addr,
            "項目": a_type,
            "坪數": sqft,
            "單價": u_price,
            "總價": int(sqft * u_price),
            "保固": w_years
        }
        st.session_state.history.append(new_entry)
        st.success(f"✅ 已成功儲存 {c_name} 的紀錄！")

# --- 6. 紀錄管理 (Excel) ---
if st.session_state.history:
    st.markdown("---")
    st.header("📊 工程紀錄清單")
    
    df = pd.DataFrame(st.session_state.history)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    # 營收統計
    total_rev = edited_df["總價"].sum()
    st.info(f"💰 目前累積總金額：**NT$ {total_rev:,}** 元")

    # Excel 下載邏輯優化
    towrite = io.BytesIO()
    # 使用 xlsxwriter 讓表格更好看
    edited_df.to_excel(towrite, index=False, engine='openpyxl')
    
    st.download_button(
        label="🟢 匯出 Excel 月報表",
        data=towrite.getvalue(),
        file_name=f"鑫龍工程報表_{datetime.now().strftime('%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    # --- 7. PDF 下載 ---
    st.subheader("📄 PDF 保固證明書")
    if st.button("點此準備最後一筆 PDF 檔案"):
        if not edited_df.empty:
            last_item = edited_df.iloc[-1]
            try:
                pdf_bytes = create_pdf(last_item)
                st.download_button(
                    label=f"📥 下載 {last_item['客戶']} 的保固證明書",
                    data=pdf_bytes,
                    file_name=f"{last_item['客戶']}_保固書.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF 製作出錯：{e}")
else:
    st.info("💡 尚無紀錄，請先填寫上方表單。")