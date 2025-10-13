# PDF Hairline Fix

Free, open‑source script that thickens too‑thin linework in PDF files. It uses the pypdf library to scan each page’s content stream and raise any stroke width set via the PDF “w” operator below a chosen threshold—similar to Adobe Acrobat Pro’s “Fix Hairlines” under Print Production.

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="docs/Before.png" alt="Before: thin 0 weight hairlines" /><br/>
        <sub><em>Before: hairline strokes from AutoCAD PDFs</em></sub>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="docs/After.png" alt="After: thicker, readable lines"/><br/>
        <sub><em>After: minimum line width enforced (e.g., 3 pt)</em></sub>
      </td>
    </tr>
  </table>
  
</div>

> Autocad‑produced PDFs that use a 0 lineweight are notoriously hard to read on paper. This tool enforces a minimum stroke width so plotted drawings remain legible.

## Features
- Enforces a minimum line width across all pages
- Lossless PDF editing (no rasterization)
- Works locally; no upload required
- Simple Python script; no Acrobat needed

## How it works
- Parses each page’s content stream with pypdf
- Iterates through content stream operators and operands using pypdf. (Does not use Regex, which can miss edge cases or change things it shouldn't).
- Finds the PDF operator `w` (set line width)
- If the width is below the configured threshold, replaces it with the threshold value
- Recompresses the content stream and writes a new PDF

Notes:
- Units are PDF user‑space units (points): 1 pt = 1/72 in ≈ 0.3528 mm

## Requirements
- Python 3.8+
- pypdf (install via pip)

## Install
PowerShell (Windows):

```powershell
python -m pip install --upgrade pip
python -m pip install pypdf
```

## Quick start
This repo contains a single script: `PDF-hairline-fix.py` with an example call at the bottom.

1. Put your PDF next to `PDF-hairline-fix.py`
2. Open `PDF-hairline-fix.py` and change the example line at the bottom:
   ```python
   modify_linewidths("your-input.pdf", "your-output.pdf", min_width=3)
   ```
3. Run it:
   ```powershell
   python .\PDF-hairline-fix.py
   ```

## Parameter
- `min_width` (float): Minimum stroke width to enforce. Example values:
  - 0.25–0.5 pt for subtle thickening
  - 3 pt for clearer plots
  - 5 pt for heavier lines

## Limitations
- Only updates explicit `w` operators; embedded graphic states, patterns, or transparency groups that define stroke widths are not touched
- Does not change dash patterns, colors, or fills, so if your drawing is gray or another light color, print it in monochrome black for best results.
- Some PDFs may have complex content streams; test results visually
- Only modifies vector line widths; does not affect images or raster content

## FAQ
- What happens to pages without content streams? They are copied unchanged.
- Is the change reversible? Your original PDF is preserved and a new file is created.
- Does this reduce quality? No rasterization is performed; only line widths are adjusted.

## License
MIT License. See `LICENSE` for details.


