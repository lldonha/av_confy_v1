# Referência da API

Documentação completa de todos os módulos, classes e configurações.

## Módulos Python

### src.logger

#### `setup_logging(log_dir, log_file, console_level, file_level)`

Configura sistema de logging global.

**Parâmetros:**
- `log_dir` (str): Diretório de logs
- `log_file` (str): Nome do arquivo de log
- `console_level` (str): Nível de log no console ("DEBUG", "INFO", etc)
- `file_level` (str): Nível de log no arquivo

**Retorna:** `LoggerManager`

#### `get_logger(component_name)`

Retorna logger para um componente.

**Parâmetros:**
- `component_name` (str): Nome do componente

**Retorna:** `ComponentLogger`

### src.error_handler

#### Classes de Exceção

**`ModelNotFoundError`**
```python
raise ModelNotFoundError(
    model_name="XTTS v2",
    model_type="TTS",
    expected_path="/path/to/model"
)
```

**`VRAMInsufficientError`**
```python
raise VRAMInsufficientError(
    required_vram="8GB",
    available_vram="6GB",
    component="LatentSync"
)
```

**`LipsyncFailedError`**
```python
raise LipsyncFailedError(
    frame_count=180,
    failed_at_frame=120,
    error_details="Face not detected"
)
```

### src.model_manager

#### `ModelManager(comfyui_path, models_config)`

Gerenciador de modelos.

**Métodos:**

```python
# Listar modelos necessários
models = model_manager.list_required()

# Verificar instalados
status = model_manager.check_installed()

# Baixar todos
successes, failures = model_manager.download_all(
    progress_callback=callback,
    skip_existing=True
)

# Validar integridade
results = model_manager.validate_integrity()
```

### src.workflow_executor

#### `WorkflowExecutor(workflow_path, config_path, comfyui_path)`

Executor de workflows.

**Métodos:**

```python
# Validar workflow
executor.validate_workflow()

# Checar dependências
deps = executor.check_dependencies()

# Estimar VRAM
vram_mb = executor.estimate_vram()

# Executar
result = executor.execute(
    inputs={"image": "path.png", "text": "texto"},
    progress_callback=callback
)

# Resultado
print(result.status)
print(result.outputs)
print(result.duration)
```

## Configuração YAML

### config.yaml

#### Seção: general

```yaml
general:
  project_name: "Nome do Projeto"
  version: "1.0.0"
  comfyui_path: "ComfyUI"
  comfyui_url: "http://127.0.0.1:8188"
```

#### Seção: logging

```yaml
logging:
  level: "INFO"            # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file_level: "DEBUG"
  console_level: "INFO"
  log_dir: "logs"
  log_file: "workflow.log"
  max_file_size_mb: 10
  backup_count: 5
```

#### Seção: workflow_settings.audio

```yaml
workflow_settings:
  audio:
    language: "pt"         # pt, en, es, fr, de, it, etc
    temperature: 0.7       # 0.1 (consistente) - 2.0 (criativo)
    speed: 1.0             # 0.5 - 2.0
    sample_rate: 24000     # 16000, 22050, 24000
```

#### Seção: workflow_settings.lipsync

```yaml
  lipsync:
    lips_expression: 2.0   # 1.0 - 3.0 (intensidade)
    inference_steps: 25    # 10 - 50 (qualidade)
    guidance_scale: 7.5    # 5.0 - 15.0 (fidelidade)
    strength: 0.8          # 0.5 - 1.0
```

#### Seção: workflow_settings.video

```yaml
  video:
    output_fps: 30         # 24, 25, 30, 60
    resolution: [512, 512] # Múltiplos de 64
    codec: "h264"          # h264, h265, vp9
    quality: "high"        # low, medium, high, ultra
    format: "mp4"          # mp4, avi, webm
```

#### Seção: performance

```yaml
performance:
  max_parallel_tasks: 2
  timeout_seconds: 600
  retry_on_failure: true
  max_retries: 3
```

#### Seção: hardware

```yaml
hardware:
  gpu_id: 0                    # GPU a usar
  max_vram_usage_gb: 10        # Limite de VRAM
  enable_cpu_fallback: true
```

#### Seção: advanced.text_segmentation

```yaml
advanced:
  text_segmentation:
    enabled: true
    max_chars_per_segment: 500
    split_on_punctuation: true
    overlap_chars: 50
```

#### Seção: cosmica_dread (personalizado)

```yaml
cosmica_dread:
  theme: "horror"
  default_voice: "narrator_dark"
  add_effects: true
  effects:
    reverb: 0.3              # 0.0 - 1.0
    echo: 0.2                # 0.0 - 1.0
    distortion: 0.1          # 0.0 - 1.0
    creepy_background: false
```

### models.yaml

#### Estrutura de Modelo

```yaml
models:
  - name: "Nome do Modelo"
    type: "xtts"                      # xtts, latentsync, checkpoint, vae, etc
    filename: "model.pth"
    destination: "models/xtts"        # Relativo ao ComfyUI
    url: "https://..."
    size: 1870000000                  # Bytes
    checksum: "md5hash"
    checksum_type: "md5"              # md5 ou sha256
    version: "2.0.0"
    description: "Descrição"
    required: true                    # true ou false
    priority: 1                       # 1 = alta, 5 = baixa
```

#### Download Settings

```yaml
download_settings:
  chunk_size: 1048576      # 1MB
  max_retries: 3
  retry_delay: 2           # segundos
  timeout: 300             # segundos
  verify_ssl: true
  use_cache: true
  parallel_downloads: 2
```

#### Workflow Requirements

