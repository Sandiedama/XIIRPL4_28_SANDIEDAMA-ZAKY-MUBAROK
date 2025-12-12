from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, HexColor
from reportlab.lib.utils import ImageReader
import os
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Frame, PageTemplate

def draw_kop_surat(c, y_start):
    """Gambar kop surat terpusat, garis penuh lebar halaman."""
    page_width = c._pagesize[0]
    margin = 40
    center_x = page_width / 2
    logo_path = os.path.join(os.path.dirname(__file__), '../assets/logo.png')
    logo_width = 120
    logo_height = 65
    logo_y = y_start - logo_height + 8

    # Tempatkan logo di margin kiri
    logo_x = margin
    if os.path.exists(logo_path):
        c.drawImage(ImageReader(logo_path), logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')

    c.setFillColor(black)
    # Title
    c.setFont("Helvetica-Bold", 20)
    title = "PT. MULTIDAYA MITRA SINERGI"
    c.drawCentredString(center_x, y_start + 2, title)
    # Subtitle
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(HexColor("#FF2800"))
    c.drawCentredString(center_x, y_start - 18, "PROJECT & ENGINEERING SOLUTIONS")
    # Address & contact
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(center_x, y_start - 38, "Jl. Cipendawa Lama No.21 Kota Bekasi")
    c.setFont("Helvetica", 12)
    c.drawCentredString(center_x, y_start - 54, "Telepon 0811-9698-237, OFFICE (021) 82635464")
    c.setFont("Helvetica", 11)
    c.drawCentredString(center_x, y_start - 70, "Website : multidayamitrasinergi.com")

    # Garis penuh
    c.setLineWidth(2)
    c.line(margin, y_start - 92, page_width - margin, y_start - 92)
    c.setLineWidth(1)
    c.line(margin, y_start - 97, page_width - margin, y_start - 97)

    return y_start - 120

def export_in_pdf(filename, data, tanggal, kop_path=None):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 60
    y = draw_kop_surat(c, y)
    # Beri jarak turun sedikit dari kop
    y -= 10
    # Jenis laporan (center)
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(black)
    text_title = "Laporan Barang Masuk (IN)"
    title_w = c.stringWidth(text_title, "Helvetica-Bold", 15)
    c.drawString((width - title_w) / 2, y, text_title)
    y -= 24
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(black)
    c.drawString(40, y, f"Tanggal: {tanggal}")
    y -= 30
    headers = ['No', 'Part Number', 'Nama Barang', 'Kategori', 'Qty', 'Penerima']
    table_data = [headers]
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    styles = getSampleStyleSheet()
    para_style = styles['Normal']
    para_style.fontName = 'Helvetica'
    para_style.fontSize = 9
    para_style.leading = 14
    for idx, row in enumerate(data):
        table_data.append([
            str(idx+1),
            Paragraph(str(row['partnumber']), para_style),
            Paragraph(str(row['nama']), para_style),
            str(row['kategori']),
            str(row['qty']),
            str(row['penerima'])
        ])
    col_widths = [30, 100, 120, 60, 35, 60]
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF2800')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'CENTER'),
        ('ALIGN', (3,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ROWHEIGHT', (0,1), (-1,-1), 32),
    ]))
    table.wrapOn(c, width, height)
    table_y = y - table._height
    # Center the table horizontally
    table_x = max(30, (width - table._width) / 2)
    table.drawOn(c, table_x, table_y)

    # ------- Area tanda tangan (Menu IN) -------
    # Ambil nama penerima dari data (diasumsikan sama untuk semua baris)
    penerima_name = ""
    if data:
        try:
            penerima_name = str(data[0].get('penerima', '') or '')
        except Exception:
            penerima_name = ""

    # Posisi blok tanda tangan di dekat bawah halaman
    # Jarak label ke nama dibuat ±60 point (~2cm) agar lebih lega
    sign_base_y = 85
    block_width = 200

    c.setFont("Helvetica", 11)

    # Garis dan label untuk Penerima
    penerima_x = 60
    # Label lebih tinggi, beri ruang cukup untuk tanda tangan
    c.drawString(penerima_x, sign_base_y + 90, "Penerima")
    if penerima_name:
        # Nama dengan underline (garis sebagai underline teks)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(penerima_x, sign_base_y + 30, penerima_name)
        name_w = c.stringWidth(penerima_name, "Helvetica-Bold", 11)
        c.line(penerima_x, sign_base_y + 28, penerima_x + name_w, sign_base_y + 28)
        c.setFont("Helvetica", 11)

    c.save()

