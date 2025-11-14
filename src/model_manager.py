"""
Gerenciador de modelos para Lipsync ComfyUI Workflow

Funcionalidades:
- Lista modelos necessários de config/models.yaml
- Verifica quais estão instalados
- Download com retry automático
- Resume downloads interrompidos
- Validação de checksum MD5/SHA256
- Cache local de modelos
- Atualização de modelos obsoletos
"""

import hashlib
import os
import time
import requests
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

from .logger import get_logger
from .error_handler import ModelNotFoundError, DependencyError


class ModelStatus(Enum):
    """Status de um modelo"""
    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    OUTDATED = "outdated"
    CORRUPTED = "corrupted"
    DOWNLOADING = "downloading"


@dataclass
class ModelInfo:
    """
    Informações sobre um modelo

    Attributes:
        name: Nome do modelo
        type: Tipo (xtts, latentsync, checkpoint, etc)
        url: URL de download
        filename: Nome do arquivo
        size: Tamanho em bytes
        checksum: Hash MD5 ou SHA256
        checksum_type: Tipo do hash (md5 ou sha256)
        destination: Caminho de destino relativo ao ComfyUI
        status: Status atual do modelo
        version: Versão do modelo
        description: Descrição
    """
    name: str
    type: str
    url: str
    filename: str
    size: int
    checksum: Optional[str] = None
    checksum_type: str = "md5"
    destination: str = ""
    status: ModelStatus = ModelStatus.NOT_INSTALLED
    version: Optional[str] = None
    description: Optional[str] = None


