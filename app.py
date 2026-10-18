
import streamlit as st
import pandas as pd
import os
from io import BytesIO

# ==================================================
# 1. CẤU HÌNH TRANG WEB
# ==================================================
st.set_page_config(
    page_title="Ứng dụng tính lương thực lãnh",
    page_icon="💰",
    layout="wide"
)

if os.path.exists("LOGO.jpg"):
    st.image("LOGO.jpg", width=180)

st.title("💰 PHẦN MỀM TÍNH LƯƠNG KHANH KHANH")
st.caption(
    "Tính lương hàng loạt cho tối đa 500 người lao động, "
    "tổng hợp bảo hiểm, thuế TNCN và xuất báo cáo Excel."
)

st.info(
    "Đơn vị nhập liệu: triệu đồng/tháng. "
    "Các mức giảm trừ và biểu thuế được giữ theo code ban đầu."
)

# ==================================================
# 2. CÁC HÀM XỬ LÝ
# ==================================================
def dinh_dang_tien(so_tien):
    return f"{so_tien:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tinh_thue_tncn(thu_nhap_tinh_thue):
    """Thu nhập và số thuế đều tính theo triệu đồng."""
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


def tao_bang_nhan_vien(so_luong):
    """Tạo bảng nhập liệu cho số lượng nhân viên được chọn."""
    return pd.DataFrame({
        "Mã nhân viên": [f"NV{i:03d}" for i in range(1, so_luong + 1)],
        "Họ và tên": ["" for _ in range(so_luong)],
        "Lương cơ bản": [15.0 for _ in range(so_luong)],
        "Tiền thưởng": [2.0 for _ in range(so_luong)],
        "Phụ cấp tính BHXH": [1.0 for _ in range(so_luong)],
        "Phụ cấp không tính BHXH": [0.5 for _ in range(so_luong)],
        "Số người phụ thuộc": [1 for _ in range(so_luong)]
    })


def cap_nhat_so_dong():
    """Thay đổi số nhân viên nhưng giữ dữ liệu đã nhập nếu còn dòng."""
    so_luong_moi = st.session_state["so_luong_nv"]
    bang_cu = st.session_state["df_nhanvien"].copy()

    if len(bang_cu) < so_luong_moi:
        so_dong_them = so_luong_moi - len(bang_cu)
        bat_dau = len(bang_cu) + 1

        bang_moi = pd.DataFrame({
            "Mã nhân viên": [
                f"NV{i:03d}"
                for i in range(bat_dau, so_luong_moi + 1)
            ],
            "Họ và tên": ["" for _ in range(so_dong_them)],
            "Lương cơ bản": [15.0 for _ in range(so_dong_them)],
            "Tiền thưởng": [2.0 for _ in range(so_dong_them)],
            "Phụ cấp tính BHXH": [1.0 for _ in range(so_dong_them)],
            "Phụ cấp không tính BHXH": [0.5 for _ in range(so_dong_them)],
            "Số người phụ thuộc": [1 for _ in range(so_dong_them)]
        })

        bang_cu = pd.concat([bang_cu, bang_moi], ignore_index=True)

    elif len(bang_cu) > so_luong_moi:
        bang_cu = bang_cu.iloc[:so_luong_moi].copy()

    st.session_state["df_nhanvien"] = bang_cu.reset_index(drop=True)
    st.session_state["editor_version"] += 1


