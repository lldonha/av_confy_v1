# Guia de Troubleshooting

Soluções para problemas comuns ao usar o Lipsync ComfyUI Workflow.

## Índice

- [Erros de Instalação](#erros-de-instalação)
- [Erros de VRAM](#erros-de-vram)
- [Erros de Modelos](#erros-de-modelos)
- [Erros de Execução](#erros-de-execução)
- [Problemas de Performance](#problemas-de-performance)

## Erros de Instalação

### Python version incompatível

**Erro**: `Python 3.10+ necessário`

**Solução**:
```bash
# Instale Python 3.10+
sudo apt install python3.10  # Ubuntu
# ou baixe de python.org
```

### Dependências faltando

**Erro**: `ModuleNotFoundError: No module named 'X'`

**Solução**:
```bash
pip install -r requirements.txt
# ou
pip install X
```

### Custom nodes não instalam

**Erro**: `git clone failed` ou `Node X not found`

**Solução**:
```bash
python scripts/install_nodes.py
# ou manualmente:
cd ComfyUI/custom_nodes
git clone [URL_DO_NODE]
cd [NOME_DO_NODE]
pip install -r requirements.txt
```

## Erros de VRAM

### VRAM insuficiente

**Erro**: `CUDA out of memory` ou `VRAMInsufficientError`

**Soluções**:

1. **Use flag --lowvram:**
```bash
python ComfyUI/main.py --lowvram
```

2. **Reduza resolução:**
```yaml
# config/config.yaml
video:
  resolution: [512, 512]  # ao invés de [768, 768]
```

3. **Reduza inference steps:**
```yaml
lipsync:
  inference_steps: 15  # ao invés de 25
```

4. **Feche outros programas:**
```bash
# Verifique uso de VRAM
nvidia-smi
```

5. **Use --novram (último recurso):**
```bash
python ComfyUI/main.py --novram
# Muito mais lento mas funciona com menos VRAM
```

### GPU não detectada

**Erro**: `CUDA not available`

**Solução**:
```python
# Verificar instalação CUDA
import torch
print(torch.cuda.is_available())

# Se False, reinstale PyTorch com CUDA:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Erros de Modelos

### Modelo não encontrado

**Erro**: `ModelNotFoundError: Modelo 'X' não encontrado`

**Solução**:
```bash
# Re-baixe o modelo
python scripts/download_models.py --model "X"

# ou com force
python scripts/download_models.py --model "X" --force
```

### Modelo corrompido

**Erro**: `Checksum inválido` ou `Failed to load model`

**Solução**:
```bash
# Delete o modelo corrompido
rm ComfyUI/models/[tipo]/[arquivo]

# Re-baixe
python scripts/download_models.py --model "[nome]" --force
```

### Download falha

**Erro**: `Connection timeout` ou `Download failed`

**Soluções**:

1. **Verifique conexão:**
```bash
ping huggingface.co
```

2. **Use VPN** se houver bloqueio regional

3. **Download manual:**
   - Acesse URLs em config/models.yaml
   - Baixe manualmente
   - Coloque em ComfyUI/models/[tipo]/

## Erros de Execução

### Workflow inválido

**Erro**: `WorkflowValidationError`

**Solução**:
```bash
# Valide o workflow
python scripts/validate_setup.py --workflow basic

# Abra no ComfyUI para debug visual
# Carregue o JSON e identifique conexões quebradas
```

### Geração de áudio falha

**Erro**: `AudioGenerationError`

**Soluções**:

1. **Texto muito longo:**
```bash
# Use workflow segmentado
python scripts/run_workflow.py --workflow segmented
```

2. **Idioma não suportado:**
```yaml
# config/config.yaml
audio:
  language: "pt"  # use: pt, en, es, fr, de, it, etc
```

3. **XTTS não carregou:**
```bash
# Verifique modelo XTTS
python scripts/validate_setup.py
```

### Lipsync falha

**Erro**: `LipsyncFailedError: Face not detected`

**Soluções**:

1. **Use imagem de retrato frontal** com rosto visível
2. **Melhore qualidade da imagem** (mínimo 512x512)
3. **Ajuste detecção:**
```yaml
lipsync:
  face_detection_threshold: 0.7  # reduza se necessário
```

### FFmpeg não encontrado

**Erro**: `FFmpeg not found`

**Solução**:
```bash
# Ubuntu
sudo apt install ffmpeg

# Windows: baixe de ffmpeg.org e adicione ao PATH
```

## Problemas de Performance

### Execução muito lenta

**Soluções**:

1. **Verifique GPU está sendo usada:**
```python
import torch
print(torch.cuda.is_available())  # deve ser True
```

2. **Habilite xformers:**
```bash
pip install xformers
```

3. **Use batch processing:**
```yaml
processing:
  batch_size: 2
```

4. **Reduza qualidade temporariamente:**
```yaml
video:
  quality: "medium"  # ao invés de "high"
lipsync:
  inference_steps: 15  # ao invés de 25
```

### Out of Memory (RAM)

**Erro**: `MemoryError` ou sistema trava

**Soluções**:

1. **Aumente swap:**
```bash
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

2. **Processe em segmentos menores**

3. **Feche outros programas**

### Logs muito verbosos

**Solução**:
```yaml
# config/config.yaml
logging:
  console_level: "WARNING"  # ao invés de "INFO"
```

ou:
```bash
python scripts/run_workflow.py --workflow basic [args] 2>/dev/null
```

## Erros Específicos do ComfyUI

### ComfyUI não inicia

**Erro**: `Failed to start ComfyUI`

**Solução**:
```bash
# Teste manualmente
cd ComfyUI
python main.py

# Verifique erros no terminal
```

### Porta 8188 em uso

**Erro**: `Port 8188 already in use`

**Solução**:
```bash
# Use porta diferente
python ComfyUI/main.py --port 8189

# Atualize .env
COMFYUI_PORT=8189
```

### Custom nodes conflitantes

**Erro**: `Node conflict` ou `Duplicate node class`

**Solução**:
```bash
# Desabilite node conflitante
cd ComfyUI/custom_nodes
mv [NODE_CONFLITANTE] [NODE_CONFLITANTE].disabled
```

## Diagnóstico Geral

### Script de diagnóstico

```bash
# Execute diagnóstico completo
python scripts/validate_setup.py

# Com verbose
python scripts/validate_setup.py --verbose
```

### Verificar logs

```bash
# Logs do workflow
cat logs/lipsync_workflow.log

# Últimas 50 linhas
tail -50 logs/lipsync_workflow.log

# Filtrar erros
grep ERROR logs/lipsync_workflow.log
```

### Exportar logs para suporte

```bash
# O logger cria export automaticamente
# Ou manualmente:
python -c "from src.logger import get_logger_manager; get_logger_manager().export_logs()"
```

## Conseguindo Ajuda

Se o problema persistir:

1. **Verifique Issues existentes**: [GitHub Issues](https://github.com/seu-usuario/lipsync-comfyui-workflow/issues)
2. **Abra novo Issue** com:
   - Descrição do problema
   - Logs relevantes
   - Specs do sistema (GPU, RAM, etc)
   - Comandos executados
3. **Pergunte nas Discussions**: [GitHub Discussions](https://github.com/seu-usuario/lipsync-comfyui-workflow/discussions)

## Checklist de Debug

Antes de reportar problema, verifique:

- [ ] Python 3.10+ instalado
- [ ] Todas dependências instaladas (`pip list`)
- [ ] ComfyUI funciona standalone
- [ ] CUDA disponível (`nvidia-smi`)
- [ ] Modelos baixados corretamente
- [ ] Custom nodes instalados
- [ ] Caminhos em .env corretos
- [ ] VRAM suficiente (~8GB mínimo)
- [ ] Logs revisados
- [ ] Validação passou (`validate_setup.py`)

---

**Dica**: A maioria dos problemas são resolvidos com `python setup.py --comfyui-path [PATH]` para reinstalar tudo.
