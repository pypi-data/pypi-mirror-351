# 🗂️ Sortium

A Python utility to **automatically sort files** in a folder by their **type** (e.g., Images, Documents, Videos, etc.) and by their **last modified date**.

---

## 📚 Table of Contents
- [🗂️ Sortium](#️-sortium)
  - [📚 Table of Contents](#-table-of-contents)
  - [🚀 Features](#-features)
  - [🛠️ Installation](#️-installation)
  - [🧪 Run Tests](#-run-tests)
  - [👤 Author](#-author)
  - [📄 License](#-license)
  - [🤝 Contributing](#-contributing)
  - [📚 Documentation \& Issues](#-documentation--issues)
  - [📦 PyPI (Coming Soon)](#-pypi-coming-soon)

## 🚀 Features

- ✅ Organize files into folders based on their type (e.g., Images, Documents, Videos, Music, Others)
- 📅 Optionally further sort files by their last modified date within each category
- 📁 Optionally flatten subdirectories into a single folder

---

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/Sarthak-G0yal/SortPy.git
cd SortPy

# Install in editable mode
pip install -e .
```

## 🧪 Run Tests

```bash
pytest src/tests --cov=src/Structa
```

---

## 👤 Author

**Sarthak Goyal**
📧 [sarthakgoyal487@gmail.com](mailto:sarthakgoyal487@gmail.com)

---

## 📄 License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## 🤝 Contributing

Contributions are welcome and appreciated! 🎉

If you'd like to improve this project, here's how to get started:

1. **Fork** the repository.  
2. **Create a new branch** for your feature or fix.  
3. **Write tests** for your changes.  
4. **Commit** your changes with clear messages.  
5. **Open a pull request** and describe what you’ve changed.

Please follow conventional commit guidelines and ensure your code is linted and tested before submitting.

---

## 📚 Documentation & Issues

This project is documented using [Sphinx](https://www.sphinx-doc.org/).

- 📖 **Documentation**: Full documentation can be viewed in the HTML version in [`_build/html/`](./_build/html/index.html) after running `make html`.

- 🐛 **Report Bugs / Request Features**: [Open an Issue](https://github.com/Sarthak-G0yal/SortPy/issues)

---

## 📦 PyPI (Coming Soon)

This project is not yet available on [PyPI](https://pypi.org), but you can install it locally:

```bash
git clone https://github.com/Sarthak-G0yal/SortPy.git
cd SortPy
pip install -e .
```

Once published, you’ll be able to install it with:

```bash
pip install sortpy
```

Stay tuned for updates! 🚀