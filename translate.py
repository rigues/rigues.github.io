import os
import shutil
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
MODEL_ID = "gemini-flash-lite-latest"

def translate_markdown(content):
    """Envia o conteúdo para o Gemini e retorna a tradução."""
    prompt = f"Traduza o seguinte conteúdo Markdown do português para o inglês. Mantenha toda a formatação, links e blocos de código intactos:\n\n{content}"
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        return response.text
    except Exception as e:
        print(f"   ❌ Erro na API Gemini: {e}")
        return None

def main():
    base_dir = Path(__file__).parent.absolute()
    print(f"--- Iniciando Sincronização (Modelo: {MODEL_ID}) ---")
    
    # Listas para o resumo final
    arquivos_criados = []
    arquivos_atualizados = []
    imagens_sincronizadas = []

    # --- PARTE 1: TRADUÇÃO DE DOCUMENTOS (.md) ---
    source_files = list((base_dir / "pt-br").rglob("*.md"))
    
    for p in source_files:
        if "images" in p.parts: continue # Ignora ficheiros .md que possam estar na pasta de imagens
        
        try:
            relative_parts = p.parts[p.parts.index("pt-br"):]
            clean_path_obj = Path(*relative_parts)
            target_rel_path = str(clean_path_obj).replace("pt-br", "en", 1)
            target_path = base_dir / target_rel_path
            
            should_translate = False
            is_new = not target_path.exists()
            
            if is_new:
                should_translate = True
            else:
                if p.stat().st_mtime > target_path.stat().st_mtime:
                    should_translate = True

            if should_translate:
                print(f"📄 Traduzindo: {clean_path_obj}...")
                original_text = p.read_text(encoding='utf-8')
                translated_text = translate_markdown(original_text)
                
                if translated_text:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.write_text(translated_text, encoding='utf-8')
                    if is_new: arquivos_criados.append(target_rel_path)
                    else: arquivos_atualizados.append(target_rel_path)
                
        except Exception as e:
            print(f"   ❌ Erro ao processar documento {p.name}: {e}")

    # --- PARTE 2: SINCRONIZAÇÃO DE IMAGENS ---
    # Define as extensões de imagem comuns para procurar
    img_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')
    source_images_dir = base_dir / "pt-br" / "images"
    
    if source_images_dir.exists():
        print(f"🖼️ Verificando imagens em {source_images_dir}...")
        for img_p in source_images_dir.rglob("*"):
            if img_p.suffix.lower() in img_extensions:
                # Calcula caminho de destino (pt-br/images/... -> en/images/...)
                relative_img_path = img_p.relative_to(base_dir / "pt-br")
                target_img_path = base_dir / "en" / relative_img_path
                
                should_copy = False
                if not target_img_path.exists():
                    should_copy = True
                elif img_p.stat().st_mtime > target_img_path.stat().st_mtime:
                    should_copy = True
                
                if should_copy:
                    target_img_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img_p, target_img_path) # copy2 preserva metadados/datas
                    imagens_sincronizadas.append(str(relative_img_path))
                    print(f"   📸 Imagem sincronizada: {relative_img_path}")

    # --- RESUMO FINAL ---
    print("\n--- RESUMO DA EXECUÇÃO ---")
    if not arquivos_criados and not arquivos_atualizados and not imagens_sincronizadas:
        print("✅ Tudo atualizado. Nenhuma ação necessária.")
    else:
        if arquivos_criados:
            print(f"🆕 Documentos criados ({len(arquivos_criados)}):")
            for f in arquivos_criados: print(f"   - {f}")
        
        if arquivos_atualizados:
            print(f"🔄 Documentos atualizados ({len(arquivos_atualizados)}):")
            for f in arquivos_atualizados: print(f"   - {f}")
            
        if imagens_sincronizadas:
            print(f"🖼️ Imagens sincronizadas ({len(imagens_sincronizadas)}):")
            for i in imagens_sincronizadas: print(f"   - {i}")
    print("--------------------------")

if __name__ == "__main__":
    main()
