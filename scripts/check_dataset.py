
import pandas as pd
from urllib.parse import urlparse

# Đọc dataset gốc
df = pd.read_csv("data/raw/URL dataset.csv")

invalid_urls = []

# Kiểm tra hostname từng URL
for index, row in df.iterrows():
    url = str(row["url"])

    try:
        host = urlparse(url).hostname

        if host is None:
            invalid_urls.append({
                "index": index,
                "url": url,
                "type": row["type"]
            })

    except ValueError:
        invalid_urls.append({
            "index": index,
            "url": url,
            "type": row["type"]
        })

# Hiển thị URL bất thường
print("SỐ URL BẤT THƯỜNG:", len(invalid_urls))

for item in invalid_urls:
    print(item)

# Thống kê nhãn của URL bất thường
if invalid_urls:
    invalid_df = pd.DataFrame(invalid_urls)

    print("\nPHÂN BỐ NHÃN URL BẤT THƯỜNG:")
    print(invalid_df["type"].value_counts())
