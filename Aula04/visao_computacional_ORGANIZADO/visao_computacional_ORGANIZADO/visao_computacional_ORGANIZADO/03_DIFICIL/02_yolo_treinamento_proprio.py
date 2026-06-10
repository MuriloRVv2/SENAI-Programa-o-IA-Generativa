# ==============================================================================
#  EXEMPLO DIFÍCIL 2  —  "TREINANDO O SEU PRÓPRIO YOLO"  (Treinamento do zero)
# ==============================================================================
#
#  OBJETIVO: o YOLO de fábrica conhece 80 objetos comuns. Mas e se você quiser
#  que ele reconheça algo ESPECÍFICO (o crachá da escola? um robô do laboratório?
#  uma fruta específica?). Aí a gente TREINA o nosso próprio modelo!
#
#  A GRANDE ANALOGIA DO TREINAMENTO:
#  Treinar uma IA é como ensinar uma criança a reconhecer "gato".
#    1) Você mostra MUITAS fotos de gato dizendo "isso é gato" (os DADOS + RÓTULOS).
#    2) A criança erra no começo, você corrige, ela tenta de novo... (as ÉPOCAS).
#    3) Depois de praticar bastante, ela acerta sozinha em fotos novas (o MODELO TREINADO).
#  É EXATAMENTE isso que faremos abaixo.
#
#  ----------------------------------------------------------------------------
#  AS 4 ETAPAS DO TREINAMENTO (leia com calma!)
#  ----------------------------------------------------------------------------
#  ETAPA A — JUNTAR AS FOTOS (dataset):
#     Tire/baixe muitas fotos do objeto. Quanto mais variado (ângulos, luz,
#     fundos), melhor. Recomendado pra aula: 50 a 150 fotos por objeto.
#
#  ETAPA B — ROTULAR (anotar onde está o objeto em cada foto):
#     Pra cada foto, você marca um retângulo em volta do objeto e diz a classe.
#     Ferramenta gratuita recomendada: site "Roboflow" ou programa "LabelImg".
#     Isso gera, pra cada imagem.jpg, um arquivo imagem.txt com linhas assim:
#         classe   x_centro   y_centro   largura   altura
#     (todos os números de 0 a 1, ou seja, "proporção" da imagem)
#     Ex:  0  0.51  0.43  0.20  0.30   ->  objeto da classe 0, no meio da foto.
#
#  ETAPA C — ORGANIZAR AS PASTAS no formato que o YOLO espera (veja função abaixo).
#
#  ETAPA D — TREINAR e depois USAR o modelo.
#  ----------------------------------------------------------------------------
#
#  COMO RODAR:
#    - Colab é o LUGAR IDEAL pra treinar (tem GPU grátis! Menu: Ambiente de
#      execução > Alterar tipo > GPU). Treinar na CPU funciona, mas é lento.
#    - PC: funciona, mas sem placa de vídeo boa pode demorar.
# ==============================================================================

import os
from ultralytics import YOLO


# Estrutura de pastas que o YOLO exige:
#
#   meu_dataset/
#   ├── images/
#   │   ├── train/   (fotos de TREINO  -> ~80% das fotos)
#   │   └── val/     (fotos de VALIDAÇÃO -> ~20%, pra "tirar a prova")
#   └── labels/
#       ├── train/   (os .txt das fotos de treino)
#       └── val/     (os .txt das fotos de validação)
#
#  Por que separar treino e validação? É como estudar com a lista de exercícios
#  (treino) e depois fazer a PROVA com questões que você não viu (validação).
#  Assim sabemos se a IA realmente aprendeu, em vez de só "decorar".

PASTA_DATASET = "meu_dataset"
NOMES_CLASSES = ["meu_objeto"]  # troque pelos nomes dos SEUS objetos. Ex: ["cracha", "robo"]


def criar_estrutura_de_pastas():
    """Cria as pastas vazias no formato certo, se ainda não existirem."""
    subpastas = [
        "images/train", "images/val",
        "labels/train", "labels/val",
    ]
    for sub in subpastas:
        os.makedirs(os.path.join(PASTA_DATASET, sub), exist_ok=True)
    print(f"Estrutura criada em '{PASTA_DATASET}/'. Agora coloque suas fotos e .txt nas pastas.")


