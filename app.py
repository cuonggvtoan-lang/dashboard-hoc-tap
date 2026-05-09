import streamlit as st
import pandas as pd
import plotly.express as px

# Cấu hình trang
st.set_page_config(page_title="Dashboard Bảng Điểm 8A6", page_icon="📊", layout="wide")

# Tiêu đề
st.title("📊 Dashboard Phân Tích Điểm Học Sinh - Lớp 8A6")
st.markdown("---")

# Hàm tải và xử lý dữ liệu
@st.cache_data
def load_data():
    # URL public của Google Sheet (dùng định dạng export csv)
    sheet_id = "16z8-Jr5wCpi1KlVpGtOAFNSXpuzn8zxZHN4J_yzkgjA"
    gid = "1172095454"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    try:
        df = pd.read_csv(csv_url)
        
        # Xử lý dữ liệu: thay thế dấu phẩy thành dấu chấm ở các cột điểm để chuyển sang số thực
        diem_cols = ['Toán', 'LS&ĐL', 'KHTN', 'Tin', 'Văn', 'Ng.ngữ', 'GDCD', 'C.nghệ', 'TBM']
        for col in diem_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
        
        return df
    except Exception as e:
        st.error(f"Lỗi khi đọc dữ liệu: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Không thể tải dữ liệu. Vui lòng kiểm tra lại link hoặc quyền truy cập của Google Sheet (Share -> Anyone with the link).")
else:
    # Sidebar - Bộ lọc
    st.sidebar.header("🔍 Bộ lọc dữ liệu")
    
    # Lọc theo Kết quả học tập
    kq_hoc_tap = st.sidebar.multiselect(
        "Kết quả học tập",
        options=df["Kết quả học tập"].dropna().unique(),
        default=df["Kết quả học tập"].dropna().unique()
    )
    
    # Lọc theo Kết quả rèn luyện
    kq_ren_luyen = st.sidebar.multiselect(
        "Kết quả rèn luyện",
        options=df["Kết quả rèn luyện"].dropna().unique(),
        default=df["Kết quả rèn luyện"].dropna().unique()
    )
    
    # Áp dụng bộ lọc
    df_filtered = df[(df["Kết quả học tập"].isin(kq_hoc_tap)) & (df["Kết quả rèn luyện"].isin(kq_ren_luyen))]
    
    # KPI Metrics
    st.subheader("📈 Tổng quan số liệu")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Tổng số học sinh", value=len(df_filtered))
    with col2:
        st.metric(label="TBM Cao Nhất", value=f"{df_filtered['TBM'].max():.2f}" if not df_filtered.empty else "0")
    with col3:
        st.metric(label="TBM Thấp Nhất", value=f"{df_filtered['TBM'].min():.2f}" if not df_filtered.empty else "0")
    with col4:
        st.metric(label="TBM Trung Bình Lớp", value=f"{df_filtered['TBM'].mean():.2f}" if not df_filtered.empty else "0")
        
    st.markdown("---")
    
    # Biểu đồ
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Phân bố Kết quả học tập")
        if "Kết quả học tập" in df_filtered.columns:
            kq_counts = df_filtered["Kết quả học tập"].value_counts().reset_index()
            kq_counts.columns = ["Kết quả", "Số lượng"]
            fig1 = px.bar(kq_counts, x="Kết quả", y="Số lượng", color="Kết quả", text="Số lượng", 
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig1.update_layout(xaxis_title="Kết quả", yaxis_title="Số lượng học sinh")
            st.plotly_chart(fig1, use_container_width=True)
            
    with col_chart2:
        st.subheader("Tỷ lệ Kết quả rèn luyện")
        if "Kết quả rèn luyện" in df_filtered.columns:
            rl_counts = df_filtered["Kết quả rèn luyện"].value_counts().reset_index()
            rl_counts.columns = ["Kết quả", "Số lượng"]
            fig2 = px.pie(rl_counts, names="Kết quả", values="Số lượng", hole=0.4,
                          color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    
    col_chart3, col_chart4 = st.columns(2)
    with col_chart3:
        st.subheader("Phân bố Điểm Trung Bình Môn (TBM)")
        if "TBM" in df_filtered.columns:
            fig3 = px.histogram(df_filtered, x="TBM", nbins=10, marginal="box", 
                                color_discrete_sequence=["#636EFA"])
            fig3.update_layout(xaxis_title="Điểm TBM", yaxis_title="Số lượng")
            st.plotly_chart(fig3, use_container_width=True)
        
    with col_chart4:
        st.subheader("Điểm Trung Bình Theo Từng Môn")
        diem_cols = ['Toán', 'LS&ĐL', 'KHTN', 'Tin', 'Văn', 'Ng.ngữ', 'GDCD', 'C.nghệ']
        avg_scores = []
        for col in diem_cols:
            if col in df_filtered.columns:
                avg_scores.append({"Môn": col, "Điểm TB": df_filtered[col].mean()})
                
        if avg_scores:
            df_avg = pd.DataFrame(avg_scores)
            fig4 = px.line(df_avg, x="Môn", y="Điểm TB", markers=True, 
                           line_shape="linear", color_discrete_sequence=["#EF553B"])
            fig4.update_layout(yaxis=dict(range=[0, 10]))
            st.plotly_chart(fig4, use_container_width=True)
            
    st.markdown("---")
    
    # Bảng dữ liệu chi tiết
    st.subheader("📋 Bảng dữ liệu chi tiết")
    st.dataframe(df_filtered, use_container_width=True)
