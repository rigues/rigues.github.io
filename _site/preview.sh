#!/bin/bash

echo "🚀 Iniciando servidor de documentação local..."

# Remove a pasta _site e .jekyll-cache para evitar erros de cache
echo "🧹 Limpando cache do Jekyll..."
bundle exec jekyll clean

# Inicia o servidor com LiveReload (atualiza o navegador ao salvar arquivos)
echo "🌐 Acesse: http://localhost:4000"
bundle exec jekyll serve --livereload
