
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedGroupKFold

# ==========================================
# 1. ĐỌC DỮ LIỆU ĐÃ LÀM SẠCH
# ==========================================

DATA_DIR = Path("data/processed")

INPUT_PATH = DATA_DIR / "urls_cleaned.csv"

df = pd.read_csv(INPUT_PATH)

print("Tổng URL:", len(df))
print("Tổng hostname:", df["hostname"].nunique())

# ==========================================
# 2. KHAI BÁO NHÃN VÀ NHÓM
# ==========================================

X = df["normalized_url"]

y = df["type"]

groups = df["hostname"]

# ==========================================
# 3. CHIA THÀNH 20 FOLDS
# ==========================================

splitter = StratifiedGroupKFold(
    n_splits=20,
    shuffle=True,
    random_state=42
)

fold_ids = pd.Series(-1, index=df.index)

for fold, (_, test_indices) in enumerate(
    splitter.split(X, y, groups)
):
    fold_ids.iloc[test_indices] = fold

# ==========================================
# 4. GÁN FOLDS VÀO 3 TẬP
# ==========================================

train_df = df[fold_ids < 14].copy()

validation_df = df[
    (fold_ids >= 14) & (fold_ids < 17)
].copy()

test_df = df[fold_ids >= 17].copy()

# ==========================================
# 5. KIỂM TRA RÒ RỈ HOSTNAME
# ==========================================

train_hosts = set(train_df["hostname"])

validation_hosts = set(validation_df["hostname"])

test_hosts = set(test_df["hostname"])

train_val_overlap = train_hosts & validation_hosts

train_test_overlap = train_hosts & test_hosts

val_test_overlap = validation_hosts & test_hosts

print("\n========== KIỂM TRA HOSTNAME ==========")

print("Train và Validation trùng:", len(train_val_overlap))

print("Train và Test trùng:", len(train_test_overlap))

print("Validation và Test trùng:", len(val_test_overlap))

assert len(train_val_overlap) == 0
assert len(train_test_overlap) == 0
assert len(val_test_overlap) == 0

# ==========================================
# 6. LƯU 3 TẬP DỮ LIỆU
# ==========================================

train_df.to_csv(DATA_DIR / "train.csv", index=False)

validation_df.to_csv(
    DATA_DIR / "validation.csv",
    index=False
)

test_df.to_csv(DATA_DIR / "test.csv", index=False)

# ==========================================
# 7. THỐNG KÊ KẾT QUẢ
# ==========================================

datasets = {
    "Train": train_df,
    "Validation": validation_df,
    "Test": test_df
}

print("\n========== KẾT QUẢ CHIA DATASET ==========")

for name, data in datasets.items():

    print(f"\n{name}")

    print("Số URL:", len(data))

    print("Số hostname:", data["hostname"].nunique())

    print("Tỷ lệ:", round(len(data) / len(df) * 100, 2), "%")

    print("\nPhân bố nhãn:")

    print(data["type"].value_counts(normalize=True) * 100)

print("\nĐÃ CHIA DỮ LIỆU THÀNH CÔNG!")

print("Train:", DATA_DIR / "train.csv")

print("Validation:", DATA_DIR / "validation.csv")

print("Test:", DATA_DIR / "test.csv")
