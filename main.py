import streamlit as st
import pandas as pd
from vnstock3 import Vnstock
from datetime import datetime, timedelta

# Thiết lập môi trường cho Vnstock
import os
if "ACCEPT_TC" not in os.environ:
    os.environ["ACCEPT_TC"] = "tôi đồng ý"

# Danh sách các mã chứng khoán cần lấy dữ liệu
stock_codes = ['MBB', 'MBS', 'VPB', 'TCB', 'IDI']

# Hàm để lấy dữ liệu lịch sử
def get_data(symbol, start_date, end_date):
    stock = Vnstock().stock(symbol=symbol, source='VCI')
    df = stock.quote.history(start=start_date, end=end_date, interval='1D')
    df['Code'] = symbol  # Thêm cột mã vào DataFrame
    return df

# Tạo giao diện Streamlit
st.title('Ứng dụng theo dõi dữ liệu lịch sử')
st.write('Ứng dụng này thu thập và hiển thị dữ liệu lịch sử theo mã.')

# Tính toán ngày mặc định cho start_date (ngày hiện tại trừ đi 1 ngày)
default_start_date = datetime.now() - timedelta(days=1)
default_start_date_str = default_start_date.strftime('%Y-%m-%d')

# Widget để chọn ngày bắt đầu và kết thúc
start_date = st.date_input("Chọn ngày bắt đầu", value=default_start_date)
end_date = st.date_input("Chọn ngày kết thúc", pd.Timestamp('today').date())

# Chuyển định dạng ngày sang chuỗi "yyyy-mm-dd"
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

# Button để chạy chương trình
if st.button('Tra cứu'):
    # Tạo DataFrame để lưu trữ dữ liệu từ các mã
    combined_df = pd.DataFrame()

    # Tạo thanh progress bar và text để hiển thị tiến độ
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Tính tổng số mã
    total_codes = len(stock_codes)
    count = 0

    # Bắt đầu tính thời gian khi bắt đầu lặp
    start_time = datetime.now()

    # Lặp qua từng mã và lấy dữ liệu
    for code in stock_codes:
        try:
            data = get_data(code, start_date_str, end_date_str)
            data.reset_index(drop=True, inplace=True)  # Đặt lại index và loại bỏ cột index
            data = data[['Code'] + [col for col in data.columns if col != 'Code']]  # Di chuyển cột 'Code' lên đầu
            combined_df = pd.concat([combined_df, data], ignore_index=True)
        except Exception as e:
            st.error(f"Không thể lấy dữ liệu cho mã {code}. Lỗi: {e}")

        # Cập nhật tiến trình và thông tin
        count += 1
        progress_percent = int(count / total_codes * 100)
        progress_bar.progress(progress_percent)
        status_text.text(f"Đang xử lý {count}/{total_codes} - {progress_percent}% hoàn thành.")

    # Kết thúc tính thời gian khi hoàn thành lặp
    end_time = datetime.now()

    # Tính toán số giây thực thi
    time_elapsed = (end_time - start_time).total_seconds()
    time_elapsed_rounded = round(time_elapsed)

    # Hiển thị thông tin thời gian thực thi
    status_text.text(f"Thời gian hoàn thành: {time_elapsed_rounded} giây")

    # Hiển thị bảng dữ liệu tổng hợp trên giao diện
    st.subheader('Bảng dữ liệu tổng hợp:')
    st.write(combined_df, index=False)  # Không hiển thị cột index
