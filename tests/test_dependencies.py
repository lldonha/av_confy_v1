"""
Testes de dependências Python

Valida que todas as dependências necessárias estão instaladas
e com versões corretas.
"""

import pytest
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPythonVersion:
    """Testa versão do Python"""

    def test_python_version_minimum(self):
        """Python deve ser 3.10 ou superior"""
        assert sys.version_info >= (3, 10), f"Python 3.10+ necessário, versão atual: {sys.version_info}"


class TestCriticalDependencies:
    """Testa dependências críticas"""

    def test_torch_installed(self):
        """PyTorch deve estar instalado"""
        try:
            import torch
            assert True
        except ImportError:
            pytest.fail("PyTorch não instalado")

    def test_torch_cuda_available(self):
        """CUDA deve estar disponível (opcional, mas recomendado)"""
        try:
            import torch
            if torch.cuda.is_available():
                print(f"\n✓ CUDA disponível: {torch.cuda.get_device_name(0)}")
            else:
                pytest.skip("CUDA não disponível (OK para CPU)")
        except ImportError:
            pytest.skip("PyTorch não instalado")

    def test_numpy_installed(self):
        """NumPy deve estar instalado"""
        try:
            import numpy
            assert True
        except ImportError:
            pytest.fail("NumPy não instalado")

    def test_pil_installed(self):
        """Pillow deve estar instalado"""
        try:
            from PIL import Image
            assert True
        except ImportError:
            pytest.fail("Pillow não instalado")

    def test_yaml_installed(self):
        """PyYAML deve estar instalado"""
        try:
            import yaml
            assert True
        except ImportError:
            pytest.fail("PyYAML não instalado")

    def test_requests_installed(self):
        """Requests deve estar instalado"""
        try:
            import requests
            assert True
        except ImportError:
            pytest.fail("Requests não instalado")


class TestOptionalDependencies:
    """Testa dependências opcionais"""

    def test_colorama_installed(self):
        """Colorama para logs coloridos"""
        try:
            import colorama
            pytest.skip("Colorama instalado ✓")
        except ImportError:
            pytest.skip("Colorama não instalado (opcional)")

    def test_xformers_installed(self):
        """xformers para otimização"""
        try:
            import xformers
            pytest.skip("xformers instalado ✓")
        except ImportError:
            pytest.skip("xformers não instalado (opcional mas recomendado)")


class TestProjectModules:
    """Testa módulos do projeto"""

    def test_import_logger(self):
        """Módulo de logging deve importar"""
        from src.logger import get_logger, setup_logging
        assert callable(get_logger)
        assert callable(setup_logging)

    def test_import_error_handler(self):
        """Módulo de error handler deve importar"""
        from src.error_handler import (
            ModelNotFoundError,
            VRAMInsufficientError,
            LipsyncWorkflowError
        )
        assert issubclass(ModelNotFoundError, Exception)
        assert issubclass(VRAMInsufficientError, Exception)

    def test_import_model_manager(self):
        """Módulo de model manager deve importar"""
        from src.model_manager import ModelManager
        assert ModelManager is not None

    def test_import_workflow_executor(self):
        """Módulo de workflow executor deve importar"""
        from src.workflow_executor import WorkflowExecutor
        assert WorkflowExecutor is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