def tinh_bang_luong(df):
    """Tính lương cho toàn bộ nhân viên trong bảng."""
    ket_qua = df.copy()

    cot_tien = [
        "Lương cơ bản",
        "Tiền thưởng",
        "Phụ cấp tính BHXH",
        "Phụ cấp không tính BHXH"
    ]

    for cot in cot_tien:
        ket_qua[cot] = pd.to_numeric(
            ket_qua[cot], errors="coerce"
        ).fillna(0).clip(lower=0)

    ket_qua["Số người phụ thuộc"] = pd.to_numeric(
        ket_qua["Số người phụ thuộc"], errors="coerce"
    ).fillna(0).clip(lower=0).astype(int)

    # Tổng thu nhập
    ket_qua["Tổng thu nhập"] = (
        ket_qua["Lương cơ bản"]
        + ket_qua["Tiền thưởng"]
        + ket_qua["Phụ cấp tính BHXH"]
        + ket_qua["Phụ cấp không tính BHXH"]
    )

    # Bảo hiểm người lao động đóng: 10,5%
    ket_qua["Bảo hiểm người lao động đóng"] = (
        ket_qua["Lương cơ bản"]
        + ket_qua["Phụ cấp tính BHXH"]
    ) * 0.105

    # Giảm trừ theo công thức gốc
    ket_qua["Giảm trừ bản thân"] = 15.5
    ket_qua["Giảm trừ người phụ thuộc"] = (
        ket_qua["Số người phụ thuộc"] * 6.2
    )

    # Thu nhập tính thuế trước khi xử lý âm
    ket_qua["Thu nhập tính thuế trước xử lý âm"] = (
        ket_qua["Tổng thu nhập"]
        - ket_qua["Giảm trừ bản thân"]
        - ket_qua["Giảm trừ người phụ thuộc"]
        - ket_qua["Bảo hiểm người lao động đóng"]
    )

    # Thu nhập tính thuế không âm
    ket_qua["Thu nhập tính thuế"] = (
        ket_qua["Thu nhập tính thuế trước xử lý âm"].clip(lower=0)
    )

    ket_qua["Thuế TNCN phải nộp"] = (
        ket_qua["Thu nhập tính thuế"].apply(tinh_thue_tncn)
    )

    # Lương thực lãnh
    ket_qua["Tiền thực lãnh"] = (
        ket_qua["Tổng thu nhập"]
        - ket_qua["Bảo hiểm người lao động đóng"]
        - ket_qua["Thuế TNCN phải nộp"]
    )

    return ket_qua


def tao_file_excel(df_ket_qua):
    """Xuất file Excel gồm bảng lương và bảng tổng hợp."""
    cot_tien = [
        "Lương cơ bản",
        "Tiền thưởng",
        "Phụ cấp tính BHXH",
        "Phụ cấp không tính BHXH",
        "Tổng thu nhập",
        "Bảo hiểm người lao động đóng",
        "Giảm trừ bản thân",
        "Giảm trừ người phụ thuộc",
        "Thu nhập tính thuế trước xử lý âm",
        "Thu nhập tính thuế",
        "Thuế TNCN phải nộp",
        "Tiền thực lãnh"
    ]

    tong_hop = pd.DataFrame({
        "Chỉ tiêu": [
            "Số người lao động",
            "Tổng lương cơ bản",
            "Tổng tiền thưởng",
            "Tổng phụ cấp tính BHXH",
            "Tổng phụ cấp không tính BHXH",
            "Tổng thu nhập",
            "Tổng bảo hiểm người lao động đóng",
            "Tổng thu nhập tính thuế",
            "Tổng thuế TNCN phải nộp",
            "Tổng tiền thực lãnh"
        ],
        "Giá trị": [
            len(df_ket_qua),
            df_ket_qua["Lương cơ bản"].sum(),
            df_ket_qua["Tiền thưởng"].sum(),
            df_ket_qua["Phụ cấp tính BHXH"].sum(),
            df_ket_qua["Phụ cấp không tính BHXH"].sum(),
            df_ket_qua["Tổng thu nhập"].sum(),
            df_ket_qua["Bảo hiểm người lao động đóng"].sum(),
            df_ket_qua["Thu nhập tính thuế"].sum(),
            df_ket_qua["Thuế TNCN phải nộp"].sum(),
            df_ket_qua["Tiền thực lãnh"].sum()
        ]
    })

    file_excel = BytesIO()

    with pd.ExcelWriter(file_excel, engine="openpyxl") as writer:
        # Sheet 1: Tổng hợp
        tong_hop.to_excel(
            writer, index=False, sheet_name="Tong hop"
        )

        # Sheet 2: Chi tiết toàn bộ nhân viên
        df_ket_qua.to_excel(
            writer, index=False, sheet_name="Bang luong"
        )

        # Định dạng độ rộng cột và số tiền
        for ten_sheet in ["Tong hop", "Bang luong"]:
            ws = writer.sheets[ten_sheet]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions

            for column_cells in ws.columns:
                max_length = max(
                    len(str(cell.value)) if cell.value is not None else 0
                    for cell in column_cells
                )
                ws.column_dimensions[
                    column_cells[0].column_letter
                ].width = min(max_length + 3, 32)

        ws_luong = writer.sheets["Bang luong"]
        header_map = {
            cell.value: cell.column
            for cell in ws_luong[1]
        }

        for cot in cot_tien:
            if cot in header_map:
                so_cot = header_map[cot]
                for row in range(2, ws_luong.max_row + 1):
                    ws_luong.cell(row, so_cot).number_format = '#,##0.000'

        ws_tong = writer.sheets["Tong hop"]
        for row in range(2, ws_tong.max_row + 1):
            ws_tong.cell(row, 2).number_format = '#,##0.000'

        # Số lượng nhân viên là số nguyên
        ws_tong["B2"].number_format = "0"

    file_excel.seek(0)
    return file_excel.getvalue()


