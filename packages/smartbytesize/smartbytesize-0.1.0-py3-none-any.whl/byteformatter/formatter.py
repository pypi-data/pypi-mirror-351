# byteformatter/formatter.py

def get_size(bytes, suffix="B"):
    """
    Scale bytes to a human-readable format.

    Examples:
        1253656 => '1.20 MB'
        1253656678 => '1.17 GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor
