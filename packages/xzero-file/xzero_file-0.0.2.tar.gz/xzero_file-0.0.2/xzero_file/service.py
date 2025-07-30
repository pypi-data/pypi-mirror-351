import os

def is_safe_path(base, path):
    safe_path = os.path.abspath(os.path.join(base, path))
    return base == os.path.commonpath((base, safe_path))
