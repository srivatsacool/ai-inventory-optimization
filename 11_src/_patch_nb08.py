import pathlib
p=pathlib.Path("11_src/_make_nb08.py")
t=p.read_text(encoding="utf-8")

# 1) Add origins_override param to function
t=t.replace(
    "def run_global_lstm_for_dataset(mat, dataset_name, pivot_or_mat_is_pivot=False):",
    "def run_global_lstm_for_dataset(mat, dataset_name, pivot_or_mat_is_pivot=False, origins_override=None):"
)
t=t.replace(
    "    for oi, od in enumerate(origin_dates, 1):",
    "        origins = origins_override if origins_override is not None else origin_dates\n        for oi, od in enumerate(origins, 1):",
    1  # only first occurrence (inside function)
)

# 2) Split M5 invocation into two chunks
old_m5 = '''t0 = time.time()
m5_lstm = run_global_lstm_for_dataset(m5_common, "m5", pivot_or_mat_is_pivot=False)
print(f"M5 global LSTM total {len(m5_lstm):,} rows — {time.time()-t0:.0f}s")
print(m5_lstm.head(3).to_string())'''

new_m5 = '''m5_parts = []
for chunk_idx, chunk_origins in enumerate([origin_dates[:4], origin_dates[4:]]):
    print(f"M5 chunk {chunk_idx+1}/2 origins {[d.date() for d in chunk_origins]}")
    t0 = time.time()
    part = run_global_lstm_for_dataset(m5_common, "m5", pivot_or_mat_is_pivot=False, origins_override=chunk_origins)
    print(f"M5 chunk {chunk_idx+1} {len(part):,} rows — {time.time()-t0:.0f}s")
    m5_parts.append(part)
# fix origin numbering (chunk-local 1..4 -> global 1..8)
m5_lstm = __import__("pandas").concat([m5_parts[0].assign(origin=m5_parts[0]["origin"]), m5_parts[1].assign(origin=m5_parts[1]["origin"]+4)], ignore_index=True)
print(f"M5 global LSTM total {len(m5_lstm):,} rows")
print(m5_lstm.head(3).to_string())'''

if old_m5 in t:
    t=t.replace(old_m5, new_m5)
    print("patched M5")
else:
    print("M5 invoke not found")
    raise SystemExit

# 3) Similarly split SIT
old_sit = '''t0 = time.time()
# pivot is dates(1238) x series(500); transpose inside helper expects dates x series
sit_lstm = run_global_lstm_for_dataset(pivot, "store_item_demand", pivot_or_mat_is_pivot=True)
print(f"Store Item global LSTM total {len(sit_lstm):,} rows — {time.time()-t0:.0f}s")
print(sit_lstm.head(3).to_string())'''

new_sit = '''sit_parts = []
for chunk_idx, chunk_origins in enumerate([origin_dates[:4], origin_dates[4:]]):
    print(f"SIT chunk {chunk_idx+1}/2 origins {[d.date() for d in chunk_origins]}")
    t0 = time.time()
    part = run_global_lstm_for_dataset(pivot, "store_item_demand", pivot_or_mat_is_pivot=True, origins_override=chunk_origins)
    print(f"SIT chunk {chunk_idx+1} {len(part):,} rows — {time.time()-t0:.0f}s")
    sit_parts.append(part)
sit_lstm = __import__("pandas").concat([sit_parts[0].assign(origin=sit_parts[0]["origin"]), sit_parts[1].assign(origin=sit_parts[1]["origin"]+4)], ignore_index=True)
print(f"Store Item global LSTM total {len(sit_lstm):,} rows — {time.time()-t0:.0f}s")
print(sit_lstm.head(3).to_string())'''

if old_sit in t:
    t=t.replace(old_sit, new_sit)
    print("patched SIT")
else:
    print("SIT invoke not found")
    raise SystemExit

p.write_text(t, encoding="utf-8")
print("done")
