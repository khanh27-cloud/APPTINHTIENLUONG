import streamlit as st
 
# =========================
# CẤU HÌNH TRANG WEB
# =========================
st.set_page_config(
   page_title="Ứng dụng tính lương thực lãnh",
   page_icon="💰",
   layout="centered"
)
 
# =========================
# HÀM ĐỊNH DẠNG TIỀN
# =========================
def dinh_dang_tien(so_tien):
   return f"{so_tien:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")
 
 
# =========================
# HÀM TÍNH THUẾ TNCN
# =========================
def tinh_thue_tncn(thu_nhap_tinh_thue):
   if thu_nhap_tinh_thue <= 0:
       return 0.0
   elif thu_nhap_tinh_thue <= 10:
       return thu_nhap_tinh_thue * 0.05
   elif thu_nhap_tinh_thue <= 30:
       return thu_nhap_tinh_thue * 0.10 - 0.5
   elif thu_nhap_tinh_thue <= 60:
       return thu_nhap_tinh_thue * 0.20 - 3.5
   elif thu_nhap_tinh_thue <= 100:
       return thu_nhap_tinh_thue * 0.30 - 9.5
   else:
       return thu_nhap_tinh_thue * 0.35 - 14.5
 
 
# =========================
# TIÊU ĐỀ ỨNG DỤNG
# =========================
st.title("💰 ỨNG DỤNG TÍNH LƯƠNG THỰC LÃNH")
st.caption(
   "Tính tổng thu nhập, bảo hiểm xã hội và các khoản bảo hiểm, "
   "thuế thu nhập cá nhân và tiền lương sau khấu trừ."
)
 
st.info(
   "Đơn vị nhập liệu: triệu đồng/tháng. "
   "Các mức giảm trừ và thuế suất bên dưới đang được lấy theo "
   "công thức trong code bạn cung cấp."
)
 
# =========================
# NHẬP THÔNG TIN LƯƠNG
# =========================
st.subheader("1. Thông tin thu nhập")
 
col1, col2 = st.columns(2)
 
with col1:
   luong_co_ban = st.number_input(
       "Lương cơ bản (triệu đồng)",
       min_value=0.0,
       value=15.0,
       step=0.5,
       format="%.3f"
   )
 
   thuong = st.number_input(
       "Tiền thưởng (triệu đồng)",
       min_value=0.0,
       value=2.0,
       step=0.5,
       format="%.3f"
   )
 
with col2:
   phu_cap_co_bhxh = st.number_input(
       "Phụ cấp tính BHXH (triệu đồng)",
       min_value=0.0,
       value=1.0,
       step=0.5,
       format="%.3f"
   )
 
   phu_cap_khong_bhxh = st.number_input(
       "Phụ cấp không tính BHXH (triệu đồng)",
       min_value=0.0,
       value=0.5,
       step=0.5,
       format="%.3f"
   )
 
so_nguoi_phu_thuoc = st.number_input(
   "Số người phụ thuộc",
   min_value=0,
   max_value=100,
   value=1,
   step=1
)
 
st.divider()
 
# =========================
# NÚT TÍNH TOÁN
# =========================
if st.button("🧮 TÍNH THUẾ VÀ LƯƠNG THỰC LÃNH", type="primary", use_container_width=True):
 
   # 1. Tổng thu nhập
   tong_thu_nhap = (
       luong_co_ban
       + thuong
       + phu_cap_co_bhxh
       + phu_cap_khong_bhxh
   )
 
   # 2. Khoản bảo hiểm người lao động đóng
   tien_bhxh = (luong_co_ban + phu_cap_co_bhxh) * 0.105
 
   # 3. Các khoản giảm trừ theo công thức ban đầu
   giam_tru_ban_than = 15.5
   giam_tru_nguoi_phu_thuoc = 6.2 * so_nguoi_phu_thuoc
 
   # 4. Thu nhập tính thuế
   thu_nhap_tinh_thue = (
       tong_thu_nhap
       - giam_tru_ban_than
       - giam_tru_nguoi_phu_thuoc
       - tien_bhxh
   )
 
   # 5. Tính thuế TNCN
   thue_tncn = tinh_thue_tncn(thu_nhap_tinh_thue)
 
   # 6. Tiền lương thực lãnh
   thuc_lanh = tong_thu_nhap - tien_bhxh - thue_tncn
 
   # =========================
   # HIỂN THỊ KẾT QUẢ
   # =========================
   st.subheader("2. Kết quả tính toán")
 
   col1, col2 = st.columns(2)
 
   with col1:
       st.metric(
           "Tổng thu nhập",
           f"{dinh_dang_tien(tong_thu_nhap)} triệu đồng"
       )
 
       st.metric(
           "Bảo hiểm người lao động đóng",
           f"{dinh_dang_tien(tien_bhxh)} triệu đồng"
       )
 
   with col2:
       st.metric(
           "Thu nhập tính thuế",
           f"{dinh_dang_tien(max(0, thu_nhap_tinh_thue))} triệu đồng"
       )
 
       st.metric(
           "Thuế TNCN phải nộp",
           f"{dinh_dang_tien(thue_tncn)} triệu đồng"
       )
 
   st.success(
       f"💵 TIỀN THỰC LÃNH: {dinh_dang_tien(thuc_lanh)} TRIỆU ĐỒNG/THÁNG"
   )
 
   # =========================
   # BẢNG CHI TIẾT
   # =========================
   st.subheader("3. Bảng chi tiết lương")
 
   bang_ket_qua = {
       "Khoản mục": [
           "Lương cơ bản",
           "Tiền thưởng",
           "Phụ cấp tính BHXH",
           "Phụ cấp không tính BHXH",
           "TỔNG THU NHẬP",
           "Bảo hiểm người lao động đóng",
           "Giảm trừ bản thân",
           "Giảm trừ người phụ thuộc",
           "Thu nhập tính thuế trước khi xử lý âm",
           "Thuế thu nhập cá nhân",
           "TIỀN THỰC LÃNH"
       ],
       "Số tiền (triệu đồng)": [
           luong_co_ban,
           thuong,
           phu_cap_co_bhxh,
           phu_cap_khong_bhxh,
           tong_thu_nhap,
           -tien_bhxh,
           -giam_tru_ban_than,
           -giam_tru_nguoi_phu_thuoc,
           thu_nhap_tinh_thue,
           -thue_tncn,
           thuc_lanh
       ]
   }
 
   import pandas as pd
 
   df = pd.DataFrame(bang_ket_qua)
   df["Số tiền (triệu đồng)"] = df["Số tiền (triệu đồng)"].map(
       dinh_dang_tien
   )
 
   st.dataframe(df, use_container_width=True, hide_index=True)
 
   # =========================
   # GIẢI THÍCH CÔNG THỨC
   # =========================
   with st.expander("📘 Xem công thức tính"):
 
       st.markdown("""
       **Bước 1. Tổng thu nhập**
 
       Tổng thu nhập = Lương cơ bản + Thưởng + Phụ cấp tính BHXH
       + Phụ cấp không tính BHXH.
 
       **Bước 2. Khoản bảo hiểm**
 
       Bảo hiểm = (Lương cơ bản + Phụ cấp tính BHXH) × 10,5%.
 
       **Bước 3. Thu nhập tính thuế**
 
       Thu nhập tính thuế = Tổng thu nhập − Giảm trừ bản thân
       − Giảm trừ người phụ thuộc − Khoản bảo hiểm.
 
       **Bước 4. Thuế TNCN**
 
       Áp dụng biểu thuế lũy tiến theo công thức trong chương trình.
 
       **Bước 5. Tiền thực lãnh**
 
       Tiền thực lãnh = Tổng thu nhập − Bảo hiểm − Thuế TNCN.
       """)
 
   # =========================
   # XUẤT FILE CSV
   # =========================
   csv_data = pd.DataFrame({
       "Khoản mục": bang_ket_qua["Khoản mục"],
       "Số tiền (triệu đồng)": bang_ket_qua["Số tiền (triệu đồng)"]
   }).to_csv(index=False).encode("utf-8-sig")
 
   st.download_button(
       label="📥 TẢI BẢNG LƯƠNG CSV",
       data=csv_data,
       file_name="bang_tinh_luong.csv",
       mime="text/csv",
       use_container_width=True
   )
 
st.divider()
st.caption(
   "Lưu ý: Kết quả là ước tính theo các giả định và công thức đã nhập, "
   "không thay thế việc xác định nghĩa vụ thuế theo quy định pháp luật."
)
