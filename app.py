import streamlit as st
import pandas as pd

# ==============================
# CẤU HÌNH ỨNG DỤNG
# ==============================
st.set_page_config(
    page_title="Tính thuế TNCN và lương thực lãnh",
    page_icon="💰",
    layout="centered"
)

# Các tham số theo code gốc, đơn vị triệu đồng
GIAM_TRU_BAN_THAN = 15.5
GIAM_TRU_PHU_THUOC = 6.2
TY_LE_BHXH = 0.105


# ==============================
# HÀM ĐỊNH DẠNG
# ==============================
def dinh_dang_tien(so_tien):
    return f"{so_tien:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ==============================
# HÀM TÍNH THUẾ TNCN
# ==============================
def tinh_thue_tncn(thu_nhap_tinh_thue):
    # Không tính thuế nếu thu nhập tính thuế <= 0
    thu_nhap_tinh_thue = max(0.0, thu_nhap_tinh_thue)

    if thu_nhap_tinh_thue <= 10:
        thue = thu_nhap_tinh_thue * 0.05
    elif thu_nhap_tinh_thue <= 30:
        thue = thu_nhap_tinh_thue * 0.10 - 0.5
    elif thu_nhap_tinh_thue <= 60:
        thue = thu_nhap_tinh_thue * 0.20 - 3.5
    elif thu_nhap_tinh_thue <= 100:
        thue = thu_nhap_tinh_thue * 0.30 - 9.5
    else:
        thue = thu_nhap_tinh_thue * 0.35 - 14.5

    return max(0.0, thue)


# ==============================
# GIAO DIỆN
# ==============================
st.title("💰 TÍNH THUẾ TNCN VÀ LƯƠNG THỰC LÃNH")

st.caption(
    "Công cụ ước tính thuế thu nhập cá nhân và tiền lương thực nhận. "
    "Đơn vị nhập liệu và kết quả: triệu đồng."
)

st.info(
    "Nhập số liệu lương của người lao động vào các ô bên dưới. "
    "Kết quả sẽ được cập nhật khi bạn thay đổi thông tin."
)

# ==============================
# NHẬP THÔNG TIN
# ==============================
st.subheader("1. Thông tin thu nhập")

col1, col2 = st.columns(2)

with col1:
    luong_co_ban = st.number_input(
        "Lương cơ bản (triệu đồng)",
        min_value=0.0,
        value=10.0,
        step=0.5,
        format="%.3f"
    )

    phu_cap_co_bhxh = st.number_input(
        "Phụ cấp tính BHXH (triệu đồng)",
        min_value=0.0,
        value=0.0,
        step=0.5,
        format="%.3f"
    )

with col2:
    tien_thuong = st.number_input(
        "Tiền thưởng (triệu đồng)",
        min_value=0.0,
        value=0.0,
        step=0.5,
        format="%.3f"
    )

    phu_cap_khong_bhxh = st.number_input(
        "Phụ cấp không tính BHXH (triệu đồng)",
        min_value=0.0,
        value=0.0,
        step=0.5,
        format="%.3f"
    )

so_nguoi_phu_thuoc = st.number_input(
    "Số người phụ thuộc",
    min_value=0,
    value=0,
    step=1
)

# ==============================
# TÍNH TOÁN
# ==============================
tong_thu_nhap = (
    luong_co_ban
    + tien_thuong
    + phu_cap_co_bhxh
    + phu_cap_khong_bhxh
)

tien_dong_bhxh = (
    luong_co_ban + phu_cap_co_bhxh) * TY_LE_BHXH

tong_giam_tru = (
    GIAM_TRU_BAN_THAN
    + GIAM_TRU_PHU_THUOC * so_nguoi_phu_thuoc
)

thu_nhap_tinh_thue = max(
    0.0,
    tong_thu_nhap - tong_giam_tru - tien_dong_bhxh
)

