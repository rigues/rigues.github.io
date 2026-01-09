import os
import google.generativeai as genai
from pathlib import Path

# Configuração da API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-flash-lite-latest')

def translate_markdown(content):
    prompt = f"""
    Traduza o seguinte conteúdo Markdown do português para o inglês. 
    Mantenha toda a formatação, links e blocos de código intactos. 
    Traduza apenas o texto descritivo.
    
    Conteúdo:
    {content}
    """
    response = model.generate_content(prompt)
    return response.text

# Identificar arquivos passados como argumento pelo Git
files_to_translate = os.environ.get("CHANGED_FILES", "").split()

for file_path in files_to_translate:
    if file_path.startswith("./pt-br/") and file_path.endswith(".md"):
        print(f"Traduzindo: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            original_text = f.read()
            
        translated_text = translate_markdown(original_text)
        
        # Define o caminho de destino (trocando pt-br por en)
        target_path = file_path.replace("./pt-br/", "./en/")
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(translated_text)
