import fitz  # PyMuPDF
import os, json, re

resource_dir = os.path.join(os.path.dirname(__file__), 'resource')
pdfs = [f for f in os.listdir(resource_dir) if f.endswith('.pdf')][:3]

results = []
for fname in pdfs:
    path = os.path.join(resource_dir, fname)
    try:
        doc = fitz.open(path)
        first_page_text = doc[0].get_text()[:300] if len(doc) > 0 else ''
        size_kb = round(os.path.getsize(path) / 1024)
        results.append({
            'filename': fname,
            'pages': len(doc),
            'size_kb': size_kb,
            'preview': first_page_text.strip()[:150]
        })
        doc.close()
    except Exception as e:
        results.append({'filename': fname, 'error': str(e)})

print(json.dumps(results, ensure_ascii=False, indent=2))
