"""
WSGI config for traitement_des_documents project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

# --- WeasyPrint on Windows: ensure MSYS2 UCRT64 DLLs are discoverable ---
if os.name == "nt":
    DLL_DIR = os.environ.get("MSYS2_UCRT64_BIN", r"C:\msys64\ucrt64\bin")
    try:
        if hasattr(os, "add_dll_directory") and os.path.isdir(DLL_DIR):
            os.add_dll_directory(DLL_DIR)
    except Exception:
        pass
# ------------------------------------------------------------------------

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traitement_des_documents.settings')

application = get_wsgi_application()
