import os
import shutil
import time
import re
import yaml
from pathlib import Path

try:
    from google.genai import Client
except ImportError:
    raise ImportError("Instale: pip install google-genai pyyaml")

client = Client(api_key=os.environ.get("GEMINI_API_KEY"))
# Usaremos o Flash 2.5 que é mais inteligente para lidar com instruções complexas
MODEL_ID = "gemini-2.5-flash"

def translate_payload(front_matter_dict, body_content):
    """Envia tudo em uma única requisição para economizar cota."""
    
    # Prepara os campos do YAML que precisam de tradução
    fields_to_translate = {k: v for k, v in front_matter_dict.items() if k in ['title', 'parent', 'description']}
    
    prompt = f"""
    Atue como um tradutor técnico. Traduza o conteúdo abaixo do português para o inglês.
    
    REGRAS:
    1. Mantenha a formatação Markdown, links e blocos de código intactos.
    2. Traduza os valores destes campos de metadados: {fields_to_translate}
    3. Traduza o corpo do texto que vem após os metadados.
    4. Responda estritamente no formato:
       METADADOS: [JSON com os campos traduzidos]
       CORPO: [Texto traduzido]

    CONTEÚDO PARA TRADUZIR:
    {body_content}
    """

    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        res_text = response.text
        
        # Extração simples usando regex para separar o que a IA devolveu
        meta_match = re.search(r"METADADOS:\s*(\{.*?\})", res_text, re.DOTALL)
        body_match = re.search(r"CORPO:\s*(.*)", res_text, re.DOTALL)
        
        if meta_match and body_match:
            import json
            translated_meta = json.loads(meta_match.group(1))
            translated_body = body_match.group(1).strip()
            return translated_meta, translated_body
        else:
            # Fallback caso a IA não siga o formato (retorna o original para não quebrar)
            print("   ⚠️ IA não seguiu o formato estrito. Tentando tradução simples...")
            return fields_to_translate, res_text
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
        return None, None

def main():
    base_dir = Path(__file__).parent.absolute()
    source_files = list((base_dir / "pt-br").rglob("*.md"))
    
    for p in source_files:
        if "images" in p.parts: continue
        
        target_path = base_dir / "en" / p.relative_to(base_dir / "pt-br")
        
        if not target_path.exists() or p.stat().st_mtime > target_path.stat().st_mtime:
            print(f"📄 Processando: {p.name} (1 requisição)")
            content = p.read_text(encoding='utf-8')
            
            # Extração do YAML original
            front_matter_dict = {}
            body = content
            if content.startswith("---"):
                parts = re.split(r'---', content, maxsplit=2)
                if len(parts) >= 3:
                    front_matter_dict = yaml.safe_load(parts[1])
                    body = parts[2]

            # TRADUÇÃO ÚNICA
            t_meta, t_body = translate_payload(front_matter_dict, body)
            
            if t_body:
                # Atualiza o dicionário original com as traduções recebidas
                for k, v in t_meta.items():
                    front_matter_dict[k] = v
                
                new_yaml = yaml.dump(front_matter_dict, allow_unicode=True, sort_keys=False)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(f"---\n{new_yaml}---\n{t_body}", encoding='utf-8')
                
                # Aguarda 30s para garantir que não estoura o limite de requisições por minuto
                print("   ⏳ Aguardando 30s...")
                time.sleep(30)

if __name__ == "__main__":
    main()
