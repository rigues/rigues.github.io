import os
import shutil
import time
from pathlib import Path

# Gerenciamento de importação para a SDK de 2026
try:
    from google.genai import Client
except ImportError:
    try:
        from genai import Client
    except ImportError:
        raise ImportError("Erro: Biblioteca 'google-genai' não encontrada.")

# Configuração do Cliente
client = Client(api_key=os.environ.get("GEMINI_API_KEY"))

# ALTERAÇÃO: Modelo Flash 2.0 costuma ter cotas diárias mais flexíveis que o Lite
MODEL_ID = "gemini-2.0-flash"

def translate_markdown(content):
    """Envia o conteúdo para o Gemini e retorna a tradução com retry robusto."""
    prompt = f"Traduza o seguinte conteúdo Markdown do português para o inglês. Mantenha toda a formatação, links e blocos de código intactos:\n\n{content}"
    
    max_retries = 5
    base_wait = 30 # Aumentamos o tempo base para garantir a liberação da cota

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=MODEL_ID, contents=prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait_time = base_wait * (attempt + 1)
                print(f"   ⏳ Cota diária/minuto atingida. Aguardando {wait_time}s (Tentativa {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                print(f"   ❌ Erro na API Gemini: {e}")
                return None
    return None

def main():
    base_dir = Path(__file__).parent.absolute()
    print(f"--- Sincronização Ativa (Modelo: {MODEL_ID}) ---")
    
    arquivos_criados = []
    arquivos_atualizados = []
    imagens_sincronizadas = []

    # 1. Documentos
    source_files = list((base_dir / "pt-br").rglob("*.md"))
    for p in source_files:
        if "images" in p.parts: continue
        
        try:
            relative_parts = p.parts[p.parts.index("pt-br"):]
            clean_path_obj = Path(*relative_parts)
            target_rel_path = str(clean_path_obj).replace("pt-br", "en", 1)
            target_path = base_dir / target_rel_path
            
            should_translate = False
            if not target_path.exists() or p.stat().st_mtime > target_path.stat().st_mtime:
                should_translate = True

            if should_translate:
                print(f"📄 Processando: {clean_path_obj}...")
                original_text = p.read_text(encoding='utf-8')
                translated_text = translate_markdown(original_text)
                
                if translated_text:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.write_text(translated_text, encoding='utf-8')
                    if not target_path.exists(): arquivos_criados.append(target_rel_path)
                    else: arquivos_atualizados.append(target_rel_path)
                    
                    # Pausa de 10s entre arquivos para evitar atingir o RPM (limite por minuto)
                    time.sleep(10)
                
        except Exception as e:
            print(f"   ❌ Erro em {p.name}: {e}")

    # 2. Imagens
    img_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')
    source_images_dir = base_dir / "pt-br" / "images"
    if source_images_dir.exists():
        for img_p in source_images_dir.rglob("*"):
            if img_p.suffix.lower() in img_extensions:
                relative_img_path = img_p.relative_to(base_dir / "pt-br")
                target_img_path = base_dir / "en" / relative_img_path
                if not target_img_path.exists() or img_p.stat().st_mtime > target_img_path.stat().st_mtime:
                    target_img_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img_p, target_img_path)
                    imagens_sincronizadas.append(str(relative_img_path))

    print("\n--- RESUMO FINAL ---")
    if not (arquivos_criados or arquivos_atualizados or imagens_sincronizadas):
        print("✅ Nada para traduzir.")
    else:
        if arquivos_criados: print(f"🆕 Criados: {len(arquivos_criados)}")
        if arquivos_atualizados: print(f"🔄 Atualizados: {len(arquivos_atualizados)}")
        if imagens_sincronizadas: print(f"🖼️ Imagens: {len(imagens_sincronizadas)}")
    print("--------------------")

if __name__ == "__main__":
    main()