```yaml
workflow_requirements:
  basic_lipsync:
    required:
      - "XTTS v2"
      - "LatentSync 1.6"
    optional:
      - "Realistic Vision v5.1"
```

## Variáveis de Ambiente (.env)

### Obrigatórias

```bash
COMFYUI_PATH=/path/to/ComfyUI
```

### Opcionais

```bash
# ComfyUI API
COMFYUI_URL=http://127.0.0.1:8188
COMFYUI_PORT=8188
COMFYUI_HOST=127.0.0.1

# Logging
LOG_LEVEL=INFO
CONSOLE_LOG_LEVEL=INFO
FILE_LOG_LEVEL=DEBUG
COLORED_LOGS=true

# Hardware
GPU_ID=0
MAX_VRAM_GB=10
LOW_VRAM_MODE=false
ENABLE_CPU_FALLBACK=true
ENABLE_XFORMERS=true
USE_HALF_PRECISION=true

# Audio (XTTS)
DEFAULT_LANGUAGE=pt
AUDIO_TEMPERATURE=0.7
AUDIO_SAMPLE_RATE=24000
SPEECH_SPEED=1.0

# Lipsync
LIPS_EXPRESSION=2.0
INFERENCE_STEPS=25
GUIDANCE_SCALE=7.5
LIPSYNC_STRENGTH=0.8

# Video
OUTPUT_FPS=30
VIDEO_WIDTH=512
VIDEO_HEIGHT=512
VIDEO_CODEC=h264
VIDEO_QUALITY=high
VIDEO_FORMAT=mp4
```

## Scripts CLI

### setup.py

```bash
python setup.py --mode install --comfyui-path /path/to/ComfyUI
python setup.py --mode validate
python setup.py --mode update-models
python setup.py --mode clean
```

**Flags:**
- `--verbose, -v`: Logs detalhados
- `--skip-deps`: Pular instalação de dependências
- `--skip-nodes`: Pular instalação de nodes
- `--skip-models`: Pular download de modelos

### scripts/run_workflow.py

```bash
python scripts/run_workflow.py \
    --workflow {basic|segmented|full} \
    --image path/to/image.png \
    [--text "texto"] \
    [--text-file path/to/text.txt] \
    [--output path/to/output.mp4] \
    [--config path/to/config.yaml] \
    [--comfyui-path path/to/ComfyUI] \
    [--debug]
```

### scripts/download_models.py

```bash
python scripts/download_models.py
python scripts/download_models.py --model "Model Name"
python scripts/download_models.py --list
python scripts/download_models.py --force
```

### scripts/install_nodes.py

```bash
python scripts/install_nodes.py
python scripts/install_nodes.py --node xtts
python scripts/install_nodes.py --list
```

### scripts/validate_setup.py

```bash
python scripts/validate_setup.py
python scripts/validate_setup.py --config
python scripts/validate_setup.py --workflow basic
```

## Workflow JSON

### Estrutura Básica

```json
{
  "_comment": "Comentário",
  "_workflow_info": {
    "name": "Nome",
    "version": "1.0",
    "description": "Descrição"
  },

  "1": {
    "class_type": "LoadImage",
    "inputs": {
      "image": "portrait.png"
    },
    "_meta": {
      "title": "Título do Node"
    }
  }
}
```

### Conexões Entre Nodes

```json
{
  "3": {
    "class_type": "LatentSyncNode",
    "inputs": {
      "image": ["1", 0],     // Output 0 do node 1
      "audio": ["2", 0],     // Output 0 do node 2
      "parameter": "value"
    }
  }
}
```

## Testes

### Executar Todos os Testes

```bash
pytest
pytest -v
pytest --cov=src
```

### Testes Específicos

```bash
pytest tests/test_dependencies.py
pytest tests/test_installation.py
pytest tests/test_workflow_basic.py
```

### Fixtures Disponíveis

```python
@pytest.fixture
def project_root():
    """Retorna caminho raiz do projeto"""

@pytest.fixture
def workflow_path():
    """Retorna caminho do workflow básico"""

@pytest.fixture
def executor(workflow_path, config_path):
    """Cria executor de workflow"""
```

## Extensões

### Criando Custom Logger

```python
from src.logger import get_logger

logger = get_logger("MeuComponente")
logger.info("Mensagem")
logger.debug("Debug")
logger.error("Erro")
logger.success("Sucesso")
```

### Criando Custom Error

```python
from src.error_handler import LipsyncWorkflowError

class MeuErro(LipsyncWorkflowError):
    def __init__(self, detalhes):
        super().__init__(
            message="Meu erro customizado",
            context={"detalhes": detalhes},
            suggestions=["Solução 1", "Solução 2"],
            docs_link="docs/MEU_ERRO.md"
        )
```

### Criando Custom Workflow

1. Crie no ComfyUI
2. Export API Format
3. Salve em `workflows/meu_workflow.json`
4. Adicione em `config/models.yaml`:

```yaml
workflow_requirements:
  meu_workflow:
    required:
      - "Modelo A"
      - "Modelo B"
```

## Performance Tuning

### Para Velocidade Máxima

```yaml
lipsync:
  inference_steps: 10
video:
  quality: "low"
processing:
  batch_size: 4
  use_half_precision: true
```

### Para Qualidade Máxima

```yaml
lipsync:
  inference_steps: 50
  guidance_scale: 12.0
video:
  quality: "ultra"
  output_fps: 60
```

### Para Economia de VRAM

```yaml
processing:
  low_vram_mode: true
  cpu_offload: true
video:
  resolution: [512, 512]
```

---

Para exemplos práticos, veja [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md).
