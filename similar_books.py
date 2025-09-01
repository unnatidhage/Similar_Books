#!/usr/bin/env python3
"""
similar_books.py
----------------
Identify the most similar pair of text books (text files) among a given set of files.

Similarity (as per the assignment's "simple but crude" spec):
- Clean text to keep only alphanumeric characters. Convert letters to UPPERCASE.
- Remove the six stopwords: A, AND, AN, OF, IN, THE
- Compute the 15 most frequent words for each file (TOP-K configurable).
- Compare every pair of files by counting how many TOP-K words are COMMON between them.
- The pair with the highest count of common TOP-K words is considered "more similar".
- (Extra) We also compute Jaccard similarity between the TOP-K word sets as a tie-breaker.
- (Extra) We report normalized frequency for the TOP-K words = count / total_filtered_tokens.

Usage:
    python similar_books.py --dir path/to/texts --topk 15 --export "results"
This will print results and create `results_pairs.csv` and `results_topk.csv` in the current directory.
"""

import argparse
import os
import re
from collections import Counter
from itertools import combinations

STOPWORDS = {"A", "AND", "AN", "OF", "IN", "THE"}

def clean_and_tokenize(text: str):
    """
    Keep only alphanumeric characters; replace everything else with spaces.
    Convert to uppercase and split on whitespace.
    """
    text = re.sub(r'[^0-9A-Za-z]+', ' ', text)  # non-alnum -> space
    text = text.upper()
    tokens = text.split()
    # filter out stopwords
    tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens

def read_tokens_from_file(path: str):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read()
    return clean_and_tokenize(raw)

def topk_frequencies(tokens, k=15):
    total = len(tokens)
    counts = Counter(tokens)
    most_common = counts.most_common(k)
    # normalized frequency excludes stopwords already (we removed them above)
    top_table = [
        {
            "WORD": w,
            "COUNT": c,
            "NORM_FREQ": (c / total) if total else 0.0
        } for (w, c) in most_common
    ]
    return top_table, total

def similarity_metrics(top_set_a, top_set_b):
    inter = top_set_a & top_set_b
    union = top_set_a | top_set_b
    common_count = len(inter)
    jaccard = (len(inter) / len(union)) if union else 0.0
    return common_count, jaccard

def list_text_files(d):
    return sorted([
        os.path.join(d, f) for f in os.listdir(d)
        if f.lower().endswith(".txt") and os.path.isfile(os.path.join(d, f))
    ])

def main():
    parser = argparse.ArgumentParser(description="Find most similar pair of text files using TOP-K common words.")
    parser.add_argument("--dir", required=True, help="Directory containing .txt files (books/pages).")
    parser.add_argument("--topk", type=int, default=15, help="K for top frequent words (default: 15).")
    parser.add_argument("--export", type=str, default="", help="Export prefix for CSVs, e.g., 'results' -> results_pairs.csv")
    args = parser.parse_args()

    files = list_text_files(args.dir)
    if len(files) < 2:
        print("Please provide at least 2 .txt files in the directory.")
        return

    print(f"Found {len(files)} .txt files:")
    for f in files:
        print(" -", os.path.basename(f))
    print()

    file_topk = {}
    file_totals = {}

    # Compute TOP-K tables for each file
    for fpath in files:
        tokens = read_tokens_from_file(fpath)
        top_table, total = topk_frequencies(tokens, k=args.topk)
        file_key = os.path.basename(fpath)
        file_topk[file_key] = top_table
        file_totals[file_key] = total

    # Print TOP-K per file
    for fname in files:
        key = os.path.basename(fname)
        print(f"=== {key} ===")
        print(f"Total tokens (after cleaning & stopword removal): {file_totals[key]}")
        print(f"Top-{args.topk} words:")
        for row in file_topk[key]:
            print(f"  {row['WORD']:>15}  COUNT={row['COUNT']:<5}  NORM_FREQ={row['NORM_FREQ']:.4f}")
        print()

    # Pairwise similarity
    pairs = []
    for a, b in combinations([os.path.basename(f) for f in files], 2):
        set_a = {row["WORD"] for row in file_topk[a]}
        set_b = {row["WORD"] for row in file_topk[b]}
        common_count, jaccard = similarity_metrics(set_a, set_b)
        pairs.append({
            "FILE_A": a,
            "FILE_B": b,
            "COMMON_TOPK_WORDS": common_count,
            "JACCARD": round(jaccard, 4)
        })

    # Sort by common words desc, then by jaccard desc
    pairs.sort(key=lambda x: (x["COMMON_TOPK_WORDS"], x["JACCARD"]), reverse=True)

    print("=== Pairwise similarity (by common TOP-K words, then Jaccard) ===")
    for p in pairs:
        print(f"{p['FILE_A']}  vs  {p['FILE_B']}  ->  COMMON={p['COMMON_TOPK_WORDS']}, JACCARD={p['JACCARD']}")
    print()

    if pairs:
        best = pairs[0]
        print("Most similar pair (by this method):")
        print(f" -> {best['FILE_A']} and {best['FILE_B']} (COMMON={best['COMMON_TOPK_WORDS']}, JACCARD={best['JACCARD']})")

    # Optional CSV export
    if args.export:
        pairs_csv = f"{args.export}_pairs.csv"
        topk_csv = f"{args.export}_topk.csv"

        import csv
        with open(pairs_csv, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["FILE_A","FILE_B","COMMON_TOPK_WORDS","JACCARD"])
            writer.writeheader()
            for row in pairs:
                writer.writerow(row)

        # Flatten TOP-K table for all files
        with open(topk_csv, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["FILE","WORD","COUNT","NORM_FREQ","TOTAL_TOKENS","TOPK"])
            writer.writeheader()
            for file_key, rows in file_topk.items():
                total = file_totals[file_key]
                for r in rows:
                    writer.writerow({
                        "FILE": file_key,
                        "WORD": r["WORD"],
                        "COUNT": r["COUNT"],
                        "NORM_FREQ": f"{r['NORM_FREQ']:.6f}",
                        "TOTAL_TOKENS": total,
                        "TOPK": args.topk
                    })

        print(f"\nExported: {pairs_csv} and {topk_csv}")

if __name__ == "__main__":
    main()
