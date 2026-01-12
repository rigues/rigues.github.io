---
layout: default
title: Organização e recursos da plataforma AIOS
parent: Visão Geral da Plataforma AIOS
nav_order: 1
description: "Organização básica da plataforma AIOS e lista de seus principais recursos."
---

# Organização e recursos da plataforma AIOS

<br>**Nesta página**:
* Table of Contents
{:toc}

## Estrutura básica da plataforma AIOS
A estrutura básica do AIOS pode dividida em quatro módulos, como ilustrado pela figura abaixo:
![Diagrama de fluxo da plataforma AIOS: aquisição de câmeras, processamento pela AlBox, controle via CLPs e APIs, com visualizações de dashboards, relatórios e gestão/apresentação.](./images/aios_platform_structure.png "Estrutura da plataforma AIOS")

| Módulo | Função | 
| :---|:---| 
| **Aquisição** | Captura de dados, usando câmeras (IP ou analógicas conectadas via DVR) para obter informações sobre o local ou situação a ser monitorada. |
| **Processamento** | Execução local dos algoritmos de IA e envio dos resultados à plataforma. | 
| **Controle** | Controle de periféricos (através de CLPs, Controladores Lógicos Programáveis) e outros sistemas (via APIs), com base nos resultados de detecção produzidos pelos algoritmos. | 
| **Gerenciamento e Apresentação** | Criação e gerenciamento de pipelines e dispositivos, análise de metadados gerados pela AIBox, produção de dashboards e reports para apresentação dos resultados. | 

## Principais recursos da plataforma AIOS
* **Interface no-code**: permite a criação de soluções de IA sem necessidade de programação.
* **Dezenas de componentes prontos para usar**: entre eles detecção de pessoas e objetos, contagem de eventos, ALPR, comunicação com dispositivos externos via CLPs ou GPIO, notificação em várias plataformas e muitos mais. 
* **Utiliza câmeras IP já existentes**: transforma as câmeras que você já tem em versáteis câmeras inteligentes com uma fração do custo de hardware dedicado.
* **Execução local (na AIBox) de algoritmos**: garante baixa latência na detecção de eventos.
* **Maior privacidade e menor consumo de banda**: somente os metadados resultantes do processamento são enviados à plataforma, reduzindo o risco de exposição de dados sensíveis (imagens captadas por suas câmeras) e o consumo de banda quando comparada a soluções que fazem o processamento na nuvem.
* **Dashboards customizáveis**: organize páginas, componentes, contadores e gráficos de acordo com sua necessidade Dashboards podem ser compartilhados na internet, com visibilidade pública ou controle de acesso por senha.
* **API para integração**: integre o AIOS a soluções e ferramentas já existentes, ou desenvolva soluções personalizadas que exijam processamento avançado.
* **Módulo de treinamento (Dojo)**: permite o desenvolvimento e treinamento de modelos de IA customizados, perfeitamente adaptados à sua necessidade.
* **Gerenciamento da frota de dispositivos (fleet management)**: veja quais dispositivos fazem parte de sua frota, quais pipelines estão disponíveis ou em execução, uso de recursos do sistema e mais.
* **Plataforma desenvolvida no Brasil**: adequada às necessidades do mercado nacional e com suporte técnico em português.
