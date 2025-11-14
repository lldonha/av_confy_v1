# Assets de Teste

Este diretório deve conter assets de teste para validar o funcionamento dos workflows.

## Arquivos Necessários

### test_portrait.png

Imagem de retrato frontal para testes de lipsync.

**Requisitos:**
- Formato: PNG ou JPG
- Resolução mínima: 512x512
- Rosto frontal visível
- Boa iluminação
- Fundo preferencialmente uniforme

**Onde encontrar:**
- Use uma foto sua ou de alguém com permissão
- Gere uma com Stable Diffusion
- Use imagens de stock (verificar licença)

### test_audio.wav

Arquivo de áudio de teste (opcional, normalmente gerado pelo XTTS).

**Requisitos:**
- Formato: WAV
- Taxa de amostragem: 24kHz recomendado
- Duração: 5-15 segundos

## Adicionando Seus Assets

```bash
# Copie sua imagem de teste
cp /caminho/para/sua/imagem.png assets/test_portrait.png

# Copie seu áudio de teste (opcional)
cp /caminho/para/seu/audio.wav assets/test_audio.wav
```

## Gerando Imagem de Teste com Stable Diffusion

Se você tem ComfyUI instalado:

1. Abra ComfyUI
2. Use este prompt:
   ```
   portrait of a person, frontal view, neutral expression,
   studio lighting, plain background, photorealistic, high quality
   ```
3. Gere a imagem
4. Salve como `assets/test_portrait.png`

## Nota sobre Copyright

**IMPORTANTE**: Certifique-se de que você tem os direitos de uso das imagens e áudios que adicionar aqui. Não adicione conteúdo protegido por direitos autorais sem permissão.

## Gitignore

Por padrão, arquivos de imagem e áudio neste diretório são ignorados pelo Git (veja `.gitignore`). Isto evita commitar arquivos grandes e potencialmente protegidos por copyright.

Se você quiser commitar seus assets de teste:

```bash
git add -f assets/test_portrait.png
git add -f assets/test_audio.wav
```

## Exemplos de Uso

Após adicionar seus assets:

```bash
# Teste básico
python scripts/run_workflow.py \
    --workflow basic \
    --image assets/test_portrait.png \
    --text "Teste de lipsync funcionando perfeitamente"

# Validação
python scripts/validate_setup.py
```

---

**Dica**: Para primeiros testes, você pode usar qualquer imagem de retrato. A qualidade do lipsync depende da qualidade da imagem de entrada.
