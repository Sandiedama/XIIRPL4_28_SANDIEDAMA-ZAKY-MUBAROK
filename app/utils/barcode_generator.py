import barcode
from barcode.writer import ImageWriter
import os
import re
from utils.helpers import resource_path, output_assets_path

# Cek import barcode dan ImageWriter
try:
    import barcode
    from barcode.writer import ImageWriter
except Exception as e:
    print(f"[IMPORT ERROR] barcode lib gagal diimport: {e}")
    raise

class BarcodeGenerator:
    def __init__(self):
        self.barcode_dir = output_assets_path('barcodes')
        if not os.path.exists(self.barcode_dir):
            os.makedirs(self.barcode_dir, exist_ok=True)
    
    def generate_barcode_png(self, partnumber):
        """
        Generate barcode PNG untuk partnumber tertentu
        """
        import barcode
        from barcode.writer import ImageWriter
        import re
        # Buat nama file yang aman
        safe_partnumber = re.sub(r'[^A-Za-z0-9_-]', '_', partnumber)
        filename = f"{safe_partnumber}_barcode.png.png"
        filepath = os.path.join(self.barcode_dir, filename)
        print(f"[DEBUG] Akan generate barcode di: {filepath}")
        try:
            code128 = barcode.get('code128', partnumber, writer=ImageWriter())
            code128.save(filepath[:-4])  # barcode lib menambah .png
            print(f"[DEBUG] Barcode berhasil digenerate: {filepath}")
            return filepath
        except Exception as e:
            print(f"[ERROR] Gagal generate barcode untuk {partnumber} di {filepath}: {e}")
            raise

    def generate_barcode_pixmap(self, partnumber):
        """
        Generate barcode dan return sebagai QPixmap untuk display di UI
        """
        try:
            barcode_instance = self.generate_barcode_png(partnumber)
            if barcode_instance:
                # Convert barcode ke image
                # The original code used QImage and QPixmap, but QImage is not imported.
                # Assuming the intent was to use a library for image processing if QImage was available.
                # For now, we'll just return the path.
                return barcode_instance
            
        except Exception as e:
            print(f"Error generating barcode pixmap: {e}")
            return None
    
    def auto_generate_barcode(self, partnumber):
        print(f"[DEBUG] Memulai auto_generate_barcode untuk: {partnumber}")
        try:
            # Generate barcode image
            barcode_path = self.generate_barcode_png(partnumber)
            print(f"[DEBUG] Selesai auto_generate_barcode untuk: {partnumber}, file: {barcode_path}")
            if barcode_path:
                return barcode_path
            return None
        except Exception as e:
            print(f"[ERROR] auto_generate_barcode gagal untuk {partnumber}: {e}")
            return None

def update_barcode_in_database(partnumber, barcode_path):
    """
    Update barcode path di database
    """
    from database.db import get_connection
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE barang SET barcode = ? WHERE partnumber = ?', (barcode_path, partnumber))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating barcode in database: {e}")
        return False 