thue_tncn = tinh_thue_tncn(thu_nhap_tinh_thue)

thuc_lanh = tong_thu_nhap - tien_dong_bhxh - thue_tncn

# ==============================
# HIỂN THỊ KẾT QUẢ
# ==============================
st.divider()
st.subheader("2. Kết quả tính lương")

m1, m2 = st.columns(2)

with m1:
    st.metric(
        label="Tổng thu nhập",
        value=f"{dinh_dang_tien(tong_thu_nhap)} triệu đồng"
    )

    st.metric(
        label="Bảo hiểm người lao động đóng",
        value=f"{dinh_dang_tien(tien_dong_bhxh)} triệu đồng"
    )

    st.metric(
        label="Thu nhập tính thuế",
        value=f"{dinh_dang_tien(thu_nhap_tinh_thue)} triệu đồng"
    )

with m2:
    st.metric(
        label="Thuế TNCN phải nộp",
        value=f"{dinh_dang_tien(thue_tncn)} triệu đồng"
    )

    st.metric(
        label="TIỀN THỰC LÃNH",
        value=f"{dinh_dang_tien(thuc_lanh)} triệu đồng"
    )

# ==============================
# BẢNG CHI TIẾT
# ==============================
st.subheader("3. Bảng chi tiết tính toán")

du_lieu = [
    ["1", "Lương cơ bản", luong_co_ban],
    ["2", "Tiền thưởng", tien_thuong],
    ["3", "Phụ cấp tính BHXH", phu_cap_co_bhxh],
    ["4", "Phụ cấp không tính BHXH", phu_cap_khong_bhxh],
    ["5", "Tổng thu nhập", tong_thu_nhap],
    ["6", "Tiền đóng BHXH, BHYT, BHTN (theo tỷ lệ gộp)", tien_dong_bhxh],
    ["7", "Giảm trừ bản thân", GIAM_TRU_BAN_THAN],
    ["8", "Giảm trừ người phụ thuộc", GIAM_TRU_PHU_THUOC * so_nguoi_phu_thuoc],
    ["9", "Thu nhập tính thuế", thu_nhap_tinh_thue],
    ["10", "Thuế TNCN", thue_tncn],
    ["11", "TIỀN THỰC LÃNH", thuc_lanh],
]

bang = pd.DataFrame(
    du_lieu,
    columns=["STT", "Nội dung", "Số tiền (triệu đồng)"]
)

bang["Số tiền (triệu đồng)"] = bang[
    "Số tiền (triệu đồng)"
].apply(dinh_dang_tien)

st.dataframe(
    bang,
    hide_index=True,
    use_container_width=True
)

# ==============================
# CÔNG THỨC TÍNH
# ==============================
with st.expander("Xem công thức tính"):
    st.markdown("""
    **1. Tổng thu nhập**

    Tổng thu nhập = Lương cơ bản + Tiền thưởng + Phụ cấp tính BHXH
    + Phụ cấp không tính BHXH

    **2. Tiền bảo hiểm theo code gốc**

    Tiền bảo hiểm = (Lương cơ bản + Phụ cấp tính BHXH) × 10,5%

    **3. Thu nhập tính thuế**

    Thu nhập tính thuế = Tổng thu nhập − Giảm trừ bản thân
    − Giảm trừ người phụ thuộc − Tiền bảo hiểm

    **4. Tiền thực lãnh**

    Tiền thực lãnh = Tổng thu nhập − Tiền bảo hiểm − Thuế TNCN
    """)

st.warning("Lưu ý: Đây là công cụ tính theo các mức được thiết lập trong code gốc, "
    "không phải kết quả quyết toán thuế chính thức. Cần cập nhật mức giảm trừ, "
    "biểu thuế, căn cứ đóng và tỷ lệ bảo hiểm theo quy định áp dụng cho kỳ tính lương."
)

st.caption("Ứng dụng được xây dựng bằng Python và Streamlit.")
