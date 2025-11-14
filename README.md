# Lipsync ComfyUI Workflow 🎬

> Sistema de geração de vídeos com lipsync production-ready para o canal **CÓSMICA DREAD**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Compatible-green.svg)](https://github.com/comfyanonymous/ComfyUI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Índice

- [Sobre](#sobre)
- [Características](#características)
- [Pré-requisitos](#pré-requisitos)
- [Instalação Rápida](#instalação-rápida)
- [Uso Básico](#uso-básico)
- [Workflows Disponíveis](#workflows-disponíveis)
- [Configuração](#configuração)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## 🎯 Sobre

Este repositório fornece um sistema completo e production-ready para geração automatizada de vídeos com **lipsync de alta qualidade** usando ComfyUI. Desenvolvido especificamente para o canal de terror **CÓSMICA DREAD**, mas adaptável para qualquer tipo de conteúdo.

### O que este projeto faz?

1. **Gera áudio** a partir de texto usando XTTS v2 (multilíngue, suporta português)
2. **Aplica lipsync** de alta qualidade em imagens de retrato usando LatentSync 1.6
3. **Exporta vídeo** completo com áudio sincronizado
4. **Opcionalmente gera** a imagem do personagem com Stable Diffusion

### Por que usar este projeto?

✅ **1-Click Setup**: Clone, execute `setup.py` e está pronto
✅ **Production-Ready**: Código robusto com logs, tratamento de erros e testes
✅ **Documentação Completa**: Guias detalhados em português
✅ **Workflows Prontos**: 3 workflows otimizados para diferentes casos de uso
✅ **Modular**: Fácil de estender e customizar
✅ **GPU Otimizado**: Funciona em RTX 4070 12GB (e similar)

## ✨ Características

### Core Features

- 🎙️ **TTS Multilíngue**: XTTS v2 com suporte a 13 idiomas incluindo português
- 💋 **Lipsync de Alta Qualidade**: LatentSync 1.6 para sincronização labial realista
- 🎬 **Pipeline Completo**: Da geração de imagem ao vídeo final
- 📦 **Setup Automático**: Instalação de dependências, nodes e modelos automatizada
- 📊 **Logging Robusto**: Sistema de logs detalhado com níveis configuráveis
- ⚠️ **Tratamento de Erros**: Mensagens claras com sugestões de correção
- 🧪 **Testes Incluídos**: Suite completa de testes com pytest
- 📚 **Documentação Extensa**: Guias, troubleshooting e API docs

### Technical Features

- Suporte a textos longos com segmentação automática
- Estimativa de VRAM e validação de hardware
- Download de modelos com retry e resume
- Validação de checksums MD5/SHA256
- Execução síncrona e assíncrona
- Configuração via YAML e variáveis de ambiente
- CLI tools para todas as operações

## 🔧 Pré-requisitos

### Hardware Mínimo

- **GPU**: NVIDIA com 8GB VRAM (recomendado: RTX 4070 12GB)
- **RAM**: 16GB (recomendado: 64GB)
- **Armazenamento**: 50GB livres (para modelos)
- **OS**: Windows 10/11 ou Linux (Ubuntu 20.04+)

### Software

- **Python**: 3.10 ou superior
- **CUDA**: 11.8 ou superior (para GPU NVIDIA)
- **FFmpeg**: Para processamento de vídeo
- **Git**: Para clone de repositórios
- **ComfyUI**: Instalação funcional do ComfyUI

### Conhecimento

- Básico de terminal/command line
- Python básico (para customizações)
- Conceitos de machine learning (opcional)

## 🚀 Instalação Rápida

### 3 Comandos para Rodar

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/lipsync-comfyui-workflow
cd lipsync-comfyui-workflow

# 2. Execute o setup (aponta para sua instalação do ComfyUI)
python setup.py --comfyui-path /caminho/para/ComfyUI

# 3. Teste com workflow básico
python scripts/run_workflow.py --workflow basic \
    --image assets/test_portrait.png \
    --text "Bem-vindo ao Cósmica Dread"
```

### Instalação Detalhada

Para instalação passo-a-passo completa, veja [INSTALL.md](docs/INSTALL.md)

## 💡 Uso Básico

### Executar Workflow Básico

```bash
python scripts/run_workflow.py \
    --workflow basic \
    --image minha_imagem.png \
    --text "Texto para narração"
```

### Executar com Arquivo de Texto

```bash
python scripts/run_workflow.py \
    --workflow segmented \
    --image portrait.png \
    --text-file script.txt
```

### Validar Instalação

```bash
python scripts/validate_setup.py
```

### Download Manual de Modelos

```bash
# Listar modelos disponíveis
python scripts/download_models.py --list

# Baixar modelo específico
python scripts/download_models.py --model "XTTS v2"

# Baixar todos
python scripts/download_models.py
```

## 📂 Workflows Disponíveis

### 1. Basic Lipsync

**Uso**: Vídeos curtos e simples

```bash
python scripts/run_workflow.py --workflow basic --image portrait.png --text "Texto"
```

- ✅ Ideal para: Vídeos de 10-30 segundos
- ⏱️ Tempo: 2-5 minutos
- 💾 VRAM: ~8GB

### 2. Segmented Lipsync

**Uso**: Textos longos com segmentação automática

```bash
python scripts/run_workflow.py --workflow segmented --image portrait.png --text-file long_script.txt
```

- ✅ Ideal para: Narrações extensas, storytelling
- ⏱️ Tempo: 5-15 minutos para 60s de vídeo
- 💾 VRAM: ~8GB

### 3. Full Pipeline

**Uso**: Geração completa (imagem + lipsync)

```bash
python scripts/run_workflow.py --workflow full \
    --prompt "mysterious person in dark room" \
    --text "Welcome to the darkness"
```

- ✅ Ideal para: Produção completa do zero
- ⏱️ Tempo: 5-10 minutos para 15s
- 💾 VRAM: ~12GB

Veja [WORKFLOW_GUIDE.md](docs/WORKFLOW_GUIDE.md) para detalhes completos.

## ⚙️ Configuração

### Arquivos de Configuração

1. **config/config.yaml**: Configurações principais do workflow
2. **config/models.yaml**: Definição de modelos e URLs
3. **.env**: Variáveis de ambiente (copie de .env.example)

### Exemplo de Customização

```yaml
# config/config.yaml
workflow_settings:
  audio:
    language: "pt"
    temperature: 0.7

  lipsync:
    lips_expression: 2.0
    inference_steps: 25

  video:
    output_fps: 30
    resolution: [512, 512]
```

Veja [API.md](docs/API.md) para referência completa de configuração.

## 🐛 Troubleshooting

### Problemas Comuns

#### VRAM Insuficiente

```bash
# Use flag --lowvram no ComfyUI
python ComfyUI/main.py --lowvram
```

#### Modelo Não Encontrado

```bash
# Re-baixe o modelo específico
python scripts/download_models.py --model "nome_do_modelo" --force
```

#### Workflow Inválido

```bash
# Valide o workflow
python scripts/validate_setup.py --workflow basic
```

Veja [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) para lista completa de soluções.

## 🗺️ Roadmap

### Versão 1.1 (Próximo)

- [ ] Web UI com Gradio
- [ ] Suporte a Docker
- [ ] Batch processing de múltiplas imagens
- [ ] API REST para integração

### Versão 1.2 (Futuro)

- [ ] Suporte a vídeos de input (não só imagens)
- [ ] Múltiplos speakers
- [ ] Tradução automática de textos
- [ ] Cache inteligente de modelos

### Versão 2.0 (Visão)

- [ ] Support for real-time lipsync
- [ ] Mobile app integration
- [ ] Cloud processing option
- [ ] Marketplace de vozes customizadas

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Diretrizes

- Siga PEP 8 para código Python
- Adicione testes para novas features
- Atualize documentação quando necessário
- Use commits descritivos em português

## 📝 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.

## 🙏 Créditos

### Tecnologias Utilizadas

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - Interface para Stable Diffusion
- [XTTS v2](https://github.com/coqui-ai/TTS) - Text-to-Speech de alta qualidade
- [LatentSync](https://github.com/doubiiu/LatentSync) - Lipsync de última geração
- [Stable Diffusion](https://github.com/Stability-AI/stablediffusion) - Geração de imagens

### Desenvolvido Para

**CÓSMICA DREAD** - Canal de histórias de terror no YouTube

## 📞 Contato

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/lipsync-comfyui-workflow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/seu-usuario/lipsync-comfyui-workflow/discussions)

---

**Nota**: Este é um projeto em desenvolvimento ativo. Features podem mudar e bugs podem existir. Reporte problemas via GitHub Issues.

**Performance esperada**: Em uma RTX 4070 12GB, espere ~3-5 minutos para gerar um vídeo de 15 segundos com lipsync de alta qualidade.

Made with 💀 for CÓSMICA DREAD
