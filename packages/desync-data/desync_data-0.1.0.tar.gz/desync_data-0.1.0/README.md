# desync-data

Utility functions for working with `PageData` objects from the [`desync_search`](https://pypi.org/project/desync-search/) library. These tools help you clean, filter, deduplicate, extract links, and export structured data from websites crawled via Desync.

---

## 🚀 Features

- 🔍 Remove boilerplate from page content (prefix/suffix delimiters)
- 📌 Filter pages by URL substring
- 🧹 Remove duplicate pages (based on `text_content`)
- 🔗 Extract link graphs (internal navigation structure)
- 📤 Export pages to CSV, JSON, or SQLite

---

## 📦 Installation

```bash
pip install desync-tools
