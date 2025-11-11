import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CHUNKS_FILE = BASE_DIR / "data" / "extracted_chunks.csv"

df = pd.read_csv(CHUNKS_FILE)
print(f"Loaded {len(df)} chunks")

# --- 1. Empty text ---
empty_chunks = df[df["text"].str.strip() == ""]
print(f"Empty chunks: {len(empty_chunks)}")

# --- 2. Garbage (non-word) chunks ---
pattern = r"^[\W\d\s]+$"
garbage = df[df["text"].str.match(pattern, na=False)]
print(f"Garbage chunks: {len(garbage)}")

# --- 3. Duplicates ---
duplicates = df["text"].duplicated().sum()
print(f"Duplicate text chunks: {duplicates}")

# --- 4. Word count distribution ---
df["word_count"] = df["text"].str.split().apply(len)
print("\nWord count distribution:")
print(df["word_count"].describe().round(2))

# --- 5. Unique word diversity ---
df["unique_words"] = df["text"].apply(lambda x: len(set(x.lower().split())))
print("\nUnique word count distribution:")
print(df["unique_words"].describe().round(2))

# --- 6. Preview few high/low diversity chunks ---
print("\nLowest diversity (possible boilerplate):")
print(df.nsmallest(3, "unique_words")[["filename", "page", "unique_words", "word_count", "text"]])

print("\nHighest diversity (long pages):")
print(df.nlargest(3, "unique_words")[["filename", "page", "unique_words", "word_count"]])
