# doc2vision

**doc2vision** is a robust Python utility designed to convert documents and image files — including **PDF**, **JPG**, **PNG**, and **TIF** — into clean, high-quality, **RGB images optimized for multimodal LLM input** (e.g., image + text AI models). It handles low-quality scans, rotated pages, and multi-page PDFs with ease.

Perfect for use in OCR preprocessing, AI pipelines, or anywhere clean document-to-image conversion is needed.

---

## 🚀 Features

- ✅ Converts **PDFs** (including multipage) into individual high-quality images
- ✅ Supports **JPG, PNG, TIF, TIFF**
- ✅ Converts all output to standard **RGB format**
- ✅ Optionally auto-corrects skewed scans
- ✅ Gracefully handles edge cases like:
  - Low-resolution scans
  - Rotated or misaligned documents
  - Corrupt or unsupported files
  - Mixed DPI across pages

---

## 📦 Installation

```bash
pip install doc2vision
```

You may also need to install [Poppler](https://github.com/jalan/papermill/wiki/Installing-Poppler) if you're using PDF input:

* **macOS:** `brew install poppler`
* **Ubuntu/Debian:** `sudo apt-get install poppler-utils`

---

## 🧠 Usage

```python
from doc2vision import convert_to_llm_ready_images

# Basic usage
images = convert_to_llm_ready_images("example.pdf")

# With skew correction
images = convert_to_llm_ready_images("example.pdf", correct_skew=True)

# With resizing (preserving aspect ratio)
images = convert_to_llm_ready_images("example.pdf", resize_to=1500)

# Iterate over output Pillow images
for img in images:
    img.show()  # Or save, analyze, etc.
```

---

## 🛠️ Parameters

| Parameter      | Type   | Default | Description                                                       |
| -------------- | ------ | ------- | ----------------------------------------------------------------- |
| `file_path`    | `str`  | —       | Path to your input file (PDF, JPG, PNG, TIF)                      |
| `correct_skew` | `bool` | `False` | If `True`, attempts to auto-detect and fix rotation               |
| `resize_to`    | `int`  | `None`  | If set, resizes image height to this value (keeping aspect ratio) |

---

## 📁 Output

Returns a list of Pillow `Image.Image` objects, one per page/image:

```python
[List[PIL.Image.Image]]
```

All output images are:

* RGB
* Preprocessed (rotation + optional resize)
* Clean and ready for AI or OCR pipelines

---

## 🤖 Perfect For

* Feeding documents into **multimodal LLMs**
* Preprocessing for **OCR or Document AI**
* Converting messy scans into standardized visuals
* AI agents needing consistent image inputs

---

## 📜 License

MIT License — feel free to use, extend, and contribute.

---

## 👨‍💻 Author

Built with 💙 by Russell Van Curen
GitHub: [@vancuren](https://github.com/vancuren)
Website: [vancuren.net](https://vancuren.net)


## Changelog

0.1.0 - Initial release

0.1.1 - Updated project description and readme.