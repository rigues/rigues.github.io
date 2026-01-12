# 📚 Teste para automação de tradução da documentação do AIOS
Este repositório centraliza a documentação técnica do AIOS, utilizando um fluxo de trabalho baseado em **Markdown, Jekyll (Just the Docs)** e **IA (Gemini 2.0 Flash)**.

## 🚀 Estrutura do Repositório  
* `./pt-br/`: Documentação original em português (Fonte da Verdade).
* `./en/`: Documentação traduzida automaticamente para inglês.
* `./pt-br/images` e `./en/images`: Armazenamento de ativos visuais sincronizados.
* `.git/hooks/pre-push`: Script de automação que garante a sincronia antes de cada envio.

## 🤖 Sistema de Tradução Inteligente
Diferente de sistemas baseados apenas em nuvem, nossa solução utiliza um **Pre-push Hook** local. Isso evita conflitos de sincronia entre repositórios locais e remotos e permite validar a tradução antes do deploy.

Como funciona:
1. Você trabalha apenas nos arquivos dentro de `./pt-br/`.
2. Ao executar `git push`, o Git dispara o script de tradução automaticamente.
3. O script identifica quais arquivos foram criados ou modificados.
4. O **Gemini 2.0 Flash** processa o arquivo em um único lote (_batching_), traduzindo o conteúdo e metadados visuais do Jekyll, enquanto preserva campos técnicos do cabeçalho.
5. Um novo commit é gerado localmente com as traduções e enviado ao GitHub junto com as suas alterações.

## 🛠️ Guia de Implementação (Passo-a-passo)
Para replicar este sistema em um novo ambiente, siga estas etapas:

**1. Requisitos de Sistema**  
Certifique-se de ter o Python 3.10+ instalado e uma chave de API válida do Google AI Studio.

**2. Módulos Python Necessários**  
Instale as dependências no seu ambiente virtual:

`pip install google-genai pyyaml`

* `google-genai`: SDK oficial para interação com os modelos Gemini.
* `pyyaml`: Essencial para a manipulação e proteção do Front Matter (YAML) dos arquivos Jekyll.

**3. Configuração do Ambiente**
Defina sua chave de API como uma variável de ambiente no seu terminal ou arquivo `.bashrc` / `.zshrc`:

`export GEMINI_API_KEY="sua_chave_aqui"`

**4. Arquivos de Configuração Web**
Para que o GitHub Pages renderize o tema corretamente, crie os seguintes arquivos na raiz:

**_config.yml**

`remote_theme: just-the-docs/just-the-docs
plugins:
  - jekyll-remote-theme
  - jekyll-seo-tag`

**Gemfile**

`source "https://rubygems.org"
gem "github-pages", group: :jekyll_plugins
gem "jekyll-remote-theme"`

**5. Instalação do Pre-push Hook**
Crie o arquivo `.git/hooks/pre-push` e dê permissão de execução (com o comando `chmod +x`):

`#!/bin/bash
python3 translate.py
git add en/
if ! git diff --cached --quiet; then
    git commit -m "docs: tradução automática (local pre-push) [skip ci]"
fi`

## ⚠️ Observações de Cota e Uso
* **Limites de Taxa:** O plano gratuito possui um limite de 20 Requisições por Dia (RPD) para o modelo Flash.
* **Otimização:** O script está configurado para traduzir metadados e corpo em uma única chamada, maximizando o uso da cota.
* **Front Matter:** O sistema protege campos como layout e nav_order, traduzindo apenas title e description para garantir a integridade do menu de navegação.