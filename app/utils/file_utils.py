# app/utils/file_utils.py

def get_file_size_str(size_bytes):
    """
    Bayt cinsinden dosya boyutunu insan tarafından okunabilir bir biçime dönüştürür
    
    Args:
        size_bytes: Bayt cinsinden dosya boyutu
        
    Returns:
        Biçimlendirilmiş dosya boyutu dizesi (örn. "2.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    else:
        return f"{size_bytes/(1024*1024):.2f} MB"
