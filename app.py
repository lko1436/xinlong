import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io
import os

# --- 1. 頁面配置 ---
st.set_page_config(page_title="鑫龍工程行-報表系統", layout="centered")

# --- 2. 初始化資料紀錄 ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 3. 標題與基本資料 ---
st.title("🏗️ 鑫龍工程行 - 報表系統")

with st.expander("📝 1. 輸入基本資料", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("客戶姓名")
        contact_info = st.text_input("聯絡電話/LINE")
    with col2:
        address = st.text_input("施工地址")
        work_days = st.text_input("施工天數", value="3")
    
    warranty_years = st.number_input("保固年限 (年)", min_value=0, value=3)

with st.expander("🛠️ 2. 施工細節", expanded=True):
    area_options = {"頂樓天台": 3500, "浴室防水": 2800, "外牆滲漏": 2200, "壁癌處理": 2500, "油漆工程": 1200, "追加工程": 0}
    area_type = st.selectbox("施工區域", list(area_options.keys()))
    
    c1, c2 = st.columns(2)
    unit_price = c1.number_input("每坪單價 (NT$)", value=area_options[area_type])
    sqft = c2.number_input("施工面積 (坪)", min_value=0.0, step=0.1)
    
    display_item = st.text_input("自定義項目名稱", value=area_type)

total_amount = int(sqft * unit_price)
st.subheader(f"💰 總金額：NT$ {total_amount:,} 元")

# --- 4. 儲存邏輯 ---
if st.button("✅ 生成報表並存檔", use_container_width=True):
    if not customer_name:
        st.error("請輸入客戶姓名")
    else:
        new_record = {
            "ID": datetime.now().strftime("%H%M%S"),
            "日期": datetime.now().strftime("%Y/%m/%d"),
            "客戶": customer_name,
            "地址": address,
            "項目": display_item,
            "坪數": sqft,
            "單價": unit_price,
            "總價": total_amount,
            "天數": work_days,
            "保固": warranty_years
        }
        st.session_state.history.append(new_record)
        st.success(f"已儲存 {customer_name} 的紀錄")

st.divider()

# --- 5. 月報管理 (修改與刪除) ---
st.header("📊 工程紀錄管理")
if st.session_state.history:
    # 轉成 DataFrame 讓使用者可以直接在網頁修改
    df = pd.DataFrame(st.session_state.history)
    edited_df = st.data_editor(df, num_rows="dynamic", key="editor")
    
    total_revenue = edited_df["總價"].sum()
    st.write(f"### 📈 本月合計營收：NT$ {total_revenue:,} 元")

    # Excel 匯出
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # 建立 Excel 格式
        output_df = edited_df.copy()
        output_df.loc['合計'] = ['', '', '', '', '', '', '', output_df['總價'].sum(), '', '']
        output_df.to_excel(writer, index=False, sheet_name='月報表')
    
    st.download_button(
        label="🟢 匯出 Excel 月報表",
        data=buffer,
        file_name=f"鑫龍工程_{datetime.now().strftime('%m')}月報.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- 6. PDF 保固書生成 (鑫龍規格) ---
    def create_pdf(rec):
        pdf = FPDF()
        pdf.add_page()
        
        # 載入字體 (需確認 font.ttf 存在)
        if os.path.exists("font.ttf"):
            pdf.add_font("MSJH", "", "font.ttf")
            pdf.set_font("MSJH", "", 12)
        
        # 標題
        pdf.set_font_size(30)
        pdf.cell(0, 20, "鑫龍工程行", ln=True, align='C')
        pdf.set_font_size(20)
        pdf.cell(0, 15, "工程保固證明書", ln=True, align='C')
        pdf.set_font_size(12)
        pdf.cell(0, 10, "茲因承攬下列工程，為確保客戶權益及維護施工品質，提供保固。", ln=True, align='C')
        pdf.ln(10)
        
        # 民國換算
        startY = datetime.now().year - 1911
        endY = startY + int(rec['保固'])
        
        # 內容
        pdf.set_font_size(16)
        pdf.cell(0, 12, f"一、 業主名稱：{rec['客戶']}", ln=True)
        pdf.cell(0, 12, f"二、 工程名稱：{rec['項目']}", ln=True)
        pdf.cell(0, 12, f"三、 工程地點：{rec['地址']}", ln=True)
        pdf.cell(0, 12, f"四、 承包內容：{rec['項目']}工程", ln=True)
        pdf.cell(0, 12, f"五、 保固期間：民國 {startY} 年起至民國 {endY} 年止", ln=True)
        
        pdf.ln(20)
        pdf.cell(0, 12, "承包商：鑫龍工程行", ln=True)
        pdf.cell(0, 12, "負責人：劉建成", ln=True)
        pdf.cell(0, 12, "電話：0917256229", ln=True)
        
        return pdf.output()

# --- 6. PDF 保固書生成修正版 ---
if st.button("🛡️ 點此生成保固書內容"):
    if not edited_df.empty:
        last_rec = edited_df.iloc[-1] # 抓最後一筆
        pdf_bytes = create_pdf(last_rec)
        
        st.success(f"✅ {last_rec['客戶']} 的保固書已生成！")
        
        # 🔴 關鍵：把下載按鈕放在生成按鈕觸發後的邏輯裡
        st.download_button(
            label="📥 點我正式下載 PDF 檔案",
            data=pdf_bytes,
            file_name=f"{last_rec['客戶']}_保固書.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.error("目前沒有資料可以生成保固書")