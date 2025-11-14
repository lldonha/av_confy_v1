#!/usr/bin/env python3
"""
Script de instalação de custom nodes do ComfyUI

Uso:
    python scripts/install_nodes.py                 # Instala todos
    python scripts/install_nodes.py --list          # Lista nodes necessários
    python scripts/install_nodes.py --node xtts     # Instala node específico
"""

import argparse
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logger import setup_logging, get_logger


# Configuração dos custom nodes necessários
CUSTOM_NODES = {
    "ComfyUI-XTTS": {
        "url": "https://github.com/YOUR_REPO/ComfyUI-XTTS.git",
        "description": "Text-to-Speech usando XTTS v2",
        "required": True
    },
    "ComfyUI-LatentSync": {
        "url": "https://github.com/YOUR_REPO/ComfyUI-LatentSync.git",
        "description": "Lipsync de alta qualidade com LatentSync 1.6",
        "required": True
    },
    "ComfyUI-VideoHelperSuite": {
        "url": "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git",
        "description": "Ferramentas para processamento de vídeo",
        "required": True
    },
    "ComfyUI-Advanced-ControlNet": {
        "url": "https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git",
        "description": "ControlNet avançado (opcional)",
        "required": False
    }
}


def install_node(node_name: str, node_info: dict, comfyui_path: Path, logger) -> bool:
    """Instala um custom node específico"""

    custom_nodes_dir = comfyui_path / "custom_nodes"
    node_path = custom_nodes_dir / node_name

    logger.info(f"\nInstalando {node_name}...")
    logger.info(f"  URL: {node_info['url']}")

    # Verificar se já existe
    if node_path.exists():
        logger.warning(f"  Node já instalado em {node_path}")

        # Perguntar se quer atualizar
        response = input("  Atualizar? (s/n): ").lower()
        if response == 's':
            logger.info("  Atualizando...")
            try:
                subprocess.run(
                    ["git", "pull"],
                    cwd=node_path,
                    check=True,
                    capture_output=True
                )
                logger.success("  ✓ Atualizado")
            except subprocess.CalledProcessError as e:
                logger.error(f"  ✗ Erro ao atualizar: {e}")
                return False
        return True

    # Clonar repositório
    try:
        logger.info("  Clonando repositório...")
        subprocess.run(
            ["git", "clone", node_info["url"], str(node_path)],
            check=True,
            capture_output=True,
            text=True
        )
        logger.success("  ✓ Repositório clonado")

    except subprocess.CalledProcessError as e:
        logger.error(f"  ✗ Erro ao clonar: {e.stderr}")
        return False

    # Instalar requirements
    requirements_file = node_path / "requirements.txt"
    if requirements_file.exists():
        logger.info("  Instalando dependências...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                check=True,
                capture_output=True,
                text=True
            )
            logger.success("  ✓ Dependências instaladas")

        except subprocess.CalledProcessError as e:
            logger.warning(f"  ⚠ Erro ao instalar dependências: {e.stderr}")
            # Não falhar se as dependências falharem
    else:
        logger.info("  Sem requirements.txt")

    logger.success(f"✓ {node_name} instalado com sucesso")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Instalação de custom nodes do ComfyUI"
    )

    parser.add_argument(
        "--node",
        type=str,
        help="Instalar node específico"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar nodes disponíveis"
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
    logger = get_logger("NodeInstaller")

    logger.info("=" * 80)
    logger.info("INSTALAÇÃO DE CUSTOM NODES")
    logger.info("=" * 80)

    comfyui_path = Path(args.comfyui_path)

    # Validar ComfyUI
    if not comfyui_path.exists():
        logger.error(f"ComfyUI não encontrado em: {comfyui_path}")
        return 1

    custom_nodes_dir = comfyui_path / "custom_nodes"
    custom_nodes_dir.mkdir(parents=True, exist_ok=True)

    # Listar nodes
    if args.list:
        logger.info("\nCustom nodes disponíveis:\n")
        for name, info in CUSTOM_NODES.items():
            required = "OBRIGATÓRIO" if info["required"] else "OPCIONAL"
            logger.info(f"• {name} [{required}]")
            logger.info(f"  {info['description']}")
            logger.info(f"  {info['url']}\n")
        return 0

    # Instalar node específico
    if args.node:
        node_name = args.node

        # Procurar node (case insensitive)
        found_node = None
        for name in CUSTOM_NODES:
            if node_name.lower() in name.lower():
                found_node = name
                break

        if not found_node:
            logger.error(f"Node não encontrado: {node_name}")
            logger.info("Use --list para ver nodes disponíveis")
            return 1

        success = install_node(
            found_node,
            CUSTOM_NODES[found_node],
            comfyui_path,
            logger
        )

        return 0 if success else 1

    # Instalar todos os nodes
    else:
        logger.info("\nInstalando todos os custom nodes...\n")

        successes = 0
        failures = 0

        for node_name, node_info in CUSTOM_NODES.items():
            try:
                if install_node(node_name, node_info, comfyui_path, logger):
                    successes += 1
                else:
                    failures += 1
                    if node_info["required"]:
                        logger.error(f"Node obrigatório falhou: {node_name}")

            except Exception as e:
                logger.error(f"Erro ao instalar {node_name}: {e}")
                failures += 1

        # Sumário
        logger.info("\n" + "=" * 80)
        logger.info(f"Resultado: {successes} instalados, {failures} falhas")
        logger.info("=" * 80)

        if failures == 0:
            logger.success("\n✓ Todos os nodes instalados!")
            logger.info("\nReinicie o ComfyUI para carregar os novos nodes")
            return 0
        else:
            logger.warning(f"\n⚠ Alguns nodes falharam ({failures})")
            return 1


if __name__ == "__main__":
    sys.exit(main())
