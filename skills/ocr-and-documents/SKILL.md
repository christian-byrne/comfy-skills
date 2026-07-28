---
name: ocr-and-documents
description: 'Extract text from PDFs and scanned documents. Choose between pymupdf (fast, text-based PDFs) and marker-pdf (OCR for scanned/complex layouts). Split, merge, and search PDFs. Use when asked to read PDFs, extract text from documents, OCR scanned pages, or process document files.'
interaction: autonomous
type: leaf
---

# OCR & Document Processing

Extract text from PDFs, scanned documents, and office files.

## Decision Flow

```
Is it a URL?
  → Yes: Try read_web_page first (handles many PDFs)
  → No: Continue ↓

Is the PDF text-based (selectable text)?
  → Yes: Use pymupdf (fast, ~25MB)
  → No (scanned/images): Use marker-pdf (OCR, ~3-5GB)

Does it have complex layouts, equations, or tables?
  → Yes: Use marker-pdf
  → No: Use pymupdf
```

## pymupdf — Fast Text Extraction (~25MB)

Best for: text-based PDFs, quick extraction, splitting/merging.

```bash
pip install pymupdf
```

```python
import fitz  # pymupdf

# Extract all text
doc = fitz.open("document.pdf")
for page_num, page in enumerate(doc):
    text = page.get_text()
    print(f"--- Page {page_num + 1} ---")
    print(text)

# Extract text from specific pages
page = doc[0]  # first page
print(page.get_text())

# Search for text
for page in doc:
    results = page.search_for("keyword")
    if results:
        print(f"Found on page {page.number + 1}: {len(results)} matches")

# Split PDF
doc = fitz.open("large.pdf")
for i in range(len(doc)):
    single = fitz.open()
    single.insert_pdf(doc, from_page=i, to_page=i)
    single.save(f"page_{i+1}.pdf")

# Merge PDFs
merged = fitz.open()
for pdf_file in ["part1.pdf", "part2.pdf", "part3.pdf"]:
    merged.insert_pdf(fitz.open(pdf_file))
merged.save("merged.pdf")

# Extract images
for page in doc:
    for img_index, img in enumerate(page.get_images()):
        xref = img[0]
        base_image = doc.extract_image(xref)
        with open(f"image_{page.number}_{img_index}.{base_image['ext']}", "wb") as f:
            f.write(base_image["image"])
```

## marker-pdf — OCR for Scanned Documents (~3-5GB)

Best for: scanned documents, complex layouts, equations, tables.

```bash
pip install marker-pdf
```

```bash
# Convert single PDF to markdown
marker_single document.pdf --output_dir ./output/

# Convert directory of PDFs
marker ./pdfs/ --output_dir ./output/ --workers 4

# With specific options
marker_single document.pdf --output_dir ./output/ --langs English
```

## arXiv Papers

```python
# Use read_web_page — it handles arXiv PDFs well
# read_web_page("https://arxiv.org/pdf/2402.03300")
# Or use the abstract page for a quick summary:
# read_web_page("https://arxiv.org/abs/2402.03300")
```

## DOCX Files

```bash
pip install python-docx
```

```python
from docx import Document
doc = Document("document.docx")
for para in doc.paragraphs:
    print(para.text)
# Tables
for table in doc.tables:
    for row in table.rows:
        print([cell.text for cell in row.cells])
```

## Tips

- Always try `read_web_page` first for URLs — it handles many document formats
- pymupdf is 100x faster than marker-pdf for text-based PDFs
- marker-pdf requires significant disk space and RAM — only install when needed
- For very large PDFs, process page-by-page to avoid memory issues
