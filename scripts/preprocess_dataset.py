
import pandas as pd
from urllib.parse import urlsplit
from pathlib import Path

# ==========================================
# 1. ĐƯỜNG DẪN DATASET
# ==========================================

RAW_PATH = Path("data/raw/URL dataset.csv")
OUTPUT_DIR = Path("data/processed")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. ĐỌC DATASET GỐC
# ==========================================

df = pd.read_csv(RAW_PATH)

print("Tổng số URL ban đầu:", len(df))

# Giữ nguyên dataset gốc.
# Tạo bản sao để xử lý.
df = df.copy()

# ==========================================
# 3. CHUẨN HÓA URL VÀ TRÍCH XUẤT HOSTNAME
# ==========================================

def extract_hostname(url):
    if pd.isna(url):
        return None

    url = str(url).strip()

    # Chuyển defanged URL về dạng có thể phân tích.
    normalized_url = url.replace("[.]", ".")

    try:
        parsed = urlsplit(normalized_url)

        hostname = parsed.hostname

        if not hostname:
            return None

        return hostname.lower()

    except (ValueError, TypeError):
        return None


def normalize_url(url):
    if pd.isna(url):
        return None

    return str(url).strip().replace("[.]", ".")


df["normalized_url"] = df["url"].apply(normalize_url)

df["hostname"] = df["url"].apply(extract_hostname)

# ==========================================
# 4. PHÂN LOẠI URL
# ==========================================

df["has_hostname"] = df["hostname"].notna()

valid_df = df[df["has_hostname"]].copy()

rejected_df = df[~df["has_hostname"]].copy()

# ==========================================
# 5. KIỂM TRA NHÃN
# ==========================================

print("\nPhân bố nhãn ban đầu:")
print(df["type"].value_counts())

print("\nPhân bố nhãn URL hợp lệ:")
print(valid_df["type"].value_counts())

print("\nPhân bố nhãn URL bị loại khỏi tập phân tích:")
print(rejected_df["type"].value_counts())

# ==========================================
# 6. LƯU DATASET ĐÃ XỬ LÝ
# ==========================================

# Dataset hợp lệ, có hostname.
valid_df.to_csv(
    OUTPUT_DIR / "urls_cleaned.csv",
    index=False
)

# Các URL không có hostname.
rejected_df.to_csv(
    OUTPUT_DIR / "urls_rejected.csv",
    index=False
)

# Lưu báo cáo kiểm tra toàn bộ dữ liệu.
df.to_csv(
    OUTPUT_DIR / "url_audit.csv",
    index=False
)

# ==========================================
# 7. THỐNG KÊ KẾT QUẢ
# ==========================================

print("\n========== KẾT QUẢ TIỀN XỬ LÝ ==========")

print("Tổng URL ban đầu:", len(df))

print("URL có hostname:", len(valid_df))

print("URL không có hostname:", len(rejected_df))

print(
    "Số hostname khác nhau:",
    valid_df["hostname"].nunique()
)

print("\nĐã lưu:")
print("- data/processed/urls_cleaned.csv")
print("- data/processed/urls_rejected.csv")
print("- data/processed/url_audit.csv")
