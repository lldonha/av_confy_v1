#!/usr/bin/env python3
"""
Script para executar workflows de lipsync

Uso:
    python scripts/run_workflow.py --workflow basic --image portrait.png --text "Olá mundo"
    python scripts/run_workflow.py --workflow segmented --image portrait.png --text-file script.txt
    python scripts/run_workflow.py --help
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Adicionar projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import setup_logging, get_logger
from src.workflow_executor import WorkflowExecutor, ExecutionStatus
from src.error_handler import handle_exception


def main():
    parser = argparse.ArgumentParser(
        description="Executa workflows de lipsync do ComfyUI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--workflow",
        required=True,
        choices=["basic", "segmented", "full"],
        help="Workflow a executar"
    )

    parser.add_argument(
        "--image",
        required=True,
        type=str,
        help="Caminho para imagem de retrato"
    )

    parser.add_argument(
        "--text",
        type=str,
        help="Texto para narração"
    )

    parser.add_argument(
        "--text-file",
        type=str,
        help="Arquivo com texto para narração"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Caminho de saída para o vídeo (opcional)"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Arquivo de configuração"
    )

    parser.add_argument(
        "--comfyui-path",
        type=str,
        default="ComfyUI",
        help="Caminho do ComfyUI"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Habilitar modo debug"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(console_level=log_level)
    logger = get_logger("RunWorkflow")

    logger.info("=" * 80)
    logger.info("LIPSYNC WORKFLOW EXECUTOR")
    logger.info("=" * 80)

    try:
        # Validar inputs
        image_path = Path(args.image)
        if not image_path.exists():
            logger.error(f"Imagem não encontrada: {image_path}")
            return 1

        # Obter texto
        text = args.text
        if args.text_file:
            text_file = Path(args.text_file)
            if not text_file.exists():
                logger.error(f"Arquivo de texto não encontrado: {text_file}")
                return 1
            with open(text_file, 'r', encoding='utf-8') as f:
                text = f.read()

        if not text:
            logger.error("Nenhum texto fornecido (use --text ou --text-file)")
            return 1

        # Determinar workflow
        workflow_map = {
            "basic": "workflows/basic_lipsync.json",
            "segmented": "workflows/segmented_lipsync.json",
            "full": "workflows/full_pipeline.json"
        }
        workflow_path = workflow_map[args.workflow]

        # Criar executor
        logger.info(f"Carregando workflow: {workflow_path}")
        executor = WorkflowExecutor(
            workflow_path=workflow_path,
            config_path=args.config,
            comfyui_path=args.comfyui_path
        )

        # Callback de progresso
        def progress_callback(message, percent):
            logger.info(f"[{percent:3d}%] {message}")

        # Executar
        logger.info(f"Texto: {text[:100]}{'...' if len(text) > 100 else ''}")
        logger.info(f"Imagem: {image_path}")

        result = executor.execute(
            inputs={
                "image": str(image_path),
                "text": text
            },
            progress_callback=progress_callback
        )

        # Resultado
        if result.status == ExecutionStatus.COMPLETED:
            logger.success(f"\n✓ Workflow executado com sucesso!")
            logger.success(f"Duração: {result.duration:.2f}s")
            logger.info(f"\nOutputs:")
            for key, value in result.outputs.items():
                logger.info(f"  • {key}: {value}")

            if result.outputs.get("video_path"):
                logger.success(f"\n✓ Vídeo salvo: {result.outputs['video_path']}")

            return 0

        else:
            logger.error(f"\n✗ Workflow falhou: {result.error}")
            logger.info("\nLogs da execução:")
            for log_line in result.logs:
                logger.info(f"  {log_line}")

            return 1

    except KeyboardInterrupt:
        logger.warning("\n\nExecução cancelada pelo usuário")
        return 130

    except Exception as e:
        logger.error(f"\nErro fatal: {e}")
        handle_exception(e, logger)
        return 1


if __name__ == "__main__":
    sys.exit(main())
