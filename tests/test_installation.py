"""
Testes de instalação

Valida que o projeto está corretamente instalado e configurado.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def project_root():
    """Retorna caminho raiz do projeto"""
    return Path(__file__).parent.parent


class TestDirectoryStructure:
    """Testa estrutura de diretórios"""

    def test_required_directories_exist(self, project_root):
        """Diretórios obrigatórios devem existir"""
        required_dirs = [
            "src",
            "config",
            "workflows",
            "scripts",
            "tests",
            "logs",
            "output"
        ]

        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Diretório '{dir_name}' não encontrado"
            assert dir_path.is_dir(), f"'{dir_name}' não é um diretório"


class TestConfigFiles:
    """Testa arquivos de configuração"""

    def test_config_yaml_exists(self, project_root):
        """config.yaml deve existir"""
        config_file = project_root / "config" / "config.yaml"
        assert config_file.exists(), "config/config.yaml não encontrado"

    def test_models_yaml_exists(self, project_root):
        """models.yaml deve existir"""
        models_file = project_root / "config" / "models.yaml"
        assert models_file.exists(), "config/models.yaml não encontrado"

    def test_env_example_exists(self, project_root):
        """.env.example deve existir"""
        env_file = project_root / ".env.example"
        assert env_file.exists(), ".env.example não encontrado"

    def test_config_yaml_valid(self, project_root):
        """config.yaml deve ser YAML válido"""
        import yaml

        config_file = project_root / "config" / "config.yaml"
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        assert isinstance(config, dict), "config.yaml deve ser um dicionário"
        assert 'general' in config, "config.yaml deve ter seção 'general'"

    def test_models_yaml_valid(self, project_root):
        """models.yaml deve ser YAML válido"""
        import yaml

        models_file = project_root / "config" / "models.yaml"
        with open(models_file, 'r', encoding='utf-8') as f:
            models = yaml.safe_load(f)

        assert isinstance(models, dict), "models.yaml deve ser um dicionário"
        assert 'models' in models, "models.yaml deve ter lista 'models'"
        assert isinstance(models['models'], list), "'models' deve ser uma lista"


class TestWorkflowFiles:
    """Testa arquivos de workflow"""

    def test_basic_workflow_exists(self, project_root):
        """basic_lipsync.json deve existir"""
        workflow = project_root / "workflows" / "basic_lipsync.json"
        assert workflow.exists(), "workflows/basic_lipsync.json não encontrado"

    def test_segmented_workflow_exists(self, project_root):
        """segmented_lipsync.json deve existir"""
        workflow = project_root / "workflows" / "segmented_lipsync.json"
        assert workflow.exists(), "workflows/segmented_lipsync.json não encontrado"

    def test_full_workflow_exists(self, project_root):
        """full_pipeline.json deve existir"""
        workflow = project_root / "workflows" / "full_pipeline.json"
        assert workflow.exists(), "workflows/full_pipeline.json não encontrado"

    def test_workflows_are_valid_json(self, project_root):
        """Workflows devem ser JSON válido"""
        import json

        workflows = [
            "basic_lipsync.json",
            "segmented_lipsync.json",
            "full_pipeline.json"
        ]

        for workflow_name in workflows:
            workflow_path = project_root / "workflows" / workflow_name
            with open(workflow_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            assert isinstance(data, dict), f"{workflow_name} deve ser um objeto JSON"


class TestScripts:
    """Testa scripts"""

    def test_setup_script_exists(self, project_root):
        """setup.py deve existir"""
        setup_script = project_root / "setup.py"
        assert setup_script.exists(), "setup.py não encontrado"

    def test_scripts_directory_has_files(self, project_root):
        """Diretório scripts deve ter arquivos Python"""
        scripts_dir = project_root / "scripts"

        required_scripts = [
            "run_workflow.py",
            "download_models.py",
            "install_nodes.py",
            "validate_setup.py"
        ]

        for script_name in required_scripts:
            script_path = scripts_dir / script_name
            assert script_path.exists(), f"scripts/{script_name} não encontrado"


class TestSourceCode:
    """Testa código fonte"""

    def test_src_has_init(self, project_root):
        """src deve ter __init__.py"""
        init_file = project_root / "src" / "__init__.py"
        assert init_file.exists(), "src/__init__.py não encontrado"

    def test_required_modules_exist(self, project_root):
        """Módulos principais devem existir"""
        required_modules = [
            "logger.py",
            "error_handler.py",
            "model_manager.py",
            "workflow_executor.py"
        ]

        src_dir = project_root / "src"
        for module_name in required_modules:
            module_path = src_dir / module_name
            assert module_path.exists(), f"src/{module_name} não encontrado"


class TestRequirements:
    """Testa requirements"""

    def test_requirements_file_exists(self, project_root):
        """requirements.txt deve existir"""
        req_file = project_root / "requirements.txt"
        assert req_file.exists(), "requirements.txt não encontrado"

    def test_requirements_not_empty(self, project_root):
        """requirements.txt não deve estar vazio"""
        req_file = project_root / "requirements.txt"
        with open(req_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        assert len(content) > 0, "requirements.txt está vazio"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