def truncate(text, maxlen):
    text = str(text)
    return text if len(text) <= maxlen else text[:maxlen-3] + '...'

def export_out_pdf(filename, data, tanggal, kop_path=None):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 60
    y = draw_kop_surat(c, y)
    # Beri jarak turun sedikit dari kop
    y -= 10
    # Jenis laporan & tanggal di bawah kop surat (center)
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(black)
    text_title = "Laporan Barang Keluar (OUT)"
    title_w = c.stringWidth(text_title, "Helvetica-Bold", 15)
    c.drawString((width - title_w) / 2, y, text_title)
    y -= 24
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(black)
    c.drawString(40, y, f"Tanggal: {tanggal}")
    y -= 30
    # Remarks per barang
    remarks_lines = []
    for row in data:
        nama = row.get('nama', '-')
        qty = row.get('qty', '-')
        remarks = row.get('remarks', '')
        if remarks:
            remarks_lines.append(f"- {nama} (Qty: {qty}) : {remarks}")
    if remarks_lines:
        c.setFont("Helvetica", 11)
        c.setFillColor(black)
        c.drawString(40, y, "Remarks:")
        y -= 18
        c.setFont("Helvetica-Oblique", 10)
        for line in remarks_lines:
            if len(line) > 120:
                line = line[:117] + '...'
            c.drawString(60, y, line)
            y -= 16
        y -= 6
    # Data tabel
    headers = ['No', 'Part Number', 'Nama Barang', 'Kategori', 'QTY', 'Pengeluar', 'Penerima', 'Menyetujui']
    table_data = [headers]
    styles = getSampleStyleSheet()
    para_style = styles['Normal']
    para_style.fontName = 'Helvetica'
    para_style.fontSize = 9
    para_style.leading = 14
    for idx, row in enumerate(data):
        table_data.append([
            str(idx+1),
            Paragraph(str(row['partnumber']), para_style),
            Paragraph(str(row['nama']), para_style),
            str(row['kategori']),
            str(row['qty']),
            str(row['pengeluar']),
            str(row['penerima']),
            str(row['approver'])
        ])
    col_widths = [30, 100, 120, 60, 35, 60, 60, 60]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF2800')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'CENTER'),
        ('ALIGN', (3,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ROWHEIGHT', (0,1), (-1,-1), 32),
    ]))
    table.wrapOn(c, width, height)
    table_y = y - table._height
    # Center the table horizontally
    table_x = max(30, (width - table._width) / 2)
    table.drawOn(c, table_x, table_y)

    # ------- Area tanda tangan (Menu OUT) -------
    # Ambil nama-nama dari data (diasumsikan sama untuk semua baris)
    pengeluar_name = penerima_name = approver_name = ""
    if data:
        try:
            first = data[0]
            pengeluar_name = str(first.get('pengeluar', '') or '')
            penerima_name = str(first.get('penerima', '') or '')
            approver_name = str(first.get('approver', '') or '')
        except Exception:
            pass

    # Posisikan blok tanda tangan dekat bawah halaman
    # Jarak label ke nama dibuat ±60 point (~2cm) agar lebih lega
    sign_base_y = 85
    block_width = 170

    c.setFont("Helvetica", 11)

    # Pengeluar
    pengeluar_x = 70
    c.drawString(pengeluar_x, sign_base_y + 90, "Pengeluar")
    if pengeluar_name:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(pengeluar_x, sign_base_y + 30, pengeluar_name)
        name_w = c.stringWidth(pengeluar_name, "Helvetica-Bold", 11)
        c.line(pengeluar_x, sign_base_y + 28, pengeluar_x + name_w, sign_base_y + 28)
        c.setFont("Helvetica", 11)

    # Penerima
    penerima_x = pengeluar_x + block_width + 60
    c.drawString(penerima_x, sign_base_y + 90, "Penerima")
    if penerima_name:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(penerima_x, sign_base_y + 30, penerima_name)
        name_w = c.stringWidth(penerima_name, "Helvetica-Bold", 11)
        c.line(penerima_x, sign_base_y + 28, penerima_x + name_w, sign_base_y + 28)
        c.setFont("Helvetica", 11)

    # Menyetujui / Approver
    approver_x = penerima_x + block_width + 60
    c.drawString(approver_x, sign_base_y + 90, "Menyetujui")
    if approver_name:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(approver_x, sign_base_y + 30, approver_name)
        name_w = c.stringWidth(approver_name, "Helvetica-Bold", 11)
        c.line(approver_x, sign_base_y + 28, approver_x + name_w, sign_base_y + 28)
        c.setFont("Helvetica", 11)

    c.save()

