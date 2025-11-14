"""
Sistema de logging robusto para Lipsync ComfyUI Workflow

Implementa logging com:
- Rotação automática de arquivos (max 10MB, 5 backups)
- Logs coloridos no console
- Níveis DEBUG, INFO, WARNING, ERROR, CRITICAL
- Contexto de execução (timestamp, função, linha)
- Logs específicos por componente
- Exportação de logs para debugging
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class LogLevel(Enum):
    """Níveis de log customizados"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    SUCCESS = 25  # Nível customizado entre INFO e WARNING


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para console"""

    def __init__(self, fmt: str, datefmt: str):
        super().__init__(fmt, datefmt)

        if COLORAMA_AVAILABLE:
            self.COLORS = {
                'DEBUG': Fore.CYAN,
                'INFO': Fore.WHITE,
                'WARNING': Fore.YELLOW,
                'ERROR': Fore.RED,
                'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
                'SUCCESS': Fore.GREEN + Style.BRIGHT
            }
        else:
            self.COLORS = {}

    def format(self, record):
        if COLORAMA_AVAILABLE and record.levelname in self.COLORS:
            # Colorir o nível de log
            levelname_color = self.COLORS[record.levelname] + record.levelname + Style.RESET_ALL
            record.levelname = levelname_color

        return super().format(record)


class ComponentLogger:
    """
    Logger específico para componentes do sistema
    Permite rastrear logs por módulo (TTS, Lipsync, Video, etc)
    """

    def __init__(self, component_name: str, logger: logging.Logger):
        self.component_name = component_name
        self.logger = logger
        self._logs_buffer: List[str] = []

    def _log(self, level: int, message: str, **kwargs):
        """Log interno com prefixo do componente"""
        formatted_msg = f"[{self.component_name}] {message}"
        self.logger.log(level, formatted_msg, **kwargs)

        # Armazenar em buffer para exportação
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._logs_buffer.append(f"[{timestamp}] [{logging.getLevelName(level)}] {formatted_msg}")

    def debug(self, message: str, **kwargs):
        """Log nível DEBUG"""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log nível INFO"""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log nível WARNING"""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log nível ERROR"""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log nível CRITICAL"""
        self._log(logging.CRITICAL, message, **kwargs)

    def success(self, message: str, **kwargs):
        """Log nível SUCCESS (customizado)"""
        self._log(LogLevel.SUCCESS.value, message, **kwargs)

    def get_logs(self) -> List[str]:
        """Retorna logs armazenados no buffer"""
        return self._logs_buffer.copy()

    def clear_logs(self):
        """Limpa buffer de logs"""
        self._logs_buffer.clear()


class LoggerManager:
    """
    Gerenciador central de logging do sistema
    """

    def __init__(
        self,
        log_dir: str = "logs",
        log_file: str = "lipsync_workflow.log",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG
    ):
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / log_file
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.console_level = console_level
        self.file_level = file_level

        # Criar diretório de logs se não existe
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Logger principal
        self.logger = logging.getLogger("LipsyncWorkflow")
        self.logger.setLevel(logging.DEBUG)

        # Registrar nível SUCCESS customizado
        logging.addLevelName(LogLevel.SUCCESS.value, "SUCCESS")

        # Remover handlers existentes para evitar duplicação
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Setup handlers
        self._setup_file_handler()
        self._setup_console_handler()

        # Cache de component loggers
        self._component_loggers: Dict[str, ComponentLogger] = {}

    def _setup_file_handler(self):
        """Configura handler para arquivo com rotação"""
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.file_level)

        # Formato detalhado para arquivo
        file_formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        self.logger.addHandler(file_handler)

    def _setup_console_handler(self):
        """Configura handler para console com cores"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.console_level)

        # Formato colorido para console
        console_formatter = ColoredFormatter(
            fmt='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(console_handler)

    def get_component_logger(self, component_name: str) -> ComponentLogger:
        """
        Retorna logger específico para um componente

        Args:
            component_name: Nome do componente (ex: "TTS", "Lipsync", "Video")

        Returns:
            ComponentLogger configurado

        Example:
            >>> logger_manager = LoggerManager()
            >>> tts_logger = logger_manager.get_component_logger("TTS")
            >>> tts_logger.info("Gerando áudio...")
        """
        if component_name not in self._component_loggers:
            self._component_loggers[component_name] = ComponentLogger(
                component_name,
                self.logger
            )

        return self._component_loggers[component_name]

    def export_logs(self, output_path: Optional[str] = None) -> str:
        """
        Exporta logs para arquivo de debugging

        Args:
            output_path: Caminho de saída (padrão: logs/export_TIMESTAMP.log)

        Returns:
            Caminho do arquivo exportado
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.log_dir / f"export_{timestamp}.log"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Coletar logs de todos os componentes
        all_logs = []
        for component_logger in self._component_loggers.values():
            all_logs.extend(component_logger.get_logs())

        # Ordenar por timestamp
        all_logs.sort()

        # Escrever arquivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("LIPSYNC COMFYUI WORKFLOW - EXPORT DE LOGS\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write("\n".join(all_logs))

        self.logger.info(f"Logs exportados para: {output_path}")
        return str(output_path)

    def set_console_level(self, level: int):
        """Altera nível de log do console em tempo real"""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
                handler.setLevel(level)

    def set_file_level(self, level: int):
        """Altera nível de log do arquivo em tempo real"""
        for handler in self.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.setLevel(level)


# Instância global do logger manager
_logger_manager: Optional[LoggerManager] = None


def setup_logging(
    log_dir: str = "logs",
    log_file: str = "lipsync_workflow.log",
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> LoggerManager:
    """
    Configura sistema de logging global

    Args:
        log_dir: Diretório para arquivos de log
        log_file: Nome do arquivo de log
        console_level: Nível de log para console (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        file_level: Nível de log para arquivo
        max_bytes: Tamanho máximo do arquivo antes de rotação
        backup_count: Número de backups a manter

    Returns:
        Instância do LoggerManager

    Example:
        >>> logger_manager = setup_logging(console_level="DEBUG")
        >>> logger = logger_manager.get_component_logger("Main")
        >>> logger.info("Sistema inicializado")
    """
    global _logger_manager

    # Converter strings de nível para constantes
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    console_level_int = level_map.get(console_level.upper(), logging.INFO)
    file_level_int = level_map.get(file_level.upper(), logging.DEBUG)

    _logger_manager = LoggerManager(
        log_dir=log_dir,
        log_file=log_file,
        max_bytes=max_bytes,
        backup_count=backup_count,
        console_level=console_level_int,
        file_level=file_level_int
    )

    return _logger_manager


def get_logger(component_name: str = "General") -> ComponentLogger:
    """
    Retorna logger para um componente
    Inicializa sistema de logging se necessário

    Args:
        component_name: Nome do componente

    Returns:
        ComponentLogger configurado

    Example:
        >>> logger = get_logger("TTS")
        >>> logger.info("Iniciando geração de áudio")
    """
    global _logger_manager

    if _logger_manager is None:
        _logger_manager = setup_logging()

    return _logger_manager.get_component_logger(component_name)


def get_logger_manager() -> LoggerManager:
    """
    Retorna instância do LoggerManager
    Inicializa se necessário
    """
    global _logger_manager

    if _logger_manager is None:
        _logger_manager = setup_logging()

    return _logger_manager


# Funções de conveniência para logging rápido
def debug(message: str, component: str = "General"):
    """Log rápido nível DEBUG"""
    get_logger(component).debug(message)


def info(message: str, component: str = "General"):
    """Log rápido nível INFO"""
    get_logger(component).info(message)


def warning(message: str, component: str = "General"):
    """Log rápido nível WARNING"""
    get_logger(component).warning(message)


def error(message: str, component: str = "General"):
    """Log rápido nível ERROR"""
    get_logger(component).error(message)


def critical(message: str, component: str = "General"):
    """Log rápido nível CRITICAL"""
    get_logger(component).critical(message)


def success(message: str, component: str = "General"):
    """Log rápido nível SUCCESS"""
    get_logger(component).success(message)


if __name__ == "__main__":
    # Teste do sistema de logging
    logger_manager = setup_logging(console_level="DEBUG")

    # Testar diferentes componentes
    main_logger = logger_manager.get_component_logger("Main")
    tts_logger = logger_manager.get_component_logger("TTS")
    lipsync_logger = logger_manager.get_component_logger("Lipsync")

    main_logger.info("Sistema de logging inicializado")
    main_logger.debug("Modo debug ativado")

    tts_logger.info("Gerando áudio: 12.3s, 24kHz")
    tts_logger.success("Áudio gerado com sucesso")

    lipsync_logger.info("Processando frames...")
    lipsync_logger.warning("VRAM em 85% de uso")
    lipsync_logger.success("Processamento completo: 180 frames")

    main_logger.error("Erro de exemplo (não é real)")
    main_logger.critical("Erro crítico de exemplo (não é real)")

    # Exportar logs
    logger_manager.export_logs()
