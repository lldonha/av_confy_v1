# Guia de Workflows

Documentação completa dos workflows disponíveis no Lipsync ComfyUI.

## Workflows Disponíveis

1. [Basic Lipsync](#basic-lipsync) - Simples e rápido
2. [Segmented Lipsync](#segmented-lipsync) - Para textos longos
3. [Full Pipeline](#full-pipeline) - Geração completa

## Basic Lipsync

### Descrição

Workflow básico que aplica lipsync em uma imagem de retrato usando um texto curto.

### Quando Usar

- Vídeos de 10-30 segundos
- Texto até 500 caracteres
- Produção rápida
- Testes e prototipagem

### Uso

```bash
python scripts/run_workflow.py \
    --workflow basic \
    --image portrait.png \
    --text "Seu texto aqui"
```

### Parâmetros Configuráveis

```yaml
# config/config.yaml
workflow_settings:
  audio:
    language: "pt"           # Idioma (pt, en, es, etc)
    temperature: 0.7         # Criatividade (0.1-2.0)
    speed: 1.0               # Velocidade da fala (0.5-2.0)

  lipsync:
    lips_expression: 2.0     # Intensidade dos lábios (1.0-3.0)
    inference_steps: 25      # Qualidade (10-50)
    guidance_scale: 7.5      # Fidelidade (5.0-15.0)

  video:
    output_fps: 30           # FPS (24, 30, 60)
    resolution: [512, 512]   # Resolução (múltiplo de 64)
    quality: "high"          # Qualidade (low, medium, high, ultra)
```

### Performance

- **Tempo**: 2-5 minutos
- **VRAM**: ~8GB
- **GPU**: RTX 3060 12GB ou superior

### Fluxo do Workflow

```
1. LoadImage → Carrega imagem de retrato
2. XTTSTextToAudio → Gera áudio do texto
3. LatentSyncNode → Aplica lipsync
4. VHSVideoCombine → Combina frames + áudio
5. SaveVideo → Salva MP4 final
```

## Segmented Lipsync

### Descrição

Workflow para textos longos com segmentação automática.

### Quando Usar

- Vídeos de 30-90 segundos
- Textos de 500-2000 caracteres
- Narrações extensas
- Storytelling e narração contínua

### Uso

```bash
python scripts/run_workflow.py \
    --workflow segmented \
    --image portrait.png \
    --text-file long_script.txt
```

### Parâmetros Adicionais

```yaml
advanced:
  text_segmentation:
    enabled: true
    max_chars_per_segment: 500     # Tamanho dos segmentos
    split_on_punctuation: true     # Dividir em pontuação
    overlap_chars: 50               # Sobreposição entre segmentos
```

### Performance

- **Tempo**: 5-15 minutos (para 60s)
- **VRAM**: ~8GB
- **GPU**: RTX 4070 12GB recomendado

### Fluxo do Workflow

```
1. LoadImage → Carrega imagem
2. TextSegmenter → Divide texto em segmentos
3. XTTSTextToAudioBatch → Gera áudio por segmento
4. AudioConcatenate → Concatena áudios
5. LatentSyncNode → Aplica lipsync (batch)
6. VHSVideoCombine → Combina frames + áudio
7. SaveVideo → Salva MP4 final
```

### Dicas

- Use textos com pontuação clara para melhor segmentação
- Ajuste `max_chars_per_segment` baseado na complexidade
- `overlap_chars` melhora transições entre segmentos

## Full Pipeline

### Descrição

Pipeline completo que gera a imagem do personagem com Stable Diffusion e aplica lipsync.

### Quando Usar

- Produção completa do zero
- Quando não tem imagem de retrato
- Controle total sobre aparência do personagem
- Conteúdo do canal Cósmica Dread

### Uso

```bash
python scripts/run_workflow.py \
    --workflow full \
    --prompt "portrait of a mysterious person, dark atmosphere, horror style" \
    --text "Bem-vindo ao Cósmica Dread"
```

### Parâmetros da Geração de Imagem

```yaml
workflow_settings:
  image_generation:
    checkpoint: "realisticVisionV51.safetensors"
    steps: 30                    # Passos SD (20-50)
    cfg: 7.5                     # Guidance (7-15)
    sampler: "euler_a"           # Sampler
    resolution: [512, 512]

  # Preset para Cósmica Dread
  cosmica_dread:
    theme: "horror"
    add_effects: true
    effects:
      reverb: 0.3
      echo: 0.2
      distortion: 0.1
```

### Performance

- **Tempo**: 5-10 minutos (para 15s)
- **VRAM**: ~12GB
- **GPU**: RTX 4070 12GB ou superior

### Fluxo do Workflow

```
1. CheckpointLoaderSimple → Carrega modelo SD
2. VAELoader → Carrega VAE
3. CLIPTextEncode → Codifica prompts (positivo e negativo)
4. EmptyLatentImage → Cria latent vazio
5. KSampler → Gera imagem
6. VAEDecode → Decodifica para imagem
7. SaveImage → Salva retrato gerado
8. XTTSTextToAudio → Gera áudio
9. AudioEffects → Aplica efeitos de terror
10. LatentSyncNode → Aplica lipsync
11. VHSVideoCombine → Combina frames + áudio
12. VideoPostProcessing → Pós-processamento
13. SaveVideo → Salva MP4 final
```

### Preset Cósmica Dread

O workflow full inclui preset otimizado para conteúdo de terror:

```yaml
cosmica_dread:
  theme: "horror"
  default_voice: "narrator_dark"
  add_effects: true
  effects:
    reverb: 0.3          # Reverberação assustadora
    echo: 0.2            # Eco
    distortion: 0.1      # Distorção leve
    creepy_background: false
```

Para ativar:
```bash
python scripts/run_workflow.py \
    --workflow full \
    --preset cosmica_dread \
    --prompt "portrait" \
    --text "História de terror"
```

## Customizando Workflows

### Editando no ComfyUI

1. Abra ComfyUI:
```bash
cd ComfyUI
python main.py
```

2. Acesse `http://127.0.0.1:8188`
3. Carregue workflow: `Load` → selecione `workflows/basic_lipsync.json`
4. Edite nodes, conexões, parâmetros
5. Salve: `Save` → sobrescreva arquivo

### Criando Novo Workflow

1. Crie no ComfyUI visualmente
2. Exporte: `Save API Format`
3. Salve em `workflows/meu_workflow.json`
4. Adicione metadados:

```json
{
  "_workflow_info": {
    "name": "Meu Workflow",
    "version": "1.0",
    "description": "Descrição",
    "requirements": {
      "nodes": ["..."],
      "models": ["..."],
      "vram_min": "8GB"
    }
  },

  "1": {
    "class_type": "...",
    "inputs": {...}
  }
}
```

### Compartilhando Workflows

1. Teste o workflow
2. Valide:
```bash
python scripts/validate_setup.py --workflow meu_workflow
```
3. Documente no README
4. Faça PR no repositório

## Melhores Práticas

### Para Qualidade Máxima

```yaml
lipsync:
  inference_steps: 50      # Máximo (lento)
  guidance_scale: 10.0
video:
  quality: "ultra"
  output_fps: 60
```

### Para Velocidade Máxima

```yaml
lipsync:
  inference_steps: 10      # Mínimo (rápido)
  guidance_scale: 5.0
video:
  quality: "low"
  output_fps: 24
processing:
  use_half_precision: true
  low_vram_mode: false
```

### Para Economia de VRAM

```yaml
processing:
  use_half_precision: true
  low_vram_mode: true
  cpu_offload: true
video:
  resolution: [512, 512]  # Não use mais que isso
lipsync:
  inference_steps: 15
```

## Exemplos Práticos

### Exemplo 1: Vídeo curto de apresentação

```bash
python scripts/run_workflow.py \
    --workflow basic \
    --image presenter.png \
    --text "Olá, bem-vindo ao meu canal!" \
    --config config/config.yaml
```

### Exemplo 2: Narração de história

```bash
python scripts/run_workflow.py \
    --workflow segmented \
    --image narrator.png \
    --text-file story.txt \
    --output output/my_story.mp4
```

### Exemplo 3: Produção completa para Cósmica Dread

```bash
python scripts/run_workflow.py \
    --workflow full \
    --preset cosmica_dread \
    --prompt "mysterious hooded figure, dark background, horror cinematic lighting" \
    --text-file horror_script.txt \
    --output output/cosmica_dread_ep01.mp4
```

## Troubleshooting de Workflows

Veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para problemas específicos.

### Workflow não valida

```bash
python scripts/validate_setup.py --workflow basic
```

### Workflow muito lento

- Reduza `inference_steps`
- Use resolução menor
- Habilite `low_vram_mode`

### Qualidade ruim

- Aumente `inference_steps`
- Use `quality: "ultra"`
- Aumente resolução para 768x768

---

Para mais informações, veja [API.md](API.md) para referência completa de parâmetros.