class ModelManager:
    """
    Gerenciador central de modelos do sistema

    Example:
        >>> model_manager = ModelManager(comfyui_path="/path/to/ComfyUI")
        >>> models = model_manager.list_required()
        >>> model_manager.check_installed()
        >>> model_manager.download_all(progress_callback=print)
        >>> model_manager.validate_integrity()
    """

    def __init__(
        self,
        comfyui_path: str = "ComfyUI",
        models_config: str = "config/models.yaml",
        cache_dir: str = ".model_cache",
        max_retries: int = 3,
        timeout: int = 300
    ):
        """
        Inicializa o gerenciador de modelos

        Args:
            comfyui_path: Caminho para instalação do ComfyUI
            models_config: Arquivo YAML com configurações dos modelos
            cache_dir: Diretório para cache de downloads
            max_retries: Número máximo de tentativas de download
            timeout: Timeout em segundos para downloads
        """
        self.comfyui_path = Path(comfyui_path)
        self.models_config = Path(models_config)
        self.cache_dir = Path(cache_dir)
        self.max_retries = max_retries
        self.timeout = timeout

        self.logger = get_logger("ModelManager")

        # Criar diretório de cache
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Carregar configuração de modelos
        self.models: Dict[str, ModelInfo] = {}
        self._load_models_config()

    def _load_models_config(self):
        """Carrega configuração de modelos do YAML"""
        if not self.models_config.exists():
            self.logger.warning(f"Arquivo de configuração não encontrado: {self.models_config}")
            return

        try:
            with open(self.models_config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not config or 'models' not in config:
                self.logger.warning("Configuração de modelos vazia ou inválida")
                return

            # Processar cada modelo
            for model_data in config['models']:
                model_info = ModelInfo(
                    name=model_data['name'],
                    type=model_data['type'],
                    url=model_data['url'],
                    filename=model_data['filename'],
                    size=model_data.get('size', 0),
                    checksum=model_data.get('checksum'),
                    checksum_type=model_data.get('checksum_type', 'md5'),
                    destination=model_data.get('destination', ''),
                    version=model_data.get('version'),
                    description=model_data.get('description')
                )

                self.models[model_info.name] = model_info

            self.logger.info(f"Carregados {len(self.models)} modelos da configuração")

        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração de modelos: {e}")
            raise

    def list_required(self) -> List[ModelInfo]:
        """
        Lista todos os modelos necessários

        Returns:
            Lista de ModelInfo
        """
        return list(self.models.values())

    def check_installed(self) -> Dict[str, ModelStatus]:
        """
        Verifica quais modelos estão instalados

        Returns:
            Dicionário {nome_modelo: status}
        """
        status_dict = {}

        for name, model in self.models.items():
            model_path = self._get_model_path(model)

            if not model_path.exists():
                status = ModelStatus.NOT_INSTALLED
            elif model.checksum and not self._verify_checksum(model_path, model.checksum, model.checksum_type):
                status = ModelStatus.CORRUPTED
            else:
                status = ModelStatus.INSTALLED

            model.status = status
            status_dict[name] = status

        return status_dict

    def _get_model_path(self, model: ModelInfo) -> Path:
        """Retorna caminho completo do modelo"""
        if model.destination:
            return self.comfyui_path / model.destination / model.filename
        else:
            # Caminho padrão baseado no tipo
            type_paths = {
                'xtts': 'models/xtts',
                'latentsync': 'models/latentsync',
                'checkpoint': 'models/checkpoints',
                'vae': 'models/vae',
                'lora': 'models/loras',
                'controlnet': 'models/controlnet'
            }
            base_path = type_paths.get(model.type, 'models')
            return self.comfyui_path / base_path / model.filename

    def download_model(
        self,
        model_name: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        force: bool = False
    ) -> bool:
        """
        Baixa um modelo específico

        Args:
            model_name: Nome do modelo
            progress_callback: Callback(bytes_downloaded, total_bytes, status_message)
            force: Forçar download mesmo se já existir

        Returns:
            True se download foi bem-sucedido

        Raises:
            ModelNotFoundError: Se modelo não está na configuração
        """
        if model_name not in self.models:
            raise ModelNotFoundError(
                model_name=model_name,
                model_type="Unknown",
                expected_path=str(self.comfyui_path / "models")
            )

        model = self.models[model_name]
        model_path = self._get_model_path(model)

        # Verificar se já existe
        if model_path.exists() and not force:
            self.logger.info(f"Modelo {model_name} já existe em {model_path}")
            if self._verify_checksum(model_path, model.checksum, model.checksum_type):
                self.logger.success(f"Modelo {model_name} verificado com sucesso")
                return True
            else:
                self.logger.warning(f"Checksum inválido para {model_name}, baixando novamente")

        # Criar diretório de destino
        model_path.parent.mkdir(parents=True, exist_ok=True)

        # Baixar com retry
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Baixando {model_name} (tentativa {attempt}/{self.max_retries})")
                self._download_file(
                    url=model.url,
                    destination=model_path,
                    expected_size=model.size,
                    progress_callback=progress_callback
                )

                # Verificar checksum
                if model.checksum:
                    if self._verify_checksum(model_path, model.checksum, model.checksum_type):
                        self.logger.success(f"Modelo {model_name} baixado e verificado com sucesso")
                        model.status = ModelStatus.INSTALLED
                        return True
                    else:
                        self.logger.error(f"Checksum inválido para {model_name}")
                        model_path.unlink(missing_ok=True)
                        if attempt < self.max_retries:
                            continue
                        return False
                else:
                    self.logger.success(f"Modelo {model_name} baixado com sucesso (sem verificação de checksum)")
                    model.status = ModelStatus.INSTALLED
                    return True

            except Exception as e:
                self.logger.error(f"Erro ao baixar {model_name}: {e}")
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Backoff exponencial
                    self.logger.info(f"Aguardando {wait_time}s antes de tentar novamente...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Falha ao baixar {model_name} após {self.max_retries} tentativas")
                    return False

        return False

    def _download_file(
        self,
        url: str,
        destination: Path,
        expected_size: int = 0,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ):
        """
        Baixa arquivo com suporte a resume e progress callback

        Args:
            url: URL do arquivo
            destination: Caminho de destino
            expected_size: Tamanho esperado em bytes
            progress_callback: Callback para progresso
        """
        # Verificar se existe download parcial
        temp_file = destination.with_suffix(destination.suffix + '.part')
        resume_pos = 0

        if temp_file.exists():
            resume_pos = temp_file.stat().st_size
            self.logger.info(f"Resumindo download de {resume_pos} bytes")

        # Headers para resume
        headers = {}
        if resume_pos > 0:
            headers['Range'] = f'bytes={resume_pos}-'

        # Fazer request
        response = requests.get(url, headers=headers, stream=True, timeout=self.timeout)
        response.raise_for_status()

        # Obter tamanho total
        total_size = int(response.headers.get('content-length', 0))
        if resume_pos > 0:
            total_size += resume_pos

        # Callback inicial
        if progress_callback:
            progress_callback(resume_pos, total_size, f"Iniciando download de {destination.name}")

        # Baixar em chunks
        chunk_size = 1024 * 1024  # 1MB
        downloaded = resume_pos

        mode = 'ab' if resume_pos > 0 else 'wb'
        with open(temp_file, mode) as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Callback de progresso
                    if progress_callback:
                        percentage = (downloaded / total_size * 100) if total_size > 0 else 0
                        status_msg = f"Baixando {destination.name}: {percentage:.1f}% ({downloaded}/{total_size} bytes)"
                        progress_callback(downloaded, total_size, status_msg)

        # Renomear arquivo temporário para final
        temp_file.rename(destination)

        self.logger.info(f"Download concluído: {destination}")

    def _verify_checksum(self, file_path: Path, expected_checksum: Optional[str], checksum_type: str = "md5") -> bool:
        """
        Verifica checksum de um arquivo

        Args:
            file_path: Caminho do arquivo
            expected_checksum: Checksum esperado
            checksum_type: Tipo (md5 ou sha256)

        Returns:
            True se checksum é válido ou não foi fornecido
        """
        if not expected_checksum:
            return True

        if not file_path.exists():
            return False

        self.logger.debug(f"Verificando {checksum_type} de {file_path.name}")

        # Calcular hash
        if checksum_type.lower() == 'md5':
            hasher = hashlib.md5()
        elif checksum_type.lower() == 'sha256':
            hasher = hashlib.sha256()
        else:
            self.logger.warning(f"Tipo de checksum desconhecido: {checksum_type}")
            return True

        # Ler arquivo em chunks
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

        calculated = hasher.hexdigest()
        is_valid = calculated.lower() == expected_checksum.lower()

        if not is_valid:
            self.logger.error(f"Checksum inválido para {file_path.name}")
            self.logger.debug(f"Esperado: {expected_checksum}")
            self.logger.debug(f"Calculado: {calculated}")

        return is_valid

    def download_all(
        self,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        skip_existing: bool = True
    ) -> Tuple[int, int]:
        """
        Baixa todos os modelos necessários

        Args:
            progress_callback: Callback para progresso
            skip_existing: Pular modelos já instalados

        Returns:
            Tupla (sucessos, falhas)
        """
        self.logger.info("Iniciando download de todos os modelos")

        # Verificar quais precisam ser baixados
        status = self.check_installed()
        to_download = [
            name for name, st in status.items()
            if not skip_existing or st != ModelStatus.INSTALLED
        ]

        if not to_download:
            self.logger.success("Todos os modelos já estão instalados")
            return (len(self.models), 0)

        self.logger.info(f"Modelos a baixar: {len(to_download)}")

        successes = 0
        failures = 0

        for i, model_name in enumerate(to_download, 1):
            self.logger.info(f"Baixando modelo {i}/{len(to_download)}: {model_name}")

            # Callback de progresso geral
            if progress_callback:
                progress_callback(i - 1, len(to_download), f"Baixando {model_name}")

            if self.download_model(model_name, progress_callback):
                successes += 1
            else:
                failures += 1

        # Callback final
        if progress_callback:
            progress_callback(len(to_download), len(to_download), "Download concluído")

        self.logger.info(f"Download finalizado: {successes} sucessos, {failures} falhas")

        return (successes, failures)

    def validate_integrity(self) -> Dict[str, bool]:
        """
        Valida integridade de todos os modelos instalados

        Returns:
            Dicionário {nome_modelo: is_valid}
        """
        self.logger.info("Validando integridade dos modelos")

        results = {}
        for name, model in self.models.items():
            model_path = self._get_model_path(model)

            if not model_path.exists():
                self.logger.warning(f"Modelo {name} não encontrado")
                results[name] = False
                continue

            if model.checksum:
                is_valid = self._verify_checksum(model_path, model.checksum, model.checksum_type)
                results[name] = is_valid

                if is_valid:
                    self.logger.success(f"Modelo {name} validado com sucesso")
                else:
                    self.logger.error(f"Modelo {name} está corrompido")
            else:
                # Sem checksum para validar
                results[name] = True
                self.logger.info(f"Modelo {name} presente (sem checksum para validar)")

        return results

    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Retorna informações sobre um modelo"""
        return self.models.get(model_name)

    def list_missing(self) -> List[str]:
        """Retorna lista de modelos faltantes"""
        status = self.check_installed()
        return [name for name, st in status.items() if st == ModelStatus.NOT_INSTALLED]

    def list_corrupted(self) -> List[str]:
        """Retorna lista de modelos corrompidos"""
        status = self.check_installed()
        return [name for name, st in status.items() if st == ModelStatus.CORRUPTED]

    def cleanup_cache(self):
        """Remove arquivos temporários do cache"""
        self.logger.info("Limpando cache de downloads")

        removed = 0
        for file_path in self.cache_dir.glob("*.part"):
            try:
                file_path.unlink()
                removed += 1
            except Exception as e:
                self.logger.error(f"Erro ao remover {file_path}: {e}")

        self.logger.info(f"Removidos {removed} arquivos temporários")


if __name__ == "__main__":
    # Teste do gerenciador de modelos
    print("Testando ModelManager...")

    manager = ModelManager(
        comfyui_path="ComfyUI",
        models_config="config/models.yaml"
    )

    print("\n=== MODELOS NECESSÁRIOS ===")
    for model in manager.list_required():
        print(f"  • {model.name} ({model.type}) - {model.filename}")

    print("\n=== STATUS DOS MODELOS ===")
    status = manager.check_installed()
    for name, st in status.items():
        print(f"  • {name}: {st.value}")

    print("\n=== MODELOS FALTANTES ===")
    missing = manager.list_missing()
    if missing:
        for name in missing:
            print(f"  • {name}")
    else:
        print("  Nenhum modelo faltando")