# ==================================================
# 3. KHỞI TẠO DỮ LIỆU
# ==================================================
if "df_nhanvien" not in st.session_state:
    st.session_state["df_nhanvien"] = tao_bang_nhan_vien(1)

if "so_luong_nv" not in st.session_state:
    st.session_state["so_luong_nv"] = 1

if "editor_version" not in st.session_state:
    st.session_state["editor_version"] = 0


# ==================================================
# 4. CHỌN SỐ LƯỢNG NGƯỜI LAO ĐỘNG
# ==================================================
st.subheader("1. Chọn số lượng người lao động")

st.number_input(
    "Số người cần tính lương",
    min_value=1,
    max_value=500,
    value=st.session_state["so_luong_nv"],
    step=1,
    key="so_luong_nv",
    on_change=cap_nhat_so_dong
)

st.caption(
    "Có thể nhập tối đa 500 người trong một lần. "
    "Khi giảm số lượng, những dòng vượt quá số lượng mới sẽ bị loại."
)


# ==================================================
# 5. NHẬP DỮ LIỆU NHÂN VIÊN
# ==================================================
st.subheader("2. Nhập thông tin nhân viên")

st.write(
    "Bạn có thể nhấp trực tiếp vào từng ô để nhập hoặc chỉnh sửa. "
    "Các khoản lương nhập theo triệu đồng/tháng."
)

bang_nhap = st.data_editor(
    st.session_state["df_nhanvien"],
    key=f"bang_nhanvien_{st.session_state['editor_version']}",
    num_rows="fixed",
    hide_index=True,
    use_container_width=True,
    height=420,
    column_config={
        "Mã nhân viên": st.column_config.TextColumn(
            "Mã nhân viên", required=True
        ),
        "Họ và tên": st.column_config.TextColumn(
            "Họ và tên", required=True
        ),
        "Lương cơ bản": st.column_config.NumberColumn(
            "Lương cơ bản (triệu đồng)",
            min_value=0.0,
            step=0.5,
            format="%.3f"
        ),
        "Tiền thưởng": st.column_config.NumberColumn(
            "Tiền thưởng (triệu đồng)",
            min_value=0.0,
            step=0.5,
            format="%.3f"
        ),
        "Phụ cấp tính BHXH": st.column_config.NumberColumn(
            "Phụ cấp tính BHXH (triệu đồng)",
            min_value=0.0,
            step=0.5,
            format="%.3f"
        ),
        "Phụ cấp không tính BHXH": st.column_config.NumberColumn(
            "Phụ cấp không tính BHXH (triệu đồng)",
            min_value=0.0,
            step=0.5,
            format="%.3f"
        ),
        "Số người phụ thuộc": st.column_config.NumberColumn(
            "Số người phụ thuộc",
            min_value=0,
            max_value=100,
            step=1,
            format="%d"
        )
    }
)

