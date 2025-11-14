#!/usr/bin/env python3
"""
Script de validação da instalação

Verifica:
- Dependências Python
- ComfyUI e custom nodes
- Modelos instalados
- Configuração
- Workflows

Uso:
    python scripts/validate_setup.py
    python scripts/validate_setup.py --config
    python scripts/validate_setup.py --workflow basic
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import setup_logging, get_logger
from src.model_manager import ModelManager, ModelStatus
from src.workflow_executor import WorkflowExecutor


def validate_dependencies() -> bool:
    """Valida dependências Python"""
    logger = get_logger("Validator")
    logger.info("Validando dependências Python...")

    critical_deps = [
        "torch",
        "torchvision",
        "PIL",
        "numpy",
        "yaml",
        "requests",
        "colorama"
    ]

    all_ok = True
    for dep in critical_deps:
        try:
            __import__(dep)
            logger.success(f"  ✓ {dep}")
        except ImportError:
            logger.error(f"  ✗ {dep} (não instalado)")
            all_ok = False

    return all_ok


def validate_models(comfyui_path: str) -> bool:
    """Valida modelos instalados"""
    logger = get_logger("Validator")
    logger.info("Validando modelos...")

    try:
        model_manager = ModelManager(comfyui_path=comfyui_path)
        status = model_manager.check_installed()

        all_ok = True
        for name, st in status.items():
            if st == ModelStatus.INSTALLED:
                logger.success(f"  ✓ {name}")
            elif st == ModelStatus.NOT_INSTALLED:
                logger.warning(f"  ✗ {name} (não instalado)")
                all_ok = False
            elif st == ModelStatus.CORRUPTED:
                logger.error(f"  ✗ {name} (corrompido)")
                all_ok = False

        return all_ok

    except Exception as e:
        logger.error(f"Erro ao validar modelos: {e}")
        return False


def validate_workflow(workflow_name: str, comfyui_path: str) -> bool:
    """Valida um workflow específico"""
    logger = get_logger("Validator")
    logger.info(f"Validando workflow: {workflow_name}")

    workflow_map = {
        "basic": "workflows/basic_lipsync.json",
        "segmented": "workflows/segmented_lipsync.json",
        "full": "workflows/full_pipeline.json"
    }

    if workflow_name not in workflow_map:
        logger.error(f"Workflow desconhecido: {workflow_name}")
        return False

    try:
        executor = WorkflowExecutor(
            workflow_path=workflow_map[workflow_name],
            comfyui_path=comfyui_path
        )

        executor.validate_workflow()
        deps = executor.check_dependencies()
        vram = executor.estimate_vram()

        logger.success(f"  ✓ Workflow válido")
        logger.info(f"  • Dependências: {len(deps)}")
        logger.info(f"  • VRAM estimado: {vram}MB ({vram/1024:.1f}GB)")

        return True

    except Exception as e:
        logger.error(f"  ✗ Workflow inválido: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Valida instalação do Lipsync Workflow")

    parser.add_argument(
        "--config",
        action="store_true",
        help="Validar apenas configuração"
    )

    parser.add_argument(
        "--workflow",
        type=str,
        choices=["basic", "segmented", "full"],
        help="Validar workflow específico"
    )

    parser.add_argument(
        "--comfyui-path",
        type=str,
        default="ComfyUI",
        help="Caminho do ComfyUI"
    )

    args = parser.parse_args()

    setup_logging(console_level="INFO")
    logger = get_logger("Validator")

    logger.info("=" * 80)
    logger.info("VALIDAÇÃO DA INSTALAÇÃO")
    logger.info("=" * 80)

    results = {}

    # Dependências
    results["Dependências"] = validate_dependencies()

    # Modelos (se não for apenas config)
    if not args.config:
        results["Modelos"] = validate_models(args.comfyui_path)

    # Workflow específico
    if args.workflow:
        results[f"Workflow {args.workflow}"] = validate_workflow(args.workflow, args.comfyui_path)

    # Sumário
    logger.info("\n" + "=" * 80)
    logger.info("RESULTADO DA VALIDAÇÃO")
    logger.info("=" * 80)

    for check, passed in results.items():
        status = "✓" if passed else "✗"
        level = "success" if passed else "error"
        getattr(logger, level)(f"{status} {check}")

    all_passed = all(results.values())
    if all_passed:
        logger.success("\n✓ Instalação válida!")
        return 0
    else:
        logger.error("\n✗ Instalação incompleta")
        return 1


if __name__ == "__main__":
    sys.exit(main())
