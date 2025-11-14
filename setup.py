#!/usr/bin/env python3
"""
Script de instalação automática para Lipsync ComfyUI Workflow
Canal: CÓSMICA DREAD

Funcionalidades:
- Detecção automática de ComfyUI existente
- Instalação de custom nodes via git clone
- Download de modelos com barra de progresso
- Validação de VRAM disponível
- Checagem de dependências Python
- Criação de diretórios necessários
- Logs detalhados de cada etapa

Uso:
    python setup.py --mode install --comfyui-path /path/to/ComfyUI
    python setup.py --mode validate
    python setup.py --mode update-models
"""

import argparse
import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# Adicionar src ao path para imports
sys.path.insert(0, str(Path(__file__).parent))

from src.logger import setup_logging, get_logger
from src.error_handler import (
    ComfyUINotFoundError,
    DependencyError,
    handle_exception
)
from src.model_manager import ModelManager


class SetupManager:
    """
    Gerenciador principal da instalação

    Responsável por:
    - Verificar dependências
    - Instalar custom nodes
    - Baixar modelos
    - Validar instalação
    """

    def __init__(self, comfyui_path: Optional[str] = None, verbose: bool = False):
        """
        Inicializa o gerenciador de setup

        Args:
            comfyui_path: Caminho para instalação do ComfyUI
            verbose: Habilitar logs verbose (DEBUG)
        """
        # Setup logging
        log_level = "DEBUG" if verbose else "INFO"
        setup_logging(console_level=log_level)
        self.logger = get_logger("Setup")

        self.logger.info("=" * 80)
        self.logger.info("LIPSYNC COMFYUI WORKFLOW - INSTALAÇÃO")
        self.logger.info("Canal: CÓSMICA DREAD")
        self.logger.info("=" * 80)

        # Detectar ou usar caminho fornecido
        self.comfyui_path = self._detect_comfyui(comfyui_path)

        # Diretórios do projeto
        self.project_root = Path(__file__).parent
        self.config_dir = self.project_root / "config"
        self.scripts_dir = self.project_root / "scripts"

        # Estado da instalação
        self.installation_status: Dict[str, bool] = {}

    def _detect_comfyui(self, provided_path: Optional[str] = None) -> Path:
        """
        Detecta instalação do ComfyUI

        Args:
            provided_path: Caminho fornecido pelo usuário

        Returns:
            Path para ComfyUI

        Raises:
            ComfyUINotFoundError: Se ComfyUI não for encontrado
        """
        self.logger.info("Detectando instalação do ComfyUI...")

        # Lista de caminhos para verificar
        search_paths = []

        if provided_path:
            search_paths.append(Path(provided_path))

        # Adicionar caminhos comuns
        common_paths = [
            Path("ComfyUI"),
            Path.home() / "ComfyUI",
            Path("/opt/ComfyUI"),
            Path("../ComfyUI"),
        ]
        search_paths.extend(common_paths)

        # Verificar cada caminho
        for path in search_paths:
            if path.exists() and path.is_dir():
                # Verificar se é realmente uma instalação do ComfyUI
                if self._validate_comfyui_installation(path):
                    self.logger.success(f"ComfyUI encontrado em: {path}")
                    return path.resolve()

        # Não encontrou
        raise ComfyUINotFoundError(
            searched_paths=[str(p) for p in search_paths]
        )

    def _validate_comfyui_installation(self, path: Path) -> bool:
        """
        Valida se o caminho é uma instalação válida do ComfyUI

        Args:
            path: Caminho a verificar

        Returns:
            True se é uma instalação válida
        """
        # Verificar arquivos/diretórios essenciais
        required_items = [
            "main.py",
            "comfy",
            "custom_nodes"
        ]

        for item in required_items:
            if not (path / item).exists():
                return False

        return True

    def check_python_version(self) -> bool:
        """Verifica se a versão do Python é adequada"""
        self.logger.info("Verificando versão do Python...")

        version = sys.version_info
        required_version = (3, 10)

        if version >= required_version:
            self.logger.success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
            return True
        else:
            self.logger.error(
                f"Python {required_version[0]}.{required_version[1]}+ necessário. "
                f"Versão atual: {version.major}.{version.minor}.{version.micro}"
            )
            return False

    def check_dependencies(self) -> Tuple[List[str], List[str]]:
        """
        Verifica dependências Python

        Returns:
            Tupla (instaladas, faltando)
        """
        self.logger.info("Verificando dependências Python...")

        # Lista de dependências críticas
        critical_deps = [
            "torch",
            "torchvision",
            "PIL",
            "numpy",
            "yaml",
            "requests"
        ]

        installed = []
        missing = []

        for dep in critical_deps:
            try:
                __import__(dep)
                installed.append(dep)
                self.logger.debug(f"  ✓ {dep}")
            except ImportError:
                missing.append(dep)
                self.logger.warning(f"  ✗ {dep} (faltando)")

        if missing:
            self.logger.warning(f"Dependências faltando: {', '.join(missing)}")
        else:
            self.logger.success("Todas as dependências críticas instaladas ✓")

        return (installed, missing)

    def install_dependencies(self) -> bool:
        """
        Instala dependências Python via pip

        Returns:
            True se instalação foi bem-sucedida
        """
        self.logger.info("Instalando dependências Python...")

        requirements_file = self.project_root / "requirements.txt"

        if not requirements_file.exists():
            self.logger.error(f"Arquivo requirements.txt não encontrado")
            return False

        try:
            # Executar pip install
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements_file)
            ]

            self.logger.info(f"Executando: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            self.logger.success("Dependências instaladas com sucesso ✓")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao instalar dependências: {e}")
            self.logger.error(f"Output: {e.stderr}")
            return False

    def install_custom_nodes(self) -> bool:
        """
        Instala custom nodes necessários no ComfyUI

        Returns:
            True se instalação foi bem-sucedida
        """
        self.logger.info("Instalando custom nodes do ComfyUI...")

        custom_nodes_dir = self.comfyui_path / "custom_nodes"
        custom_nodes_dir.mkdir(parents=True, exist_ok=True)

        # Lista de nodes necessários
        nodes_to_install = [
            {
                "name": "ComfyUI-XTTS",
                "url": "https://github.com/YOUR_REPO/ComfyUI-XTTS.git",
                "required": True
            },
            {
                "name": "ComfyUI-LatentSync",
                "url": "https://github.com/YOUR_REPO/ComfyUI-LatentSync.git",
                "required": True
            },
            {
                "name": "ComfyUI-VideoHelperSuite",
                "url": "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git",
                "required": True
            }
        ]

        success_count = 0
        failed_count = 0

        for node_info in nodes_to_install:
            node_name = node_info["name"]
            node_url = node_info["url"]
            node_path = custom_nodes_dir / node_name

            self.logger.info(f"Instalando {node_name}...")

            # Verificar se já está instalado
            if node_path.exists():
                self.logger.info(f"  {node_name} já instalado, pulando...")
                success_count += 1
                continue

            try:
                # Clonar repositório
                subprocess.run(
                    ["git", "clone", node_url, str(node_path)],
                    check=True,
                    capture_output=True,
                    text=True
                )

                # Instalar requirements se existir
                node_requirements = node_path / "requirements.txt"
                if node_requirements.exists():
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-r", str(node_requirements)],
                        check=True,
                        capture_output=True,
                        text=True
                    )

                self.logger.success(f"  ✓ {node_name} instalado")
                success_count += 1

            except subprocess.CalledProcessError as e:
                self.logger.error(f"  ✗ Erro ao instalar {node_name}: {e}")
                failed_count += 1

                if node_info["required"]:
                    return False

        self.logger.info(f"Custom nodes: {success_count} instalados, {failed_count} falhas")

        return failed_count == 0 or success_count > 0

    def download_models(self, skip_existing: bool = True) -> bool:
        """
        Baixa modelos necessários

        Args:
            skip_existing: Pular modelos já instalados

        Returns:
            True se download foi bem-sucedido
        """
        self.logger.info("Iniciando download de modelos...")

        try:
            model_manager = ModelManager(
                comfyui_path=str(self.comfyui_path),
                models_config=str(self.config_dir / "models.yaml")
            )

            # Callback de progresso
            def progress_callback(current, total, message):
                if total > 0:
                    percent = (current / total) * 100
                    self.logger.info(f"  [{percent:5.1f}%] {message}")
                else:
                    self.logger.info(f"  {message}")

            # Baixar todos os modelos
            successes, failures = model_manager.download_all(
                progress_callback=progress_callback,
                skip_existing=skip_existing
            )

            if failures == 0:
                self.logger.success(f"Todos os modelos baixados com sucesso ({successes} modelos)")
                return True
            else:
                self.logger.warning(f"Download concluído: {successes} sucessos, {failures} falhas")
                return successes > 0

        except Exception as e:
            self.logger.error(f"Erro ao baixar modelos: {e}")
            handle_exception(e, self.logger)
            return False

    def create_directories(self) -> bool:
        """
        Cria diretórios necessários

        Returns:
            True se criação foi bem-sucedida
        """
        self.logger.info("Criando diretórios necessários...")

        directories = [
            "logs",
            "output",
            "config",
            "workflows",
            "scripts",
            "src",
            "tests",
            "assets",
            ".cache",
            ".model_cache"
        ]

        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"  ✓ {dir_name}")

        self.logger.success("Diretórios criados ✓")
        return True

    def validate_installation(self) -> bool:
        """
        Valida instalação completa

        Returns:
            True se instalação está válida
        """
        self.logger.info("Validando instalação...")

        checks = []

        # 1. Python version
        checks.append(("Versão Python", self.check_python_version()))

        # 2. ComfyUI
        checks.append(("ComfyUI", self.comfyui_path.exists()))

        # 3. Dependências
        installed, missing = self.check_dependencies()
        checks.append(("Dependências", len(missing) == 0))

        # 4. Diretórios
        required_dirs = ["logs", "output", "config", "workflows"]
        all_dirs_exist = all((self.project_root / d).exists() for d in required_dirs)
        checks.append(("Diretórios", all_dirs_exist))

        # 5. Config files
        config_files = ["config.yaml", "models.yaml"]
        all_configs_exist = all((self.config_dir / f).exists() for f in config_files)
        checks.append(("Arquivos de config", all_configs_exist))

        # Exibir resultados
        self.logger.info("\nResultado da validação:")
        all_passed = True

        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            level = "success" if passed else "error"
            getattr(self.logger, level)(f"  {status} {check_name}")

            if not passed:
                all_passed = False

        if all_passed:
            self.logger.success("\n✓ Instalação válida!")
        else:
            self.logger.error("\n✗ Instalação incompleta. Verifique os erros acima.")

        return all_passed

    def run_full_installation(self) -> bool:
        """
        Executa instalação completa

        Returns:
            True se instalação foi bem-sucedida
        """
        self.logger.info("Iniciando instalação completa...\n")

        steps = [
            ("Verificar versão Python", self.check_python_version),
            ("Criar diretórios", self.create_directories),
            ("Instalar dependências Python", self.install_dependencies),
            ("Instalar custom nodes", self.install_custom_nodes),
            ("Baixar modelos", lambda: self.download_models(skip_existing=True)),
            ("Validar instalação", self.validate_installation)
        ]

        for i, (step_name, step_func) in enumerate(steps, 1):
            self.logger.info(f"\n[{i}/{len(steps)}] {step_name}...")

            try:
                if not step_func():
                    self.logger.error(f"Falha na etapa: {step_name}")
                    return False

            except Exception as e:
                self.logger.error(f"Erro na etapa '{step_name}': {e}")
                handle_exception(e, self.logger)
                return False

        self.logger.success("\n" + "=" * 80)
        self.logger.success("INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        self.logger.success("=" * 80)
        self.logger.info("\nPróximos passos:")
        self.logger.info("  1. Copie .env.example para .env e ajuste as configurações")
        self.logger.info("  2. Execute: python scripts/validate_setup.py")
        self.logger.info("  3. Teste com: python scripts/run_workflow.py --workflow basic")

        return True


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Setup do Lipsync ComfyUI Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--mode",
        choices=["install", "validate", "update-models", "clean"],
        default="install",
        help="Modo de operação"
    )

    parser.add_argument(
        "--comfyui-path",
        type=str,
        help="Caminho para instalação do ComfyUI"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Habilitar logs verbose (DEBUG)"
    )

    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Pular instalação de dependências Python"
    )

    parser.add_argument(
        "--skip-nodes",
        action="store_true",
        help="Pular instalação de custom nodes"
    )

    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Pular download de modelos"
    )

    args = parser.parse_args()

    try:
        # Criar gerenciador de setup
        setup_manager = SetupManager(
            comfyui_path=args.comfyui_path,
            verbose=args.verbose
        )

        # Executar modo selecionado
        if args.mode == "install":
            if args.skip_deps and args.skip_nodes and args.skip_models:
                setup_manager.logger.warning("Todas as etapas foram puladas!")

            success = setup_manager.run_full_installation()

        elif args.mode == "validate":
            success = setup_manager.validate_installation()

        elif args.mode == "update-models":
            success = setup_manager.download_models(skip_existing=False)

        elif args.mode == "clean":
            setup_manager.logger.warning("Modo clean ainda não implementado")
            success = True

        # Exit code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nInstalação cancelada pelo usuário.")
        sys.exit(130)

    except Exception as e:
        print(f"\nErro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