# Lưu dữ liệu vừa chỉnh sửa
st.session_state["df_nhanvien"] = bang_nhap.copy()


# ==================================================
# 6. NÚT TÍNH LƯƠNG
# ==================================================
st.divider()

if st.button(
    "🧮 TÍNH LƯƠNG TOÀN BỘ NHÂN VIÊN",
    type="primary",
    use_container_width=True
):
    df_tinh = st.session_state["df_nhanvien"].copy()

    # Kiểm tra mã nhân viên
    df_tinh["Mã nhân viên"] = (
        df_tinh["Mã nhân viên"].fillna("").astype(str).str.strip()
    )

    if (df_tinh["Mã nhân viên"] == "").any():
        st.error("Vui lòng nhập mã nhân viên cho tất cả các dòng.")
        st.stop()

    if df_tinh["Mã nhân viên"].duplicated().any():
        st.error("Mã nhân viên bị trùng. Vui lòng kiểm tra lại.")
        st.stop()

    if df_tinh["Họ và tên"].fillna("").astype(str).str.strip().eq("").any():
        st.error("Vui lòng nhập họ và tên cho tất cả nhân viên.")
        st.stop()

    # Tính toán
    df_ket_qua = tinh_bang_luong(df_tinh)

    # Lưu kết quả vào session để dùng cho lần tải xuống
    st.session_state["df_ket_qua"] = df_ket_qua

    st.success(
        f"Đã tính lương cho {len(df_ket_qua)} người lao động."
    )


