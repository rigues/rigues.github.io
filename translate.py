import os
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
    
    source_files = list((base_dir / "pt-br").rglob("*.md"))
    
    if not source_files:
        print("ℹ️ Nenhuma tradução realizada (pasta pt-br/ vazia).")
        return

    # Listas para o resumo final
    arquivos_criados = []
    arquivos_atualizados = []

    for p in source_files:
        try:
            relative_parts = p.parts[p.parts.index("pt-br"):]
            clean_path_obj = Path(*relative_parts)
            
            target_rel_path = str(clean_path_obj).replace("pt-br", "en", 1)
            target_path = base_dir / target_rel_path
            
            should_translate = False
            is_new = False
            
            # Regra 1: Se o arquivo NÃO EXISTE em inglês
            if not target_path.exists():
                should_translate = True
                is_new = True
            else:
                # Regra 2: Se existe, compara a data de modificação
                pt_mtime = p.stat().st_mtime
                en_mtime = target_path.stat().st_mtime
                
                if pt_mtime > en_mtime:
                    should_translate = True

            if should_translate:
                print(f"📄 Processando: {clean_path_obj}...")
                original_text = p.read_text(encoding='utf-8')
                translated_text = translate_markdown(original_text)
                
                if translated_text:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.write_text(translated_text, encoding='utf-8')
                    
                    if is_new:
                        arquivos_criados.append(target_rel_path)
                    else:
                        arquivos_atualizados.append(target_rel_path)
                
        except Exception as e:
            print(f"   ❌ Erro ao processar {p.name}: {e}")

    # --- Resumo Final ---
    print("\n--- RESUMO DA EXECUÇÃO ---")
    if not arquivos_criados and not arquivos_atualizados:
        print("✅ Nenhuma tradução realizada (tudo atualizado).")
    else:
        if arquivos_criados:
            print(f"🆕 Arquivos criados ({len(arquivos_criados)}):")
            for f in arquivos_criados: print(f"   - {f}")
        
        if arquivos_atualizados:
            print(f"🔄 Arquivos atualizados ({len(arquivos_atualizados)}):")
            for f in arquivos_atualizados: print(f"   - {f}")
    print("--------------------------")

if __name__ == "__main__":
    main()
