
# Problem 25 — Similar Pair of Text Books (Python + JIRA)

This package contains:
- `similar_books.py`: the Python program.
- `sample_texts/`: five example `.txt` files for a quick demo.
- (Optional) `jira_issues.csv`: a ready-made CSV to import issues into Jira Cloud.

## How to run

1. Put your 5 `.txt` files into a folder (or use `sample_texts`).
2. Run the program:
   ```bash
   python similar_books.py --dir "/mnt/data/p25_similarity_jira_package/sample_texts" --topk 15 --export results
   ```
3. Output:
   - Prints Top-15 words per file (with counts and normalized frequencies).
   - Shows pairwise similarity by COMMON Top-15 words and Jaccard.
   - Exports two CSVs: `results_pairs.csv`, `results_topk.csv`.

## Notes

- Cleaning: Keep only alphanumeric characters; convert letters to uppercase.
- Stopwords removed everywhere (counting, totals, normalization): `A, AND, AN, OF, IN, THE`.
- Normalized frequency = `count / (total tokens after cleaning & stopword removal)`.
- "More similar" = pair with the most common Top-15 words (tie break: higher Jaccard).
