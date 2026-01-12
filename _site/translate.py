import os
import shutil
import time
import re
import yaml
import json
from pathlib import Path

# --- CONFIGURAÇÃO ---
try:
    from google.genai import Client
except ImportError:
    raise ImportError("Instale: pip install google-genai pyyaml")

client = Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = "gemini-2.5-flash"
SIMULACAO = False
# --------------------

def clean_ai_output(text):
    """Limpa blocos de código e caracteres de controle que quebram o JSON."""
    text = re.sub(r'^```[a-z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    # Remove caracteres de controle (0-31) exceto quebra de linha e tabulação
    text = "".join(ch for ch in text if ord(ch) >= 32 or ch in "\n\r\t")
    return text.strip()

def translate_payload(front_matter_dict, body_content):
    """Traduz metadados e corpo garantindo integridade do JSON."""
    meta_to_translate = {k: v for k, v in front_matter_dict.items() if k in ['title', 'parent', 'description']}
    
    # O prompt agora pede explicitamente para escapar aspas internas
    prompt = f"""
    Traduza este conteúdo Markdown para o inglês.
    Retorne APENAS um objeto JSON.
    IMPORTANTE: Se o título contiver aspas, use barra invertida para escapar.
    {{
      "metadata": {json.dumps(meta_to_translate, ensure_ascii=False)},
      "body": "corpo traduzido"
    }}
    ORIGINAL:
    METADADOS: {json.dumps(meta_to_translate, ensure_ascii=False)}
    CORPO: {body_content}
    """

    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        raw_text = clean_ai_output(response.text)
        
        # Tenta localizar o JSON ignorando lixo antes ou depois
        start_idx = raw_text.find('{')
        end_idx = raw_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_str = raw_text[start_idx:end_idx+1]
            data = json.loads(json_str)
            return data
        return None
    except Exception as e:
        print(f"   ❌ Erro na API/JSON: {e}")
        return None

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

            data = translate_payload(front_matter_dict, body)
            
            if data and "metadata" in data and "body" in data:
                for k, v in data['metadata'].items():
                    front_matter_dict[k] = v
                
                # O yaml.dump com default_flow_style=False ajuda a formatar como o Jekyll gosta
                new_yaml = yaml.dump(front_matter_dict, allow_unicode=True, sort_keys=False, default_flow_style=False)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write("---\n")
                    f.write(new_yaml)
                    f.write("---\n")
                    f.write(data['body'])
                
                print(f"   ✅ Sincronizado com sucesso.")
                time.sleep(30) # Respeito à cota diária

if __name__ == "__main__":
    main()
