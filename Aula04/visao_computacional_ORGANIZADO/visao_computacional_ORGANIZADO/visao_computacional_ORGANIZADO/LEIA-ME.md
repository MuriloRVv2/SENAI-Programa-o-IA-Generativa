# 👁️ Curso de Visão Computacional — Códigos organizados por dificuldade

Todos os exemplos da aula, agrupados em **3 níveis**. Cada pasta já tem o
`util_ambiente.py` (o "adaptador universal" que faz o código rodar tanto no
**Google Colab** quanto no **PyCharm/VSCode**).

> ⚙️ **Antes de tudo:** instale as bibliotecas com `pip install -r requirements.txt`
> (ou, no Colab, `!pip install opencv-python-headless ultralytics face_recognition SpeechRecognition`).

---

## 🟢 01_FACIL — Primeiros passos (a imagem é uma tabela de números)

| Arquivo | O que ensina | Tecnologia |
|--------|--------------|-----------|
| `01_primeira_imagem.py` | Abrir, mostrar, preto e branco, redimensionar | OpenCV |
| `02_deteccao_rosto_haar.py` | **Detectar** rostos (Haar Cascade) | OpenCV |
| `03_filtros_desenhos.py` | Filtros (borrar, bordas, negativo) e desenhos | OpenCV |
| `04_opencv_edicao_de_fotos.py` | Brilho, contraste, girar, espelhar, recortar | OpenCV |
| `05_stt_fala_virou_texto.py` | Transcrição básica de voz | STT |

## 🟡 02_INTERMEDIARIO — Começa a ficar esperto

| Arquivo | O que ensina | Tecnologia |
|--------|--------------|-----------|
| `01_reconhecimento_facial.py` | **Reconhecer** de quem é o rosto | face_recognition |
| `02_deteccao_cor_e_movimento.py` | Perseguir objeto por cor + detectar movimento | OpenCV |
| `03_stt_comando_de_voz.py` | Falar "foto" e a câmera obedecer | STT + OpenCV |
| `04_opencv_contar_objetos.py` | Contar objetos numa foto (limiar + contornos) | OpenCV |
| `05_stt_ditado_inteligente.py` | Bloco de notas por voz com comandos | STT |

## 🔴 03_DIFICIL — Nível profissional (IA de verdade)

| Arquivo | O que ensina | Tecnologia |
|--------|--------------|-----------|
| `01_yolo_deteccao_objetos.py` | Detectar 80 tipos de objetos de uma vez | YOLO |
| `02_yolo_treinamento_proprio.py` | **TREINAR seu próprio modelo** passo a passo | YOLO |
| `03_yolo_rastreamento_contagem.py` | Seguir e contar objetos únicos (IDs) | YOLO |
| `04_opencv_scanner_documento.py` | Scanner de documentos (corrigir perspectiva) | OpenCV |
| `05_stt_pergunte_a_camera.py` | Falar uma pergunta e a câmera responde | STT + YOLO |

---

## ▶️ Como rodar um exemplo

**No computador (PyCharm/VSCode):**
```bash
cd 01_FACIL
python 01_primeira_imagem.py
```

**No Google Colab:** crie um notebook, instale as libs, e cole o conteúdo do
arquivo **junto** com o conteúdo do `util_ambiente.py` na mesma célula (ou
faça upload dos dois arquivos).

> 💡 Todos os exemplos deixam o aluno **testar com arquivos externos** (suas
> próprias fotos, vídeos e áudios).

---

### Sequência sugerida para a aula de 4 horas
1. Conceito + instalação (~30 min)
2. Grupo **Fácil** (~50 min)
3. Grupo **Intermediário** (~60 min)
4. Grupo **Difícil**, com destaque para o **treinamento YOLO** (~80 min)
5. Encerramento + exercícios (~20 min)
