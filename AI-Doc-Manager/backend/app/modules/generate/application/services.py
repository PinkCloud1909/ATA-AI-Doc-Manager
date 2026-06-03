from __future__ import annotations

import html
import io
import textwrap
import zipfile


def build_runbook_text(prompt: str) -> str:
    topic = prompt.strip()
    return "\n".join(
        [
            f"RUNBOOK: {topic}",
            "",
            "1. Muc tieu",
            "Dam bao quy trinh duoc thuc hien nhat quan, co the kiem tra lai va co phuong an rollback.",
            "",
            "2. Pham vi ap dung",
            "Ap dung cho doi ngu van hanh, phat trien va cac ben lien quan khi can xu ly yeu cau duoc mo ta.",
            "",
            "3. Dieu kien tien quyet",
            "- Co quyen truy cap he thong lien quan.",
            "- Co ban sao cau hinh/du lieu quan trong neu can rollback.",
            "- Co kenh lien lac voi nguoi phe duyet va nguoi chiu trach nhiem.",
            "",
            "4. Cac buoc thuc hien",
            "- Ghi nhan yeu cau, muc do uu tien va thoi diem bat dau.",
            "- Kiem tra trang thai dich vu, log, metric va cac thay doi gan nhat.",
            "- Thuc hien tung buoc theo checklist, ghi lai bang chung sau moi buoc.",
            "- Neu gap loi nghiem trong, dung thao tac va chuyen sang rollback.",
            "",
            "5. Kiem tra sau xu ly",
            "- Xac nhan health check thanh cong.",
            "- Kiem tra chuc nang chinh va du lieu dau ra.",
            "- Cap nhat ticket/bien ban voi ket qua va thoi gian hoan tat.",
            "",
            "6. Rollback",
            "- Khoi phuc cau hinh/phien ban truoc do.",
            "- Kiem tra lai dich vu va thong bao cho cac ben lien quan.",
            "",
            "7. Tieu chi hoan thanh",
            "Quy trinh duoc xem la hoan thanh khi he thong on dinh, khong con canh bao bat thuong va thong tin da duoc luu lai.",
        ]
    )


def build_docx_bytes(title: str, content: str) -> bytes:
    paragraphs = [title, *content.splitlines()]
    body = "".join(
        f"<w:p><w:r><w:t>{html.escape(line) or ' '}</w:t></w:r></w:p>"
        for line in paragraphs
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body></w:document>"
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>",
        )
        zf.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/>'
            "</Relationships>",
        )
        zf.writestr("word/document.xml", document_xml)
    return buffer.getvalue()


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf_bytes(title: str, content: str) -> bytes:
    lines = [title, "", *content.splitlines()]
    commands = ["BT", "/F1 11 Tf", "72 760 Td"]
    for index, line in enumerate(lines[:42]):
        if index:
            commands.append("0 -16 Td")
        commands.append(f"({_pdf_escape(line[:100])}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", "replace")
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        b"5 0 obj << /Length " + str(len(stream)).encode() + b" >> stream\n" + stream + b"\nendstream endobj\n",
    ]
    buffer = io.BytesIO()
    buffer.write(b"%PDF-1.4\n")
    offsets = []
    for obj in objects:
        offsets.append(buffer.tell())
        buffer.write(obj)
    xref = buffer.tell()
    buffer.write(f"xref\n0 {len(objects) + 1}\n".encode())
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets:
        buffer.write(f"{offset:010d} 00000 n \n".encode())
    buffer.write(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    )
    return buffer.getvalue()
