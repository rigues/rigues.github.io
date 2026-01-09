# 📚 Documentação do Software (Empresa X)

Este repositório centraliza toda a documentação técnica do nosso software. Utilizamos um fluxo de trabalho moderno baseado em **Markdown**, **GitHub Pages** e **Inteligência Artificial (Gemini)**.

## 🚀 Estrutura do Repositório

- `/docs/pt-br/`: Documentação original em português (Fonte da Verdade).
- `/docs/en/`: Documentação traduzida automaticamente para inglês.
- `.github/workflows/`: Automações (GitHub Actions).

## 🤖 Automação de Tradução

Não é necessário traduzir manualmente os artigos para o inglês. Implementamos um agente de IA usando o modelo **Gemini 2.0 Flash-Lite**.

### Como funciona:
1. Você cria ou edita um arquivo em `docs/pt-br/`.
2. Ao realizar o `git push`, uma **GitHub Action** é disparada.
3. O script `translate.py` identifica as mudanças e solicita a tradução via API do Google Gemini.
4. O robô faz o commit da versão traduzida diretamente na pasta `docs/en/`.

## 🛠️ Como Contribuir

1. Faça o clone do repositório: `git clone git@github.com:seu-usuario/seu-repo.git`.
2. Crie/edite arquivos **apenas** dentro de `docs/pt-br/`.
3. Salve e envie suas alterações:
   ```bash
   git add .
   git commit -m "docs: descrição da sua alteração"
   git push origin main
4. Aguarde ~1 minuto e verifique a pasta docs/en/ para ver a tradução.

## ⚠️ Observações Técnicas
* O script de tradução preserva blocos de código e links.
* Caso precise forçar uma tradução, você pode rodar o script localmente definindo a variável GEMINI_API_KEY.