def export_table_only_pdf(filename, data, headers):
    """
    Export PDF hanya tabel (tanpa kop surat, tanpa tanggal, tanpa tanda tangan).
    headers: list judul kolom
    data: list of list/baris (isi tabel)
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 100  # Margin atas
    # Siapkan data tabel
    table_data = [headers]
    styles = getSampleStyleSheet()
    para_style = styles['Normal']
    para_style.fontName = 'Helvetica'
    para_style.fontSize = 10
    para_style.leading = 12
    for row in data:
        row_out = []
        for i, val in enumerate(row):
            # Kolom Nama Barang (index 2) pakai Paragraph agar wrap
            if i == 2:
                row_out.append(Paragraph(str(val), para_style))
            else:
                row_out.append(str(val))
        table_data.append(row_out)
    # Lebar kolom proporsional (bisa diubah sesuai kebutuhan)
    col_widths = [30, 70, 200, 70, 35, 70, 70, 70][:len(headers)]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF2800')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),  # No
        ('ALIGN', (1,1), (1,-1), 'CENTER'),  # Part Number
        ('ALIGN', (3,1), (-1,-1), 'CENTER'), # Kategori dst
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#FF2800')),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ROWHEIGHT', (0,1), (-1,-1), 30),
    ]))
    table.wrapOn(c, width, height)
    table.drawOn(c, 30, y - table._height)
    c.save()

def export_barang_pdf(filename, data):
    """
    Export PDF untuk list barang (landscape).
    data: list of dict dengan key: partnumber, nama, kategori, satuan, stok, rop
    """
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Frame, PageTemplate
    from reportlab.lib.pagesizes import A4
    width, height = landscape(A4)

    # Margin dan frame untuk konten (tabel) – top lebih besar agar tidak menabrak header
    left_margin = 30
    right_margin = 30
    top_margin = 220  # ruang untuk kop + judul + tanggal
    bottom_margin = 40
    frame = Frame(left_margin, bottom_margin, width - left_margin - right_margin, height - top_margin - bottom_margin, id='frame')

    # Fungsi header tiap halaman
    def draw_header(canvas_obj, doc):
        y_top = height - 60
        y_after = draw_kop_surat(canvas_obj, y_top)
        # Sedikit turun
        y_after -= 14
        # Title center
        canvas_obj.setFont("Helvetica-Bold", 15)
        title = "Laporan List Barang"
        title_w = canvas_obj.stringWidth(title, "Helvetica-Bold", 15)
        canvas_obj.drawString((width - title_w) / 2, y_after, title)
        # Tanggal kiri
        canvas_obj.setFont("Helvetica-Bold", 12)
        canvas_obj.drawString(40, y_after - 20, f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4),
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
    )

    # Siapkan tabel
    headers = ["No", "Part Number", "Nama Barang", "Kategori", "Satuan", "Stok", "ROP"]
    table_data = [headers]
    styles = getSampleStyleSheet()
    para_style = styles["Normal"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 9
    para_style.leading = 13

    for idx, row in enumerate(data, start=1):
        table_data.append([
            str(idx),
            Paragraph(str(row.get("partnumber", "")), para_style),
            Paragraph(str(row.get("nama", "")), para_style),
            Paragraph(str(row.get("kategori", "")), para_style),
            Paragraph(str(row.get("satuan", "")), para_style),
            str(row.get("stok", "")),
            str(row.get("rop", "")),
        ])

    col_widths = [30, 110, 200, 90, 70, 70, 70]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF2800')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (1,1), (4,-1), 'LEFT'),
        ('ALIGN', (5,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ROWHEIGHT', (0,1), (-1,-1), 26),
    ]))

    elements = []
    # Spacer kecil sebelum tabel untuk memastikan tidak menabrak header
    elements.append(Spacer(1, 12))
    elements.append(table)
    # Signature block untuk halaman terakhir (kolom di kanan, teks rata kiri)
    sig_style = styles["Normal"].clone('sig')
    sig_style.alignment = TA_LEFT
    sig_style.fontName = "Helvetica-Bold"
    sig_style.fontSize = 11
    sig_style.leading = 14
    
    # Buat tabel dengan 2 kolom: spacer kiri dan tanda tangan kanan (teks rata kiri)
    sig_col_width = 250
    right_margin_sig = 5  # Margin sangat kecil agar lebih ke kanan
    sig_table_data = [
        ['', Paragraph("Mengetahui,", sig_style)],
        ['', Paragraph("Kepala Gudang", sig_style)],
        ['', ''],  # Spacer baris 1
        ['', ''],  # Spacer baris 2 - tambah spacing
        ['', ''],  # Spacer baris 3 - tambah spacing lagi
        ['', Paragraph("<u>Khalid</u>", sig_style)],
    ]
    # Hitung lebar spacer agar kolom kanan lebih ke kanan
    # Total lebar tabel = width - left_margin - right_margin_sig
    available_width = width - left_margin - right_margin_sig
    spacer_width = available_width - sig_col_width
    sig_table = Table(sig_table_data, colWidths=[spacer_width, sig_col_width])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('TOPPADDING', (1, 0), (1, -1), 2),
        ('BOTTOMPADDING', (1, 0), (1, -1), 2),
    ]))
    
    sig_block = [
        Spacer(1, 24),
        sig_table,
    ]

    from reportlab.platypus import KeepTogether
    elements.append(KeepTogether(sig_block))

    def _draw_header(canvas_obj, doc):
        # Hitung posisi berdasarkan pagesize agar konsisten di semua halaman
        page_w, page_h = doc.pagesize
        y_top = page_h - 60
        y_after = draw_kop_surat(canvas_obj, y_top)
        y_after -= 14
        canvas_obj.setFont("Helvetica-Bold", 12)
        canvas_obj.drawString(40, y_after - 22, f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        canvas_obj.setFont("Helvetica-Bold", 15)
        title = "Laporan List Barang"
        title_w = canvas_obj.stringWidth(title, "Helvetica-Bold", 15)
        canvas_obj.drawCentredString(page_w / 2, y_after - 2, title)

    doc.build(elements, onFirstPage=_draw_header, onLaterPages=_draw_header)

def export_custom_pdf(filename, data, headers):
    width, height = landscape(A4)
    styles = getSampleStyleSheet()
    para_style = styles['Normal']
    para_style.fontName = 'Helvetica'
    para_style.fontSize = 9
    para_style.leading = 14
    # Margin
    leftMargin = 30
    rightMargin = 30
    topMargin = 40
    bottomMargin = 30
    # Frame untuk halaman pertama (ada kop surat, remarks, dsb)
    frame_first = Frame(leftMargin, bottomMargin, width-leftMargin-rightMargin, height-topMargin-bottomMargin-100, id='first')
    # Frame untuk halaman berikutnya (tanpa kop surat, tabel mulai dari atas)
    frame_later = Frame(leftMargin, bottomMargin, width-leftMargin-rightMargin, height-topMargin-bottomMargin, id='later')
    # Fungsi kop surat halaman pertama
    def draw_kop(canvas, doc):
        y = height - 60
        y_after = draw_kop_surat(canvas, y)
        # Beri jarak turun sedikit dari kop
        y_after -= 10
        # Jenis laporan custom (center)
        tanggal = datetime.now().strftime('%d/%m/%Y')
        canvas.setFont("Helvetica-Bold", 15)
        canvas.setFillColor(colors.black)
        title = "Laporan Custom (IN/OUT)"
        title_w = canvas.stringWidth(title, "Helvetica-Bold", 15)
        canvas.drawString((width - title_w) / 2, y_after, title)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(40, y_after-24, f"Tanggal: {tanggal}")
    # Fungsi halaman berikutnya (kosong, hanya margin atas)
    def draw_blank(canvas, doc):
        pass
    # Siapkan template
    doc = SimpleDocTemplate(filename, pagesize=landscape(A4), leftMargin=leftMargin, rightMargin=rightMargin, topMargin=topMargin, bottomMargin=bottomMargin)
    doc.addPageTemplates([
        PageTemplate(id='First', frames=frame_first, onPage=draw_kop),
        PageTemplate(id='Later', frames=frame_later, onPage=draw_blank)
    ])
    elements = []
    # Spacer untuk kop surat
    elements.append(Spacer(1, 28))
    # Remarks (hanya di halaman pertama)
    remarks_idx = None
    nama_idx = None
    qty_idx = None
    if 'Remarks' in headers:
        remarks_idx = headers.index('Remarks')
    if 'Nama Barang' in headers:
        nama_idx = headers.index('Nama Barang')
    if 'Qty' in headers:
        qty_idx = headers.index('Qty')
    remarks_lines = []
    if remarks_idx is not None and nama_idx is not None and qty_idx is not None:
        for row in data:
            remarks = row[remarks_idx]
            if remarks:
                nama = row[nama_idx]
                qty = row[qty_idx]
                remarks_lines.append(f"- {nama} (Qty: {qty}) : {remarks}")
    if remarks_lines:
        elements.append(Paragraph('<b>Remarks:</b>', styles['Normal']))
        for line in remarks_lines:
            if len(line) > 120:
                line = line[:117] + '...'
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 12))
    # Data tabel
    table_data = [headers]
    for row in data:
        row_out = []
        for i, val in enumerate(row):
            if headers[i] in ['Nama Barang', 'Remarks']:
                row_out.append(Paragraph(str(val), para_style))
            else:
                row_out.append(str(val))
        table_data.append(row_out)
    # Lebar kolom proporsional untuk landscape
    n = len(headers)
    # Contoh: [No, Jenis, Part Number, Nama Barang, Kategori, Qty, User, Penerima, Menyetujui, Remarks]
    # Total width: width-leftMargin-rightMargin
    # Atur lebar kolom agar proporsional
    col_widths = []
    for h in headers:
        if h == 'No':
            col_widths.append(30)
        elif h == 'Jenis':
            col_widths.append(45)
        elif h == 'Part Number':
            col_widths.append(90)
        elif h == 'Nama Barang':
            col_widths.append(180)
        elif h == 'Kategori':
            col_widths.append(70)
        elif h == 'Qty':
            col_widths.append(35)
        elif h == 'User':
            col_widths.append(70)
        elif h == 'Penerima':
            col_widths.append(70)
        elif h == 'Menyetujui':
            col_widths.append(70)
        elif h == 'Remarks':
            col_widths.append(150)
        else:
            col_widths.append(60)
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF2800')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'CENTER'),
        ('ALIGN', (3,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ROWHEIGHT', (0,1), (-1,-1), 30),
    ]))
    elements.append(table)
    doc.build(elements) 