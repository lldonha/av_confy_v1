# Guia de Instalação Completo

Este guia fornece instruções detalhadas para instalar o Lipsync ComfyUI Workflow.

## Índice

- [Pré-requisitos](#pré-requisitos)
- [Instalação do ComfyUI](#instalação-do-comfyui)
- [Instalação do Projeto](#instalação-do-projeto)
- [Instalação de Modelos](#instalação-de-modelos)
- [Verificação](#verificação)
- [Problemas Comuns](#problemas-comuns)

## Pré-requisitos

### 1. Sistema Operacional

**Linux (Ubuntu 20.04+):**
```bash
sudo apt update
sudo apt install -y python3.10 python3-pip git ffmpeg espeak-ng
```

**Windows 10/11:**
- Instale [Python 3.10+](https://www.python.org/downloads/)
- Instale [Git](https://git-scm.com/downloads)
- Instale [FFmpeg](https://ffmpeg.org/download.html)
- Baixe [espeak-ng](https://github.com/espeak-ng/espeak-ng/releases)

### 2. NVIDIA CUDA (para GPU)

```bash
# Ubuntu
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run
```

### 3. PyTorch com CUDA

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Instalação do ComfyUI

### Opção 1: Clone do GitHub

```bash
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
pip install -r requirements.txt
```

### Opção 2: Usar instalação existente

Se você já tem ComfyUI instalado, anote o caminho para usá-lo no setup.

## Instalação do Projeto

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/lipsync-comfyui-workflow
cd lipsync-comfyui-workflow
```

### 2. Criar Ambiente Virtual (Recomendado)

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Ambiente

```bash
cp .env.example .env
# Edite .env com seu editor preferido
nano .env  # ou vim, code, etc.
```

Ajuste principalmente:
```
COMFYUI_PATH=/caminho/para/ComfyUI
```

### 5. Executar Setup Automático

```bash
python setup.py --comfyui-path /caminho/para/ComfyUI
```

O setup irá:
- ✅ Verificar dependências
- ✅ Criar diretórios necessários
- ✅ Instalar custom nodes do ComfyUI
- ✅ Baixar modelos necessários
- ✅ Validar instalação

**Nota**: O download de modelos pode levar 30-60 minutos dependendo da sua conexão (~15GB total).

## Instalação de Modelos

### Download Automático

```bash
python scripts/download_models.py
```

### Download Seletivo

```bash
# Listar modelos
python scripts/download_models.py --list

# Baixar modelo específico
python scripts/download_models.py --model "XTTS v2"
```

### Download Manual

Se o download automático falhar, baixe manualmente:

1. **XTTS v2**: https://huggingface.co/coqui/XTTS-v2
2. **LatentSync 1.6**: https://huggingface.co/Doubiiu/LatentSync
3. **VAE**: https://huggingface.co/stabilityai/sd-vae-ft-mse-original

Coloque os modelos em:
- XTTS: `ComfyUI/models/xtts/`
- LatentSync: `ComfyUI/models/latentsync/`
- VAE: `ComfyUI/models/vae/`

## Verificação

### 1. Validar Instalação

```bash
python scripts/validate_setup.py
```

Deve mostrar:
```
✓ Versão Python
✓ ComfyUI
✓ Dependências
✓ Diretórios
✓ Arquivos de config
```

### 2. Testar Workflow

```bash
python scripts/run_workflow.py \
    --workflow basic \
    --image assets/test_portrait.png \
    --text "Teste de instalação bem-sucedido"
```

Se funcionar, você verá:
```
✓ Workflow executado com sucesso!
✓ Vídeo salvo: output/lipsync_basic_TIMESTAMP.mp4
```

## Problemas Comuns

### ImportError: No module named 'torch'

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### CUDA não disponível

Verifique instalação:
```python
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

Se False, reinstale PyTorch com CUDA.

### Custom nodes não instalam

Instale manualmente:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/REPO/ComfyUI-XTTS
cd ComfyUI-XTTS
pip install -r requirements.txt
```

### Modelos corrompidos

Re-baixe com --force:
```bash
python scripts/download_models.py --model "MODEL_NAME" --force
```

## Próximos Passos

1. Leia [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) para entender os workflows
2. Veja [API.md](API.md) para customizar configurações
3. Consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md) se tiver problemas

## Suporte

- Issues: [GitHub Issues](https://github.com/seu-usuario/lipsync-comfyui-workflow/issues)
- Discussions: [GitHub Discussions](https://github.com/seu-usuario/lipsync-comfyui-workflow/discussions)

---

Instalação completa! Você está pronto para gerar vídeos com lipsync 🎬
