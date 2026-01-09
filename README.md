# 📚 Teste para automação de tradução da documentação do AIOS

Este repositório centraliza toda a documentação técnica do AIOS. Utilizamos um fluxo de trabalho moderno baseado em **Markdown**, **GitHub Pages** e **Inteligência Artificial (Gemini)**.

## 🚀 Estrutura do Repositório

- `./pt-br/`: Documentação original em português (Fonte da Verdade).
- `./pt-br/images`: Imagens para a documentação em português.
- `./en/`: Documentação traduzida automaticamente para inglês.
- `./en/images`: Imagens para a documentação em inglês. Devem ter o MESMO NOME que as imagens em português (mesmo que o conteúdo seja diferente), para evitar que links se quebrem na tradução.
- `.github/workflows/`: Automações (GitHub Actions).

## 🤖 Automação de Tradução

Não é necessário traduzir manualmente os artigos para o inglês. Implementamos um agente de IA usando o modelo **Gemini 2.0 Flash-Lite**.

### Como funciona:
1. Você cria ou edita um arquivo em `./pt-br/`.
2. Ao realizar o `git push`, uma **GitHub Action** é disparada.
3. O script `translate.py` identifica as mudanças e solicita a tradução via API do Google Gemini.
4. O robô faz o commit da versão traduzida diretamente na pasta `./en/`.

É recomendado verificar manualmente o resultado da tradução e corrigir eventuais erros como expressões não nativas. O script tem lógica para ignorar trechos de código, mas ainda assim um "double-check" é recomendado por precaução.

## 🛠️ Como Contribuir

1. Faça o clone do repositório: `git clone git@github.com:seu-usuario/seu-repo.git`.
2. Crie/edite arquivos **apenas** dentro de `./pt-br/`.
3. Salve e envie suas alterações:  
    `git add .`  
    `git commit -m "docs: descrição da sua alteração"`  
    `git push origin main`  
4. Aguarde ~1 minuto e verifique a pasta `./en/` para ver a tradução.

## ⚠️ Observações Técnicas
* O script de tradução preserva blocos de código e links.
* Caso precise forçar uma tradução, você pode rodar o script `translate.py` localmente. Não se esqueça de informar sua chave de API no GEMINI definindo a variável de ambiente `GEMINI_API_KEY`.