def criar_arquivo_yaml():
    """
    Cria o 'dados.yaml' — o mapa que diz ao YOLO onde estão as fotos e quais
    são as classes. É a 'lista de chamada' das coisas que ele vai aprender.
    """
    caminho_abs = os.path.abspath(PASTA_DATASET)
    linhas_classes = "\n".join([f"  {i}: {nome}" for i, nome in enumerate(NOMES_CLASSES)])
    conteudo = f"""# Mapa do dataset para o YOLO
path: {caminho_abs}
train: images/train
val: images/val

names:
{linhas_classes}
"""
    with open("dados.yaml", "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("Criei o arquivo 'dados.yaml'. Confira se está tudo certo.")
    print(conteudo)


def treinar():
    """
    TREINA o modelo. Os parâmetros explicados (em analogia):
      - epochs (épocas): quantas vezes a IA "revê a matéria inteira".
                         Poucas = aprende mal; muitas = pode "decorar demais".
                         Pra aula, 50 costuma ser um bom começo.
      - imgsz: o tamanho que as fotos são redimensionadas pra treinar (640 é padrão).
      - batch: quantas fotos ela olha por vez (como estudar de 16 em 16 cartões).
    """
    if not os.path.exists("dados.yaml"):
        print("Falta o 'dados.yaml'. Rode a opção 2 primeiro.")
        return

    # Começamos a partir do modelo de fábrica (yolov8n.pt) e o "afinamos" pro
    # nosso problema. Isso se chama TRANSFER LEARNING: aproveitar o que ele já
    # sabe (bordas, formas) em vez de aprender tudo do zero. Economiza MUITO tempo.
    modelo = YOLO("yolov8n.pt")

    print("\nIniciando o treinamento... (acompanhe os números subindo!)")
    modelo.train(
        data="dados.yaml",
        epochs=50,
        imgsz=640,
        batch=16,
        name="meu_modelo",   # nome da pasta de resultados
    )
    print("\nTreino concluído! O melhor modelo foi salvo em:")
    print("   runs/detect/meu_modelo/weights/best.pt")


def testar_modelo_treinado():
    """Usa o modelo que VOCÊ treinou numa foto nova."""
    caminho_modelo = "runs/detect/meu_modelo/weights/best.pt"
    if not os.path.exists(caminho_modelo):
        print("Ainda não há modelo treinado. Treine primeiro (opção 3).")
        return
    modelo = YOLO(caminho_modelo)
    from util_ambiente import escolher_arquivo, mostrar_imagem
    import cv2
    print("\nEscolha uma foto NOVA pra testar seu modelo:")
    caminho = escolher_arquivo()
    if not caminho:
        return
    resultados = modelo(caminho)
    anotada = resultados[0].plot()
    mostrar_imagem(anotada, "Meu modelo treinado")
    cv2.imwrite("meu_modelo_resultado.jpg", anotada)
    print("Salvei como 'meu_modelo_resultado.jpg'.")


def main():
    print("=" * 60)
    print(" EXEMPLO DIFÍCIL 2 — Treinando o SEU próprio YOLO")
    print("=" * 60)
    print("""
Roteiro sugerido:
  1) Criar as pastas      -> opção 1
  2) (Você) coloca fotos + .txt nas pastas e ajusta NOMES_CLASSES no topo
  3) Criar o dados.yaml   -> opção 2
  4) Treinar              -> opção 3
  5) Testar o seu modelo  -> opção 4
""")
    print("  1 - Criar estrutura de pastas")
    print("  2 - Criar o arquivo dados.yaml")
    print("  3 - TREINAR o modelo")
    print("  4 - TESTAR o modelo treinado")
    escolha = input("O que deseja fazer? (1/2/3/4): ").strip()

    if escolha == "1":
        criar_estrutura_de_pastas()
    elif escolha == "2":
        criar_arquivo_yaml()
    elif escolha == "3":
        treinar()
    elif escolha == "4":
        testar_modelo_treinado()
    else:
        print("Opção inválida.")


if __name__ == "__main__":
    main()
