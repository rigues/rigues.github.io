import os
import shutil
import time
import re
from pathlib import Path

# Gerenciamento de importação
try:
    from google.genai import Client
except ImportError:
    raise ImportError("Instale a biblioteca: pip install google-genai")

# Configuração do Cliente
client = Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Alterado para o modelo Flash 2.0 (mais estável para v1)
MODEL_ID = "gemini-2.0-flash"

def translate_markdown(content):
    """Separa o Front Matter, traduz o corpo e remonta o arquivo."""
    front_matter = ""
    body = content
    
    # Lógica para proteger o Front Matter do Jekyll (entre ---)
    if content.startswith("---"):
        parts = re.split(r'---', content, maxsplit=2)
        if len(parts) >= 3:
            front_matter = f"---{parts[1]}---\n"
            body = parts[2]

    prompt = f"""
    Traduza o seguinte conteúdo Markdown do português para o inglês.
    Instruções CRÍTICAS:
    1. Mantenha todos os links, tags e blocos de código intactos.
    2. Não traduza termos técnicos entre crases (`term`).
    3. Retorne apenas a tradução do corpo.
    
    Conteúdo:
    {body}
    """
    
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        # Remonta o arquivo: Front Matter Original + Texto Traduzido
        return front_matter + response.text
    except Exception as e:
        print(f"   ❌ Erro na API Gemini: {e}")
        return None

def main():
    base_dir = Path(__file__).parent.absolute()
    print(f"--- Sincronização Jekyll (Modelo: {MODEL_ID}) ---")
    
    # 1. Processamento de Documentos
    source_files = list((base_dir / "pt-br").rglob("*.md"))
    
    for p in source_files:
        if "images" in p.parts: continue
        
        # Define caminho de destino preservando subpastas
        relative_path = p.relative_to(base_dir / "pt-br")
        target_path = base_dir / "en" / relative_path
        
        should_translate = False
        if not target_path.exists() or p.stat().st_mtime > target_path.stat().st_mtime:
            should_translate = True

        if should_translate:
            print(f"📄 Processando: {relative_path}")
            original_text = p.read_text(encoding='utf-8')
            translated_text = translate_markdown(original_text)
            
            if translated_text:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(translated_text, encoding='utf-8')
                # Pausa para respeitar o limite de Requisições por Minuto (RPM)
                time.sleep(5) 

    # 2. Sincronização de Imagens
    source_images = base_dir / "pt-br" / "images"
    if source_images.exists():
        print("🖼️ Sincronizando imagens...")
        for img in source_images.rglob("*"):
            if img.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'):
                rel_img = img.relative_to(base_dir / "pt-br")
                dest_img = base_dir / "en" / rel_img
                
                if not dest_img.exists() or img.stat().st_mtime > dest_img.stat().st_mtime:
                    dest_img.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img, dest_img)
                    print(f"   📸 Imagem: {rel_img}")

if __name__ == "__main__":
    main()
    print("--- Processo Finalizado ---")
