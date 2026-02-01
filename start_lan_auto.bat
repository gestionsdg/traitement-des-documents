@echo off
cd /d E:\traitement_des_documents
env\Scripts\python.exe -m waitress --host=0.0.0.0 --port=8000 traitement_des_documents.wsgi:application
