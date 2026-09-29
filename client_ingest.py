import os
import argparse
import requests
from pathlib import Path
import tempfile

try:
    from docx2pdf import convert
except ImportError:
    convert = None
    print("Le module docx2pdf n'est pas installé. (pip install docx2pdf)")
    print("Les fichiers .docx ne pourront pas être convertis sans ce module.\n")

def upload_file(file_path: str, url: str, original_name: str = None):
    """Envoie un fichier PDF à l'endpoint spécifié."""
    filename = original_name if original_name else os.path.basename(file_path)
    print(f"Envoi de {filename} vers {url}...")
    try:
        with open(file_path, 'rb') as f:
            # Le backend attend un fichier avec la clé 'file'
            files = {'file': (filename, f, 'application/pdf')}
            response = requests.post(url, files=files)
            
        if response.status_code in [200, 201]:
            print(f"  -> Succès ! Réponse: {response.json()}")
        else:
            print(f"  -> Erreur HTTP {response.status_code} : {response.text}")
    except Exception as e:
        print(f"  -> Erreur lors de l'envoi de {filename}: {e}")

def process_directory(directory: str, url: str):
    """Parcourt le dossier et traite les PDF et DOCX."""
    dir_path = Path(directory)
    if not dir_path.is_dir():
        print(f"Erreur: '{directory}' n'est pas un dossier valide.")
        return

    print(f"Analyse du dossier : {dir_path.absolute()}")
    
    for file_path in dir_path.rglob('*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            
            if ext == '.pdf':
                upload_file(str(file_path), url)
                
            elif ext == '.docx':
                if convert is None:
                    print(f"Ignoré (docx2pdf manquant) : {file_path}")
                    continue
                
                print(f"Conversion de {file_path.name} en PDF...")
                try:
                    # On crée un fichier temporaire pour le PDF généré
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                        temp_pdf_path = tmp_pdf.name
                    
                    # Conversion du docx vers le fichier pdf temporaire
                    convert(str(file_path), temp_pdf_path)
                    
                    # On upload le fichier converti en lui donnant le nom d'origine mais en .pdf
                    target_filename = file_path.with_suffix('.pdf').name
                    upload_file(temp_pdf_path, url, original_name=target_filename)
                    
                    # Nettoyage
                    os.remove(temp_pdf_path)
                except Exception as e:
                    print(f"  -> Erreur lors du traitement de {file_path.name} : {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client d'ingestion de documents (PDF/DOCX) vers l'API vector store.")
    parser.add_argument("-d", "--dir", type=str, required=True, help="Chemin vers le dossier contenant les fichiers (PDF/DOCX).")
    parser.add_argument("-u", "--url", type=str, default="https://precise-rag.onrender.com/add", help="URL de l'endpoint d'ajout (par défaut: http://localhost:8000/add)")
    
    args = parser.parse_args()
    
    print("=== Démarrage de l'ingestion ===")
    print(f"Dossier cible : {args.dir}")
    print(f"Endpoint URL  : {args.url}\n")
    
    process_directory(args.dir, args.url)
    
    print("\n=== Ingestion terminée ===")
