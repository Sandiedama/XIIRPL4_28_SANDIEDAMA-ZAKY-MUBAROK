# Kategori peruntukan utama untuk transaksi
CATEGORIES = [
    '',
    'project',
    'retail',
    'stock',
    'warranty',
]

COMMON_CATEGORIES = CATEGORIES.copy()

def get_categories():
    return CATEGORIES

def get_common_categories():
    return COMMON_CATEGORIES

def get_category_groups():
    return {'Peruntukan': CATEGORIES} 