# ==================================================
# 7. HIỂN THỊ KẾT QUẢ VÀ XUẤT FILE
# ==================================================
if "df_ket_qua" in st.session_state:
    df_ket_qua = st.session_state["df_ket_qua"]

    # Tránh hiển thị kết quả cũ nếu số lượng đã thay đổi
    df_hien_tai = st.session_state["df_nhanvien"]

    if (
        len(df_ket_qua) != len(df_hien_tai)
        or not df_ket_qua["Mã nhân viên"].reset_index(drop=True).equals(
            df_hien_tai["Mã nhân viên"].fillna("").astype(str).str.strip()
            .reset_index(drop=True)
        )
        or not df_ket_qua["Họ và tên"].fillna("").astype(str).reset_index(drop=True).equals(
            df_hien_tai["Họ và tên"].fillna("").astype(str).reset_index(drop=True)
        )
        or not df_ket_qua[
            [
                "Lương cơ bản",
                "Tiền thưởng",
                "Phụ cấp tính BHXH",
                "Phụ cấp không tính BHXH",
                "Số người phụ thuộc"
            ]
        ].reset_index(drop=True).equals(
            df_hien_tai[
                [
                    "Lương cơ bản",
                    "Tiền thưởng",
                    "Phụ cấp tính BHXH",
                    "Phụ cấp không tính BHXH",
                    "Số người phụ thuộc"
                ]
            ].reset_index(drop=True)
        )
    ):
        st.warning(
            "Dữ liệu đã thay đổi sau lần tính trước. "
            "Hãy nhấn nút tính lương lại để cập nhật kết quả."
        )
    else:
        st.divider()
        st.subheader("3. Tổng hợp quỹ lương")

        tong_thu_nhap = df_ket_qua["Tổng thu nhập"].sum()
        tong_bao_hiem = df_ket_qua["Bảo hiểm người lao động đóng"].sum()
        tong_thue = df_ket_qua["Thuế TNCN phải nộp"].sum()
        tong_thuc_lanh = df_ket_qua["Tiền thực lãnh"].sum()

        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)

        c1.metric(
            "Số người lao động",
            f"{len(df_ket_qua):,} người"
        )
        c2.metric(
            "Tổng thu nhập",
            f"{dinh_dang_tien(tong_thu_nhap)} triệu"
        )
        c3.metric(
            "Tổng bảo hiểm",
            f"{dinh_dang_tien(tong_bao_hiem)} triệu"
        )
        c4.metric(
            "Tổng thuế TNCN",
            f"{dinh_dang_tien(tong_thue)} triệu"
        )

        st.success(
            f"💵 TỔNG LƯƠNG THỰC LÃNH: "
            f"{dinh_dang_tien(tong_thuc_lanh)} TRIỆU ĐỒNG/THÁNG"
        )

        st.subheader("4. Bảng lương chi tiết")

        cot_hien_thi = [
            "Mã nhân viên",
            "Họ và tên",
            "Lương cơ bản",
            "Tiền thưởng",
            "Phụ cấp tính BHXH",
            "Phụ cấp không tính BHXH",
            "Tổng thu nhập",
            "Bảo hiểm người lao động đóng",
            "Số người phụ thuộc",
            "Thu nhập tính thuế",
            "Thuế TNCN phải nộp",
            "Tiền thực lãnh"
        ]

        df_hien_thi = df_ket_qua[cot_hien_thi].copy()

        cot_so_tien = [
            "Lương cơ bản",
            "Tiền thưởng",
            "Phụ cấp tính BHXH",
            "Phụ cấp không tính BHXH",
            "Tổng thu nhập",
            "Bảo hiểm người lao động đóng",
            "Thu nhập tính thuế",
            "Thuế TNCN phải nộp",
            "Tiền thực lãnh"
        ]

        df_hien_thi[cot_so_tien] = df_hien_thi[cot_so_tien].round(3)

        st.dataframe(
            df_hien_thi,
            use_container_width=True,
            hide_index=True,
            height=500
        )

        # Xuất Excel
        file_excel = tao_file_excel(df_ket_qua)

        st.download_button(
            label="📥 TẢI FILE EXCEL TỔNG HỢP (.xlsx)",
            data=file_excel,
            file_name="bang_luong_tong_hop.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        # Xuất CSV
        csv_data = df_ket_qua.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="📄 TẢI FILE CSV",
            data=csv_data,
            file_name="bang_luong_tong_hop.csv",
            mime="text/csv",
            use_container_width=True
        )

        with st.expander("📘 Xem công thức tính lương"):
            st.markdown("""
            **1. Tổng thu nhập**

            = Lương cơ bản + Thưởng + Phụ cấp tính BHXH
            + Phụ cấp không tính BHXH.

            **2. Bảo hiểm người lao động đóng**

            = (Lương cơ bản + Phụ cấp tính BHXH) × 10,5%.

            **3. Thu nhập tính thuế**

            = Tổng thu nhập − Bảo hiểm − Giảm trừ bản thân
            − Giảm trừ người phụ thuộc.

            **4. Thuế TNCN**

            Tính theo biểu thuế và công thức trong chương trình gốc.

            **5. Tiền thực lãnh**

            = Tổng thu nhập − Bảo hiểm − Thuế TNCN.

            Đơn vị của các số tiền là triệu đồng.
            """)

st.divider()

st.caption(
    "Lưu ý: Chương trình đang sử dụng giả định giảm trừ bản thân "
    "15,5 triệu đồng/tháng, giảm trừ người phụ thuộc 6,2 triệu đồng/tháng "
    "và biểu thuế theo code ban đầu. Cần cập nhật các thông số này "
    "nếu sử dụng để tính lương thực tế theo quy định pháp luật hiện hành."
)
