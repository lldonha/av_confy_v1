#!/usr/bin/env python3
"""
Script de download de modelos

Uso:
    python scripts/download_models.py                    # Baixa todos
    python scripts/download_models.py --model xtts_v2    # Modelo específico
    python scripts/download_models.py --force            # Forçar redownload
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import setup_logging, get_logger
from src.model_manager import ModelManager


def main():
    parser = argparse.ArgumentParser(description="Download de modelos para Lipsync Workflow")

    parser.add_argument(
        "--model",
        type=str,
        help="Baixar modelo específico"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar modelos disponíveis"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Forçar download mesmo se já existir"
    )

    parser.add_argument(
        "--comfyui-path",
        type=str,
        default="ComfyUI",
        help="Caminho do ComfyUI"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Logs detalhados"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(console_level=log_level)
    logger = get_logger("ModelDownloader")

    logger.info("=" * 80)
    logger.info("DOWNLOAD DE MODELOS")
    logger.info("=" * 80)

    try:
        model_manager = ModelManager(comfyui_path=args.comfyui_path)

        # Listar modelos
        if args.list:
            logger.info("\nModelos disponíveis:")
            for model in model_manager.list_required():
                logger.info(f"\n• {model.name}")
                logger.info(f"  Tipo: {model.type}")
                logger.info(f"  Tamanho: {model.size / (1024**3):.2f}GB")
                if model.description:
                    logger.info(f"  Descrição: {model.description}")
            return 0

        # Progress callback
        def progress(current, total, message):
            if total > 0:
                percent = (current / total) * 100
                logger.info(f"[{percent:5.1f}%] {message}")

        # Download específico
        if args.model:
            logger.info(f"\nBaixando modelo: {args.model}")
            success = model_manager.download_model(
                args.model,
                progress_callback=progress,
                force=args.force
            )

            if success:
                logger.success(f"\n✓ Modelo baixado: {args.model}")
                return 0
            else:
                logger.error(f"\n✗ Falha ao baixar: {args.model}")
                return 1

        # Download de todos
        else:
            logger.info("\nBaixando todos os modelos...")
            successes, failures = model_manager.download_all(
                progress_callback=progress,
                skip_existing=not args.force
            )

            logger.info(f"\nResultado: {successes} sucessos, {failures} falhas")

            if failures == 0:
                logger.success("\n✓ Todos os modelos baixados!")
                return 0
            else:
                logger.warning(f"\n⚠ Alguns modelos falharam ({failures})")
                return 1

    except Exception as e:
        logger.error(f"\nErro: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
