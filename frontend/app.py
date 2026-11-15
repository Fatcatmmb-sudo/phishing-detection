
import streamlit as st
import requests

# =========================
# CONFIGURATION
# =========================
API_URL = "http://127.0.0.1:8000/api/v1/predict"
TIMEOUT = 10

FEATURE_LABELS = {
    "has_ip": "Hostname sử dụng địa chỉ IP",
    "long_url": "URL có độ dài lớn",
    "has_at_symbol": "URL chứa ký tự @",
    "subdomain_count": "Số lượng subdomain",
    "has_prefix_suffix": "Hostname chứa dấu gạch ngang",
}

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Phishing Website Detection",
    page_icon="🛡️",
    layout="centered",
)

# =========================
# CSS
# =========================
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #3B82F6;
        font-size: 32px;
        font-weight: 700;
    }

    .sub-title {
        text-align: center;
        color: #94A3B8;
        margin-bottom: 35px;
    }

    .result-box {
        padding: 22px;
        border-radius: 12px;
        text-align: center;
        margin: 15px 0;
    }

    .phishing-box {
        background-color: #451A1A;
        border: 1px solid #EF4444;
        color: #FCA5A5;
    }

    .safe-box {
        background-color: #14532D;
        border: 1px solid #22C55E;
        color: #86EFAC;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown(
    '<div class="main-title">🛡️ Phishing Website Detection</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="sub-title">'
    'Hệ thống phát hiện website lừa đảo bằng Machine Learning'
    '</div>',
    unsafe_allow_html=True,
)

# =========================
# INPUT
# =========================
st.subheader("Kiểm tra website")

url = st.text_input(
    "Nhập địa chỉ Website cần kiểm tra",
    placeholder="https://example.com",
)

check_button = st.button(
    "🔍 Kiểm tra an toàn",
    use_container_width=True,
    type="primary",
)

# =========================
# PREDICTION
# =========================
if check_button:

    if not url.strip():
        st.warning("Vui lòng nhập URL cần kiểm tra.")

    else:
        try:
            with st.spinner("Đang phân tích website..."):

                response = requests.post(
                    API_URL,
                    json={"url": url.strip()},
                    timeout=TIMEOUT,
                )

            # -------------------------
            # SUCCESS
            # -------------------------
            if response.status_code == 200:

                result = response.json()

                is_phishing = result["is_phishing"]
                confidence = float(result["confidence"])
                details = result.get("details", {})

                if not 0 <= confidence <= 1:
                    raise ValueError("Confidence nằm ngoài khoảng 0 đến 1.")

                # Result
                if is_phishing:
                    st.markdown("""
                    <div class="result-box phishing-box">
                        <h2>⚠️ WEBSITE CÓ NGUY CƠ LỪA ĐẢO</h2>
                        <p>Không nên truy cập hoặc cung cấp thông tin cá nhân.</p>
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown("""
                    <div class="result-box safe-box">
                        <h2>✅ WEBSITE CÓ VẺ AN TOÀN</h2>
                        <p>Không phát hiện dấu hiệu phishing theo mô hình.</p>
                    </div>
                    """, unsafe_allow_html=True)

                # URL
                st.subheader("Thông tin kiểm tra")
                st.code(result.get("url", url))

                # Risk bar
                st.subheader("Mức độ rủi ro phishing")

                st.progress(confidence)

                st.write(f"**{confidence:.1%}**")

                if confidence >= 0.7:
                    st.error("Mức độ rủi ro cao.")
                elif confidence >= 0.4:
                    st.warning("Mức độ rủi ro trung bình.")
                else:
                    st.success("Mức độ rủi ro thấp.")

                # Details
                st.subheader("🔎 Chi tiết phân tích")

                if details:
                    for key, value in details.items():

                        label = FEATURE_LABELS.get(
                            key,
                            key.replace("_", " ").capitalize(),
                        )

                        if isinstance(value, bool):
                            display_value = "Có" if value else "Không"
                        else:
                            display_value = str(value)

                        st.write(f"**{label}:** {display_value}")

                else:
                    st.info("Không có thông tin chi tiết.")

                st.caption(
                    "Lưu ý: Kết quả là dự đoán của mô hình, "
                    "không đảm bảo website an toàn tuyệt đối."
                )

            # -------------------------
            # API ERRORS
            # -------------------------
            else:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {}

                error_code = error_data.get("error", "")
                error_message = error_data.get(
                    "message",
                    "Không thể phân tích URL.",
                )

                if response.status_code == 422:
                    st.error(f"URL không hợp lệ: {error_message}")

                elif response.status_code == 503:
                    if error_code == "MODEL_NOT_LOADED":
                        st.error(
                            "Mô hình chưa được tải. "
                            "Vui lòng thử lại sau."
                        )
                    else:
                        st.error(error_message)

                else:
                    st.error(error_message)

        # -------------------------
        # CONNECTION ERRORS
        # -------------------------
        except requests.exceptions.Timeout:
            st.error(
                "Yêu cầu quá thời gian chờ. Vui lòng thử lại."
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "Không thể kết nối Backend. "
                "Hãy kiểm tra server FastAPI."
            )

        except requests.exceptions.RequestException as error:
            st.error(f"Lỗi khi gửi yêu cầu: {error}")

        except (ValueError, KeyError):
            st.error(
                "Dữ liệu trả về từ Backend không đúng định dạng contract."
            )
