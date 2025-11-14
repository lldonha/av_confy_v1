"""
Sistema de tratamento de erros customizado para Lipsync ComfyUI Workflow

Implementa exceções específicas com:
- Mensagens claras em português
- Contexto detalhado do erro
- Sugestões de correção
- Links para documentação
- Comandos para resolver
"""

from typing import List, Optional, Dict, Any
from pathlib import Path


class LipsyncWorkflowError(Exception):
    """
    Exceção base para todos os erros do Lipsync Workflow

    Attributes:
        message: Mensagem de erro principal
        context: Contexto adicional do erro
        suggestions: Lista de sugestões para correção
        docs_link: Link para documentação relevante
        commands: Comandos para resolver o problema
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        docs_link: Optional[str] = None,
        commands: Optional[List[str]] = None
    ):
        self.message = message
        self.context = context or {}
        self.suggestions = suggestions or []
        self.docs_link = docs_link
        self.commands = commands or []

        # Construir mensagem completa
        full_message = self._build_full_message()
        super().__init__(full_message)

    def _build_full_message(self) -> str:
        """Constrói mensagem de erro formatada"""
        parts = [f"\n{'=' * 80}"]
        parts.append(f"ERRO: {self.message}")
        parts.append('=' * 80)

        # Adicionar contexto
        if self.context:
            parts.append("\nCONTEXTO:")
            for key, value in self.context.items():
                parts.append(f"  • {key}: {value}")

        # Adicionar sugestões
        if self.suggestions:
            parts.append("\nSUGESTÕES DE CORREÇÃO:")
            for i, suggestion in enumerate(self.suggestions, 1):
                parts.append(f"  {i}. {suggestion}")

        # Adicionar comandos
        if self.commands:
            parts.append("\nCOMANDOS PARA RESOLVER:")
            for command in self.commands:
                parts.append(f"  $ {command}")

        # Adicionar link para docs
        if self.docs_link:
            parts.append(f"\nDOCUMENTAÇÃO: {self.docs_link}")

        parts.append('=' * 80 + '\n')

        return '\n'.join(parts)


class ModelNotFoundError(LipsyncWorkflowError):
    """
    Erro quando modelo necessário não está instalado

    Example:
        >>> raise ModelNotFoundError(
        ...     model_name="XTTS v2",
        ...     model_type="TTS",
        ...     expected_path="/ComfyUI/models/xtts/model.pth"
        ... )
    """

    def __init__(
        self,
        model_name: str,
        model_type: str,
        expected_path: Optional[str] = None,
        download_url: Optional[str] = None
    ):
        context = {
            "Modelo": model_name,
            "Tipo": model_type,
        }

        if expected_path:
            context["Caminho esperado"] = expected_path

        suggestions = [
            f"Execute o script de download de modelos",
            f"Baixe manualmente o modelo '{model_name}'",
            "Verifique se o caminho do ComfyUI está correto",
            "Consulte a documentação de instalação"
        ]

        commands = ["python scripts/download_models.py --model " + model_name.lower().replace(" ", "_")]

        if download_url:
            commands.append(f"# Ou baixe manualmente de: {download_url}")

        super().__init__(
            message=f"Modelo '{model_name}' não encontrado",
            context=context,
            suggestions=suggestions,
            docs_link="docs/TROUBLESHOOTING.md#modelo-nao-encontrado",
            commands=commands
        )


class VRAMInsufficientError(LipsyncWorkflowError):
    """
    Erro quando VRAM disponível é insuficiente

    Example:
        >>> raise VRAMInsufficientError(
        ...     required_vram="8GB",
        ...     available_vram="6GB",
        ...     component="LatentSync 1.6"
        ... )
    """

    def __init__(
        self,
        required_vram: str,
        available_vram: str,
        component: str = "Workflow"
    ):
        context = {
            "Componente": component,
            "VRAM necessária": required_vram,
            "VRAM disponível": available_vram
        }

        suggestions = [
            "Use a flag --lowvram ao iniciar o ComfyUI",
            "Feche outros programas que usam a GPU",
            "Reduza a resolução do vídeo nas configurações",
            "Processe o vídeo em segmentos menores",
            "Use um modelo mais leve se disponível",
            "Considere usar CPU (mais lento, mas funciona)"
        ]

        commands = [
            "# Iniciar ComfyUI com baixo uso de VRAM:",
            "python ComfyUI/main.py --lowvram",
            "",
            "# Ou com VRAM muito baixo:",
            "python ComfyUI/main.py --novram"
        ]

        super().__init__(
            message=f"VRAM insuficiente para executar {component}",
            context=context,
            suggestions=suggestions,
            docs_link="docs/TROUBLESHOOTING.md#vram-insuficiente",
            commands=commands
        )


class NodeMissingError(LipsyncWorkflowError):
    """
    Erro quando custom node do ComfyUI não está instalado

    Example:
        >>> raise NodeMissingError(
        ...     node_name="XTTS",
        ...     node_type="custom_nodes",
        ...     install_url="https://github.com/author/ComfyUI-XTTS"
        ... )
    """

    def __init__(
        self,
        node_name: str,
        node_type: str = "custom_nodes",
        install_url: Optional[str] = None,
        expected_path: Optional[str] = None
    ):
        context = {
            "Node": node_name,
            "Tipo": node_type
        }

        if expected_path:
            context["Caminho esperado"] = expected_path

        if install_url:
            context["Repositório"] = install_url

        suggestions = [
            f"Execute o script de instalação de nodes",
            f"Instale manualmente o node '{node_name}'",
            "Reinicie o ComfyUI após a instalação",
            "Verifique se não há erros no console do ComfyUI"
        ]

        commands = ["python scripts/install_nodes.py"]

        if install_url:
            comfyui_path = "ComfyUI"  # Padrão, será substituído em runtime
            commands.append(f"# Ou instale manualmente:")
            commands.append(f"cd {comfyui_path}/custom_nodes")
            commands.append(f"git clone {install_url}")
            commands.append(f"cd {node_name}")
            commands.append("pip install -r requirements.txt")

        super().__init__(
            message=f"Custom node '{node_name}' não encontrado no ComfyUI",
            context=context,
            suggestions=suggestions,
            docs_link="docs/TROUBLESHOOTING.md#node-nao-encontrado",
            commands=commands
        )


class WorkflowValidationError(LipsyncWorkflowError):
    """
    Erro quando workflow JSON é inválido

    Example:
        >>> raise WorkflowValidationError(
        ...     workflow_path="workflows/basic_lipsync.json",
        ...     validation_errors=["Node 5 missing required input", "Invalid connection"],
        ...     line_number=45
        ... )
    """

    def __init__(
        self,
        workflow_path: str,
        validation_errors: List[str],
        line_number: Optional[int] = None
    ):
        context = {
            "Arquivo": workflow_path,
            "Erros encontrados": len(validation_errors)
        }

        if line_number:
            context["Linha"] = line_number

        suggestions = [
            "Verifique a sintaxe JSON do workflow",
            "Certifique-se de que todos os nodes estão instalados",
            "Valide as conexões entre nodes",
            "Use um workflow de exemplo como referência",
            "Abra o workflow no ComfyUI para identificar erros visuais"
        ]

        # Construir lista de erros
        error_list = "\n".join([f"    • {error}" for error in validation_errors])
        full_message = f"Workflow inválido: {workflow_path}\n\n  Erros detectados:\n{error_list}"

        commands = [
            "python scripts/validate_setup.py --workflow " + Path(workflow_path).stem,
            "",
            "# Ou valide manualmente no ComfyUI"
        ]

        super().__init__(
            message=full_message,
            context=context,
            suggestions=suggestions,
            docs_link="docs/WORKFLOW_GUIDE.md#validacao-de-workflows",
            commands=commands
        )


class AudioGenerationError(LipsyncWorkflowError):
    """
    Erro durante geração de áudio com XTTS

    Example:
        >>> raise AudioGenerationError(
        ...     text="Texto muito longo...",
        ...     language="pt",
        ...     error_details="CUDA out of memory"
        ... )
    """

    def __init__(
        self,
        text: str,
        language: str = "pt",
        error_details: Optional[str] = None,
        text_length: Optional[int] = None
    ):
        if text_length is None:
            text_length = len(text)

        context = {
            "Idioma": language,
            "Tamanho do texto": f"{text_length} caracteres",
            "Texto (preview)": text[:100] + "..." if len(text) > 100 else text
        }

        if error_details:
            context["Detalhes do erro"] = error_details

        suggestions = [
            "Reduza o tamanho do texto (max recomendado: 500 caracteres)",
            "Divida o texto em múltiplos segmentos",
            "Verifique se o modelo XTTS está carregado corretamente",
            "Tente reduzir a temperatura da geração",
            "Libere VRAM fechando outros processos"
        ]

        # Sugestões específicas baseadas no erro
        if error_details:
            if "CUDA out of memory" in error_details or "VRAM" in error_details:
                suggestions.insert(0, "Use --lowvram flag no ComfyUI")
            elif "language" in error_details.lower():
                suggestions.insert(0, f"Verifique se o idioma '{language}' é suportado pelo XTTS")

        commands = [
            "# Teste a geração de áudio isoladamente:",
            "python scripts/run_workflow.py --workflow basic --text \"Teste curto\" --debug"
        ]

        super().__init__(
            message="Falha na geração de áudio com XTTS",
            context=context,
            suggestions=suggestions,
            docs_link="docs/TROUBLESHOOTING.md#erro-geracao-audio",
            commands=commands
        )


class LipsyncFailedError(LipsyncWorkflowError):
    """
    Erro durante processamento de lipsync

    Example:
        >>> raise LipsyncFailedError(
        ...     frame_count=180,
        ...     failed_at_frame=120,
        ...     error_details="Face not detected"
        ... )
    """

    def __init__(
        self,
        frame_count: int,
        failed_at_frame: Optional[int] = None,
        error_details: Optional[str] = None,
        image_path: Optional[str] = None
    ):
        context = {
            "Total de frames": frame_count,
        }

        if failed_at_frame:
            context["Falhou no frame"] = failed_at_frame
            context["Progresso"] = f"{(failed_at_frame / frame_count * 100):.1f}%"

        if error_details:
            context["Detalhes do erro"] = error_details

        if image_path:
            context["Imagem de entrada"] = image_path

        suggestions = [
            "Verifique se a imagem contém um rosto visível",
            "Use uma imagem de retrato frontal com boa iluminação",
            "Certifique-se de que a imagem está no formato correto (PNG/JPG)",
            "Tente com resolução diferente (recomendado: 512x512)",
            "Verifique se o modelo LatentSync está carregado corretamente"
        ]

        # Sugestões específicas baseadas no erro
        if error_details:
            if "face" in error_details.lower() or "detect" in error_details.lower():
                suggestions.insert(0, "A detecção de rosto falhou - use imagem com rosto mais visível")
            elif "resolution" in error_details.lower():
                suggestions.insert(0, "Ajuste a resolução da imagem (múltiplo de 64 pixels)")

        commands = [
            "# Teste o lipsync com imagem de exemplo:",
            "python scripts/run_workflow.py --workflow basic --image assets/test_portrait.png --debug"
        ]

        super().__init__(
            message="Falha no processamento de lipsync",
            context=context,
            suggestions=suggestions,
            docs_link="docs/TROUBLESHOOTING.md#erro-lipsync",
            commands=commands
        )


class DependencyError(LipsyncWorkflowError):
    """
    Erro quando dependência Python está faltando ou é incompatível

    Example:
        >>> raise DependencyError(
        ...     package_name="torch",
        ...     required_version="2.0.0",
        ...     current_version="1.13.0"
        ... )
    """

    def __init__(
        self,
        package_name: str,
        required_version: Optional[str] = None,
        current_version: Optional[str] = None,
        install_command: Optional[str] = None
    ):
        context = {
            "Pacote": package_name,
        }

        if required_version:
            context["Versão necessária"] = required_version

        if current_version:
            context["Versão atual"] = current_version
        else:
            context["Status"] = "Não instalado"

        suggestions = [
            f"Instale o pacote '{package_name}'",
            "Execute pip install -r requirements.txt",
            "Use um ambiente virtual Python limpo",
            "Verifique conflitos de dependências"
        ]

        if current_version and required_version:
            suggestions.insert(0, f"Atualize {package_name} para versão {required_version} ou superior")

        commands = []
        if install_command:
            commands.append(install_command)
        else:
            if required_version:
                commands.append(f"pip install {package_name}>={required_version}")
            else:
                commands.append(f"pip install {package_name}")

        commands.append("# Ou reinstale todas as dependências:")
        commands.append("pip install -r requirements.txt")

        super().__init__(
            message=f"Dependência '{package_name}' não encontrada ou incompatível",
            context=context,
            suggestions=suggestions,
            docs_link="docs/INSTALL.md#dependencias",
            commands=commands
        )


class ConfigurationError(LipsyncWorkflowError):
    """
    Erro de configuração inválida

    Example:
        >>> raise ConfigurationError(
        ...     config_file="config/config.yaml",
        ...     invalid_keys=["output_fps", "temperature"],
        ...     details="FPS deve ser entre 24-60"
        ... )
    """

    def __init__(
        self,
        config_file: str,
        invalid_keys: Optional[List[str]] = None,
        details: Optional[str] = None
    ):
        context = {
            "Arquivo de configuração": config_file,
        }

        if invalid_keys:
            context["Chaves inválidas"] = ", ".join(invalid_keys)

        if details:
            context["Detalhes"] = details

        suggestions = [
            "Verifique a sintaxe YAML do arquivo de configuração",
            "Compare com o arquivo .env.example",
            "Certifique-se de usar valores válidos para cada parâmetro",
            "Consulte a documentação de configuração"
        ]

        commands = [
            f"# Valide o arquivo de configuração:",
            "python scripts/validate_setup.py --config",
            "",
            f"# Ou use configuração padrão:",
            f"cp config/config.yaml.example {config_file}"
        ]

        super().__init__(
            message=f"Configuração inválida em {config_file}",
            context=context,
            suggestions=suggestions,
            docs_link="docs/API.md#configuracao",
            commands=commands
        )


class ComfyUINotFoundError(LipsyncWorkflowError):
    """
    Erro quando ComfyUI não é encontrado

    Example:
        >>> raise ComfyUINotFoundError(
        ...     searched_paths=["/ComfyUI", "/home/user/ComfyUI"]
        ... )
    """

    def __init__(
        self,
        searched_paths: Optional[List[str]] = None,
        expected_structure: Optional[List[str]] = None
    ):
        context = {}

        if searched_paths:
            context["Caminhos verificados"] = ", ".join(searched_paths)

        suggestions = [
            "Instale o ComfyUI antes de continuar",
            "Especifique o caminho correto do ComfyUI",
            "Use a flag --comfyui-path durante a instalação",
            "Certifique-se de que o ComfyUI está completo e funcional"
        ]

        commands = [
            "# Instalar ComfyUI:",
            "git clone https://github.com/comfyanonymous/ComfyUI",
            "cd ComfyUI",
            "pip install -r requirements.txt",
            "",
            "# Depois execute setup apontando para o caminho:",
            "python setup.py --comfyui-path /caminho/para/ComfyUI"
        ]

        super().__init__(
            message="ComfyUI não encontrado no sistema",
            context=context,
            suggestions=suggestions,
            docs_link="docs/INSTALL.md#instalando-comfyui",
            commands=commands
        )


def handle_exception(error: Exception, logger=None) -> None:
    """
    Handler global para exceções
    Formata e loga erros adequadamente

    Args:
        error: Exceção capturada
        logger: Logger opcional para registrar o erro

    Example:
        >>> try:
        ...     # código que pode falhar
        ...     pass
        ... except Exception as e:
        ...     handle_exception(e, logger)
        ...     raise
    """
    if logger:
        if isinstance(error, LipsyncWorkflowError):
            logger.error(str(error))
        else:
            logger.error(f"Erro inesperado: {type(error).__name__}: {str(error)}")


if __name__ == "__main__":
    # Testes das exceções
    print("\n=== TESTE 1: ModelNotFoundError ===")
    try:
        raise ModelNotFoundError(
            model_name="XTTS v2",
            model_type="TTS",
            expected_path="/ComfyUI/models/xtts/model.pth",
            download_url="https://example.com/model"
        )
    except LipsyncWorkflowError as e:
        print(e)

    print("\n=== TESTE 2: VRAMInsufficientError ===")
    try:
        raise VRAMInsufficientError(
            required_vram="8GB",
            available_vram="6GB",
            component="LatentSync 1.6"
        )
    except LipsyncWorkflowError as e:
        print(e)

    print("\n=== TESTE 3: AudioGenerationError ===")
    try:
        raise AudioGenerationError(
            text="Este é um texto de teste muito longo que excede o limite recomendado...",
            language="pt",
            error_details="CUDA out of memory"
        )
    except LipsyncWorkflowError as e:
        print(e)
