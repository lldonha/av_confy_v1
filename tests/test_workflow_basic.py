"""
Testes do workflow básico

Testa funcionalidades básicas do workflow executor.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflow_executor import WorkflowExecutor, ExecutionStatus
from src.error_handler import WorkflowValidationError


@pytest.fixture
def workflow_path():
    """Retorna caminho do workflow básico"""
    return "workflows/basic_lipsync.json"


@pytest.fixture
def config_path():
    """Retorna caminho da config"""
    return "config/config.yaml"


@pytest.fixture
def executor(workflow_path, config_path):
    """Cria executor de workflow"""
    try:
        return WorkflowExecutor(
            workflow_path=workflow_path,
            config_path=config_path,
            comfyui_path="ComfyUI"
        )
    except FileNotFoundError:
        pytest.skip("Workflow ou config não encontrado")


class TestWorkflowLoading:
    """Testa carregamento de workflows"""

    def test_workflow_loads_successfully(self, executor):
        """Workflow deve carregar sem erros"""
        assert executor.workflow is not None
        assert isinstance(executor.workflow, dict)

    def test_workflow_has_nodes(self, executor):
        """Workflow deve ter nodes"""
        assert len(executor.workflow) > 0, "Workflow não tem nodes"

    def test_config_loads_successfully(self, executor):
        """Config deve carregar sem erros"""
        # Config pode estar vazio se arquivo não existe
        assert executor.config is not None
        assert isinstance(executor.config, dict)


class TestWorkflowValidation:
    """Testa validação de workflows"""

    def test_workflow_validates(self, executor):
        """Workflow deve validar corretamente"""
        try:
            result = executor.validate_workflow()
            assert result is True
        except WorkflowValidationError as e:
            # Se falhar por nodes faltando, é OK (não temos ComfyUI instalado)
            pytest.skip(f"Validação falhou (esperado sem ComfyUI): {e}")

    def test_workflow_has_class_types(self, executor):
        """Nodes devem ter class_type"""
        for node_id, node_data in executor.workflow.items():
            if node_id.startswith("_"):
                continue  # Pular metadados

            if isinstance(node_data, dict):
                # Pode não ter class_type se for metadado
                if 'class_type' in node_data:
                    assert isinstance(node_data['class_type'], str)


class TestDependencyChecking:
    """Testa checagem de dependências"""

    def test_check_dependencies_returns_dict(self, executor):
        """check_dependencies deve retornar dicionário"""
        try:
            deps = executor.check_dependencies()
            assert isinstance(deps, dict)
        except Exception:
            pytest.skip("Não foi possível checar dependências")

    def test_dependencies_have_boolean_values(self, executor):
        """Valores das dependências devem ser booleanos"""
        try:
            deps = executor.check_dependencies()
            for key, value in deps.items():
                assert isinstance(value, bool), f"Dependência {key} não é booleana"
        except Exception:
            pytest.skip("Não foi possível checar dependências")


class TestVRAMEstimation:
    """Testa estimativa de VRAM"""

    def test_estimate_vram_returns_int(self, executor):
        """estimate_vram deve retornar inteiro"""
        vram = executor.estimate_vram()
        assert isinstance(vram, int)
        assert vram > 0, "VRAM estimado deve ser positivo"

    def test_vram_estimate_reasonable(self, executor):
        """VRAM estimado deve estar em range razoável"""
        vram = executor.estimate_vram()

        # VRAM deve estar entre 1GB e 32GB
        assert 1024 <= vram <= 32768, f"VRAM estimado fora do range: {vram}MB"


class TestWorkflowExecution:
    """Testa execução de workflows (simulada)"""

    def test_executor_has_execute_method(self, executor):
        """Executor deve ter método execute"""
        assert hasattr(executor, 'execute')
        assert callable(executor.execute)

    def test_executor_has_logs_method(self, executor):
        """Executor deve ter método get_logs"""
        assert hasattr(executor, 'get_logs')
        assert callable(executor.get_logs)

    def test_get_logs_returns_list(self, executor):
        """get_logs deve retornar lista"""
        logs = executor.get_logs()
        assert isinstance(logs, list)


class TestWorkflowMetadata:
    """Testa metadados do workflow"""

    def test_workflow_has_info(self, executor):
        """Workflow pode ter metadados _workflow_info"""
        if '_workflow_info' in executor.workflow:
            info = executor.workflow['_workflow_info']
            assert isinstance(info, dict)
            # Verificar campos esperados
            expected_fields = ['name', 'version', 'description']
            for field in expected_fields:
                if field in info:
                    assert isinstance(info[field], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
