import os
import shutil
import time
import re
import yaml
import json
from pathlib import Path

try:
    from google.genai import Client
except ImportError:
    raise ImportError("Instale: pip install google-genai pyyaml")

client = Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = "gemini-2.5-flash"

def clean_json_response(text):
    """Extrai apenas o conteúdo entre as chaves { } caso a IA mande texto extra."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text)
    except:
        return None

def translate_payload(front_matter_dict, body_content):
    """Traduz tudo em uma única chamada com restrições rígidas de formato."""
    
    # Prepara apenas o que precisa de tradução para o prompt
    meta_to_translate = {k: v for k, v in front_matter_dict.items() if k in ['title', 'parent', 'description']}
    
    prompt = f"""
    Traduza o conteúdo Markdown abaixo do português para o inglês.
    
    REGRAS ESTRITAS:
    1. Retorne a resposta EXATAMENTE no formato JSON abaixo, sem qualquer texto adicional antes ou depois.
    2. Não ofereça alternativas. Escolha a melhor tradução técnica e use-a.
    3. Mantenha toda a formatação Markdown, links e códigos do corpo intactos.
    4. O campo "body" deve conter o texto completo traduzido.
    5. O campo "metadata" deve conter um objeto com as chaves traduzidas.

    FORMATO DA RESPOSTA:
    {{
      "metadata": {json.dumps(meta_to_translate)},
      "body": "corpo do texto traduzido aqui"
    }}

    CONTEÚDO ORIGINAL:
    METADADOS: {json.dumps(meta_to_translate)}
    CORPO: {body_content}
    """

    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        res_text = response.text
        
        # Tenta decodificar a resposta como JSON puro
        data = clean_json_response(res_text)
        
        if data and "metadata" in data and "body" in data:
            return data["metadata"], data["body"]
        else:
            print("   ⚠️ Erro na estrutura da resposta. Retornando original.")
            return meta_to_translate, body_content
            
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
            print(f"📄 Processando: {p.name}")
            content = p.read_text(encoding='utf-8')
            
            front_matter_dict = {}
            body = content
            if content.startswith("---"):
                parts = re.split(r'---', content, maxsplit=2)
                if len(parts) >= 3:
                    try:
                        front_matter_dict = yaml.safe_load(parts[1])
                        body = parts[2]
                    except: pass

            t_meta, t_body = translate_payload(front_matter_dict, body)
            
            if t_body:
                # Atualiza metadados originais com os traduzidos
                for k, v in t_meta.items():
                    front_matter_dict[k] = v
                
                new_yaml = yaml.dump(front_matter_dict, allow_unicode=True, sort_keys=False)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(f"---\n{new_yaml}---\n{t_body}", encoding='utf-8')
                
                print("   ✅ Sucesso. Aguardando 30s de cota...")
                time.sleep(30)

if __name__ == "__main__":
    main()
