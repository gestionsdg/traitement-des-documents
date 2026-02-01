# run_waitress.py (version debug)
import os, traceback, time

print("[run_waitress] Démarrage…")
try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "traitement_des_documents.settings")
    print("[run_waitress] DJANGO_SETTINGS_MODULE =", os.environ["DJANGO_SETTINGS_MODULE"])

    from waitress import serve
    print("[run_waitress] Waitress importé")

    from traitement_des_documents.wsgi import application
    print("[run_waitress] WSGI application importée")

    print("[run_waitress] Lancement sur http://0.0.0.0:8000 …")
    serve(application, host="0.0.0.0", port=8000, threads=8)
except Exception as e:
    print("\n[run_waitress][ERREUR]", e)
    traceback.print_exc()
    print("\nAppuie sur Entrée pour fermer…")
    try:
        input()
    except:
        time.sleep(8)
