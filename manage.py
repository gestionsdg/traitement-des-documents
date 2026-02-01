#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# --- WeasyPrint on Windows: ensure MSYS2 UCRT64 DLLs are discoverable ---
if os.name == "nt":
    # You can override this with the env var MSYS2_UCRT64_BIN if needed
    DLL_DIR = os.environ.get("MSYS2_UCRT64_BIN", r"C:\msys64\ucrt64\bin")
    try:
        if hasattr(os, "add_dll_directory") and os.path.isdir(DLL_DIR):
            os.add_dll_directory(DLL_DIR)
    except Exception:
        # Stay silent if the directory doesn't exist or the API isn't available
        pass
# ------------------------------------------------------------------------

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traitement_des_documents.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
