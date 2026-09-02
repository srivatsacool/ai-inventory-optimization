import pathlib
p=pathlib.Path("11_src/_make_nb08.py")
t=p.read_text(encoding="utf-8")
old = '''m5_parts = []
for chunk_idx, chunk_origins in enumerate([origin_dates[:4], origin_dates[4:]]):
    print(f"M5 chunk {chunk_idx+1}/2 origins {[d.date() for d in chunk_origins]}")
    t0 = time.time()
    part = run_global_lstm_for_dataset(m5_common, "m5", pivot_or_mat_is_pivot=False, origins_override=chunk_origins)
    print(f"M5 chunk {chunk_idx+1} {len(part):,} rows — {time.time()-t0:.0f}s")
    m5_parts.append(part)
# fix origin numbering (chunk-local 1..4 -> global 1..8)
m5_lstm = __import__("pandas").concat([m5_parts[0].assign(origin=m5_parts[0]["origin"]), m5_parts[1].assign(origin=m5_parts[1]["origin"]+4)], ignore_index=True)
print(f"M5 global LSTM total {len(m5_lstm):,} rows")
print(m5_lstm.head(3).to_string())
\"\"\"))'''

new = '''m5_part1 = run_global_lstm_for_dataset(m5_common, "m5", pivot_or_mat_is_pivot=False, origins_override=origin_dates[:4])
print(f"M5 chunk 1/2 {len(m5_part1):,} rows")
m5_part1["origin"] = m5_part1["origin"]  # 1..4 already
\"\"\"))

cells.append(code(r\"\"\"
m5_part2 = run_global_lstm_for_dataset(m5_common, "m5", pivot_or_mat_is_pivot=False, origins_override=origin_dates[4:])
print(f"M5 chunk 2/2 {len(m5_part2):,} rows")
m5_part2["origin"] = m5_part2["origin"] + 4  # 1..4 -> 5..8
m5_lstm = __import__("pandas").concat([m5_part1, m5_part2], ignore_index=True)
print(f"M5 global LSTM total {len(m5_lstm):,} rows")
print(m5_lstm.head(3).to_string())
\"\"\"))'''

if old in t:
    t=t.replace(old, new)
    print("patched M5 split into 2 cells")
else:
    print("M5 old not found")
    raise SystemExit

old_sit = '''sit_parts = []
for chunk_idx, chunk_origins in enumerate([origin_dates[:4], origin_dates[4:]]):
    print(f"SIT chunk {chunk_idx+1}/2 origins {[d.date() for d in chunk_origins]}")
    t0 = time.time()
    part = run_global_lstm_for_dataset(pivot, "store_item_demand", pivot_or_mat_is_pivot=True, origins_override=chunk_origins)
    print(f"SIT chunk {chunk_idx+1} {len(part):,} rows — {time.time()-t0:.0f}s")
    sit_parts.append(part)
sit_lstm = __import__("pandas").concat([sit_parts[0].assign(origin=sit_parts[0]["origin"]), sit_parts[1].assign(origin=sit_parts[1]["origin"]+4)], ignore_index=True)
print(f"Store Item global LSTM total {len(sit_lstm):,} rows — {time.time()-t0:.0f}s")
print(sit_lstm.head(3).to_string())'''

new_sit = '''sit_part1 = run_global_lstm_for_dataset(pivot, "store_item_demand", pivot_or_mat_is_pivot=True, origins_override=origin_dates[:4])
print(f"SIT chunk 1/2 {len(sit_part1):,} rows")
sit_part1["origin"] = sit_part1["origin"]
\"\"\"))

cells.append(code(r\"\"\"
sit_part2 = run_global_lstm_for_dataset(pivot, "store_item_demand", pivot_or_mat_is_pivot=True, origins_override=origin_dates[4:])
print(f"SIT chunk 2/2 {len(sit_part2):,} rows")
sit_part2["origin"] = sit_part2["origin"] + 4
sit_lstm = __import__("pandas").concat([sit_part1, sit_part2], ignore_index=True)
print(f"Store Item global LSTM total {len(sit_lstm):,} rows")
print(sit_lstm.head(3).to_string())
\"\"\"))'''

if old_sit in t:
    t=t.replace(old_sit, new_sit)
    print("patched SIT")
else:
    print("SIT old not found")
    raise SystemExit

p.write_text(t, encoding="utf-8")
print("done")
