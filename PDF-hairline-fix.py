from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, NameObject, FloatObject

def modify_linewidths(input_pdf, output_pdf, min_width=5):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page_num, page in enumerate(reader.pages, start=1):
        contents = page.get_contents()
        if contents is None:
            writer.add_page(page)
            continue

        # Parse content stream into operator sequence
        content = ContentStream(contents, reader)

        modified = False
        for operands, operator in content.operations:
            if operator == b"w":  # 'set line width' operator
                # compare numeric value; operands[0] is a PDF number object
                if float(operands[0]) < min_width:
                    print(f"Page {page_num}: {operands[0]} → {min_width}")
                    operands[0] = FloatObject(min_width)  # <-- use PDF number object
                    modified = True

        if modified:
            # Replace the page’s content with updated one
            page[NameObject("/Contents")] = writer._add_object(content)

        # Add page to writer first
        writer.add_page(page)

        # Re-compress content streams after the page is part of the writer
        writer.pages[-1].compress_content_streams()

    with open(output_pdf, "wb") as f:
        writer.write(f)

    print(f"Modified PDF saved to: {output_pdf}")

# Example usage
modify_linewidths("input.pdf", "output.pdf", min_width=3)
