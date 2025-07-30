# 📦 FileHandler

![Build](https://github.com/charlie6027/filehandler/actions/workflows/python-package.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-brightgreen)

A flexible and beginner-friendly Python package for safe and cross-platform file operations.  
Supports both **traditional** (Unix-style `~`) and **modern** (`pathlib`) path handling modes with built-in logging, error management, and content retrieval.

---

## ✨ Features

- 🗂️ Read, write, and append to files with automatic encoding (`utf-8`)
- 🔁 Switchable file handling modes: `Traditional` and `Modern`
- 🧠 FullPathBuilder for safe home-relative paths
- 🔐 Exception-safe file operations
- 📄 License: MIT (free for all use)

---

## 📥 Installation

```bash
git clone https://github.com/charlie6027/filehandler.git
cd filehandler
pip install -e .
```

---

## 🧪 Running Tests

```bash
python -m unittest discover -s tests
```

---

## 🚀 Usage Example

```python
from filehandler import FileHandler, FileHandleMode

handler = FileHandler()
handler.write('~/Documents/test.txt', 'Hello, world!')
print(handler.read('~/Documents/test.txt'))
```

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!  
Feel free to check [issues page](https://github.com/charlie6027/filehandler/issues).

---

## 🧑 Author

**Charlie Sky**  
Feel free to ⭐ the repo if you find it useful!
