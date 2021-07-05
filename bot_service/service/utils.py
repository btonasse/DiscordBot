import unicodedata

def str_as_ascii(orig_str):
    try:
        return ''.join(c for c in unicodedata.normalize('NFD', orig_str) if unicodedata.category(c) != 'Mn')
    except:
        return orig_str