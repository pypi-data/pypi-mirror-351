# sortbybytes

> Sort and format human-readable byte-size strings.

`sortbybytes` provides two simple, yet powerful functions:

- `get_size(bytes, suffix="B")` — Convert an integer byte count into a human-readable string (e.g. `1253656 → "1.20 MB"`).  
- `sortvalue(values, reverse=False)` — Sort a list of human-readable byte-size strings (e.g. `"25.6 MB"`, `"5.6 KB"`, `"12.5 GB"`) in ascending (default) or descending order.

---

## 🚀 Installation

```bash
pip install sortbybytes
