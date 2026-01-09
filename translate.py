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
MODEL_ID = "gemini-2.0-flash"
SIMULACAO = False # Coloque False para corrigir seus arquivos agora
# --------------------

def clean_ai_output(text):
    """Remove marcações de blocos de código (```json, ```markdown) que a IA insere."""
    # Remove as crases e o nome da linguagem no início e fim
    text = re.sub(r'^```[a-z]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    return text.strip()

def translate_payload(front_matter_dict, body_content):
    """Traduz metadados e corpo em uma única chamada estruturada."""
    meta_to_translate = {k: v for k, v in front_matter_dict.items() if k in ['title', 'parent', 'description']}
    
    prompt = f"""
    Traduza este conteúdo Markdown para o inglês.
    Retorne APENAS um objeto JSON puro. Não use blocos de código (```).
    {{
      "metadata": {json.dumps(meta_to_translate)},
      "body": "corpo traduzido aqui"
    }}
    ORIGINAL:
    METADADOS: {json.dumps(meta_to_translate)}
    CORPO: {body_content}
    """

    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        raw_text = clean_ai_output(response.text)
        
        # Tenta encontrar o JSON dentro da resposta caso ainda haja texto extra
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            # Limpa também o corpo traduzido de possíveis crases indesejadas
            data["body"] = clean_ai_output(data["body"])
            return data
        return None
    except Exception as e:
        print(f"   ❌ Erro na API: {e}")
        return None

def main():
    base_dir = Path(__file__).parent.absolute()
    source_files = list((base_dir / "pt-br").rglob("*.md"))
    
    for p in source_files:
        if "images" in p.parts: continue
        target_path = base_dir / "en" / p.relative_to(base_dir / "pt-br")
        
        # Processa se o arquivo não existe ou o original é mais novo
        if not target_path.exists() or p.stat().st_mtime > target_path.stat().st_mtime:
            print(f"📄 Sincronizando: {p.name}")
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
                if not SIMULACAO:
                    # Mescla metadados traduzidos com os originais (preserva layout, nav_order)
                    for k, v in data['metadata'].items():
                        front_matter_dict[k] = v
                    
                    # Gera o YAML limpo
                    new_yaml = yaml.dump(front_matter_dict, allow_unicode=True, sort_keys=False)
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # GRAVAÇÃO CRÍTICA: Garante que os traços '---' estão sozinhos na linha
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write("---\n")
                        f.write(new_yaml)
                        f.write("---\n")
                        f.write(data['body'])
                    
                    print(f"   ✅ Arquivo corrigido: {target_path}")
                else:
                    print(f"🔍 [SIMULAÇÃO] Tradução de {p.name} ok.")
                
                time.sleep(30) # Respeito à cota RPD

if __name__ == "__main__":
    main()
