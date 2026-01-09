import os
import shutil
import time
import re
import yaml # Pode ser necessário instalar: pip install pyyaml
from pathlib import Path

try:
    from google.genai import Client
except ImportError:
    raise ImportError("Instale: pip install google-genai")

client = Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = "gemini-2.5-flash"

def translate_text(text, is_title=False):
    """Função auxiliar para traduzir pequenos trechos ou o corpo do texto."""
    if not text or str(text).isdigit():
        return text
        
    context = "como um título de página de documentação" if is_title else ""
    prompt = f"Traduza o seguinte texto do português para o inglês {context}. Mantenha a formatação Markdown se houver:\n\n{text}"
    
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"   ❌ Erro na tradução: {e}")
        return text

def process_jekyll_content(content):
    """Separa, traduz seletivamente o YAML e traduz o corpo."""
    front_matter_dict = {}
    body = content
    has_front_matter = False

    # 1. Extrair Front Matter
    if content.startswith("---"):
        parts = re.split(r'---', content, maxsplit=2)
        if len(parts) >= 3:
            try:
                front_matter_dict = yaml.safe_load(parts[1])
                body = parts[2]
                has_front_matter = True
            except:
                pass

    # 2. Traduzir campos específicos do YAML (Title e Parent)
    if has_front_matter:
        fields_to_translate = ['title', 'parent', 'description']
        for field in fields_to_translate:
            if field in front_matter_dict and front_matter_dict[field]:
                print(f"   🏷️  Traduzindo campo YAML: {field}")
                front_matter_dict[field] = translate_text(front_matter_dict[field], is_title=True)

    # 3. Traduzir o corpo do Markdown
    print("   📝 Traduzindo corpo do arquivo...")
    translated_body = translate_text(body)

    # 4. Reconstruir o arquivo
    if has_front_matter:
        # Re-gera o YAML preservando a estrutura
        new_yaml = yaml.dump(front_matter_dict, allow_unicode=True, sort_keys=False)
        return f"---\n{new_yaml}---\n{translated_body}"
    
    return translated_body

def main():
    base_dir = Path(__file__).parent.absolute()
    print(f"--- Sincronização Just the Docs ({MODEL_ID}) ---")
    
    source_files = list((base_dir / "pt-br").rglob("*.md"))
    
    for p in source_files:
        if "images" in p.parts: continue
        
        relative_path = p.relative_to(base_dir / "pt-br")
        target_path = base_dir / "en" / relative_path
        
        if not target_path.exists() or p.stat().st_mtime > target_path.stat().st_mtime:
            print(f"📄 Processando: {relative_path}")
            original_content = p.read_text(encoding='utf-8')
            
            final_content = process_jekyll_content(original_content)
            
            if final_content:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(final_content, encoding='utf-8')
                time.sleep(10) # Pausa preventiva para RPM

    # Sincronização de imagens (mantida igual)
    source_images = base_dir / "pt-br" / "images"
    if source_images.exists():
        for img in source_images.rglob("*"):
            if img.suffix.lower() in ('.png', '.jpg', '.jpeg', '.svg'):
                dest = base_dir / "en" / "images" / img.name
                if not dest.exists() or img.stat().st_mtime > dest.stat().st_mtime:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img, dest)

if __name__ == "__main__":
    main()
