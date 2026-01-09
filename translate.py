# Versão experimental do script de tradução, levando em consideração um tema do Jekyll (Minima) e usando o modelo gemma-3-27b, com um limite de uso mais generoso. Versão original no arquivo translate.bak

import os
import shutil
import time
import re
from pathlib import Path

try:
    from google.genai import Client
except ImportError:
    raise ImportError("Instale: pip install google-genai")

client = Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = "gemma-3-27b" # Usando sua cota de 14.4K RPD

def translate_markdown(content):
    # Separa o Front Matter (YAML) do corpo do Markdown
    front_matter = ""
    body = content
    
    if content.startswith("---"):
        parts = re.split(r'---', content, maxsplit=2)
        if len(parts) >= 3:
            front_matter = f"---{parts[1]}---\n"
            body = parts[2]

    prompt = f"Traduza o seguinte texto Markdown para o inglês, mantendo a formatação e links intactos:\n\n{body}"
    
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        # Retorna o Front Matter original (sem traduzir) + o corpo traduzido
        return front_matter + response.text
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def main():
    base_dir = Path(__file__).parent.absolute()
    source_files = list((base_dir / "pt-br").rglob("*.md"))
    
    for p in source_files:
        if "images" in p.parts: continue
        target_path = base_dir / str(p.relative_to(base_dir / "pt-br")).replace("pt-br", "en", 1)
        
        if not target_path.exists() or p.stat().st_mtime > target_path.stat().st_mtime:
            print(f"📄 Traduzindo: {p.name}")
            translated = translate_markdown(p.read_text(encoding='utf-8'))
            if translated:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(translated, encoding='utf-8')
                time.sleep(2) # Pausa curta para o Gemma

    # Sincroniza Imagens
    img_dir = base_dir / "pt-br" / "images"
    if img_dir.exists():
        for img in img_dir.rglob("*"):
            if img.suffix.lower() in ('.png', '.jpg', '.jpeg', '.svg'):
                dest = base_dir / "en" / "images" / img.name
                if not dest.exists() or img.stat().st_mtime > dest.stat().st_mtime:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img, dest)

if __name__ == "__main__":
    main()
