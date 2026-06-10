# ==============================================================================
#  EXEMPLO DIFÍCIL 3  —  "CONTANDO E SEGUINDO"  (Rastreamento + contagem)
# ==============================================================================
#
#  OBJETIVO: além de detectar, vamos SEGUIR cada objeto e CONTAR quantos
#  diferentes apareceram. É a tecnologia por trás de: contar quantas pessoas
#  entraram numa loja, quantos carros passaram numa rua, etc.
#
#  DETECTAR x RASTREAR (a diferença chave):
#    * Detectar = em cada quadro, "tem 2 pessoas aqui" (mas não sabe se são as
#      MESMAS do quadro anterior).
#    * Rastrear = dá um "número de crachá" (ID) pra cada objeto e segue ele
#      quadro a quadro. Assim a pessoa #3 continua sendo a #3 enquanto anda.
#
#  ANALOGIA: imagina um professor na excursão. Detectar é contar cabeças a cada
#  parada (pode contar a mesma pessoa duas vezes). Rastrear é dar um colete
#  numerado pra cada aluno — aí dá pra saber exatamente quem é quem e quantos
#  alunos diferentes existem no total. O YOLO faz isso com o modo .track().
#
#  COMO RODAR:
#    - Colab: modo VÍDEO (envie um .mp4). Gera um vídeo de saída anotado.
#    - PC: VÍDEO ou WEBCAM ao vivo.
# ==============================================================================

import cv2
from util_ambiente import escolher_arquivo, webcam_disponivel, estou_no_colab

try:
    from ultralytics import YOLO
except ImportError:
    print("Instale o YOLO com:  pip install ultralytics")
    raise SystemExit


MODELO = "yolov8n.pt"

# Por padrão vamos contar PESSOAS (classe 0 no COCO). Para contar carros, use 2.
CLASSE_ALVO = 0
NOME_ALVO = "pessoa"


def processar(modelo, fonte, salvar_video=False):
    """
    Roda o rastreamento na 'fonte' (caminho de vídeo ou 0 pra webcam) e conta
    quantos objetos ÚNICOS da classe-alvo apareceram (pelos IDs de crachá).
    """
    cap = cv2.VideoCapture(fonte)
    ids_vistos = set()  # guarda os "crachás" já contados (não repete)

    escritor = None
    if salvar_video:
        largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        escritor = cv2.VideoWriter("contagem_saida.mp4",
                                   cv2.VideoWriter_fourcc(*"mp4v"),
                                   fps, (largura, altura))

    while True:
        ok, quadro = cap.read()
        if not ok:
            break

        # persist=True faz o YOLO "lembrar" dos crachás entre os quadros.
        resultados = modelo.track(quadro, persist=True, verbose=False)

        if resultados[0].boxes.id is not None:
            classes = resultados[0].boxes.cls.tolist()
            ids = resultados[0].boxes.id.tolist()
            for classe, ident in zip(classes, ids):
                if int(classe) == CLASSE_ALVO:
                    ids_vistos.add(int(ident))

        anotada = resultados[0].plot()
        # Escreve o total no canto da tela.
        cv2.putText(anotada, f"{NOME_ALVO}(s) unicas: {len(ids_vistos)}",
                    (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if escritor is not None:
            escritor.write(anotada)

        if not estou_no_colab():
            cv2.imshow("Rastreamento + contagem - 'q' pra sair", anotada)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    if escritor is not None:
        escritor.release()
        print("Vídeo anotado salvo como 'contagem_saida.mp4'.")
    if not estou_no_colab():
        cv2.destroyAllWindows()

    print(f"\n>> TOTAL de {NOME_ALVO}(s) diferentes detectadas: {len(ids_vistos)}")


def main():
    print("=" * 60)
    print(" EXEMPLO DIFÍCIL 3 — Rastreamento e contagem com YOLO")
    print("=" * 60)

    print("\nCarregando o YOLO...")
    modelo = YOLO(MODELO)

    if webcam_disponivel():
        print("\nEscolha o modo:")
        print("  1 - VÍDEO (arquivo externo)")
        print("  2 - WEBCAM ao vivo")
        escolha = input("Digite 1 ou 2: ").strip()
        if escolha == "2":
            processar(modelo, 0, salvar_video=False)
        else:
            caminho = escolher_arquivo()
            if caminho:
                processar(modelo, caminho, salvar_video=True)
    else:
        print("\nVocê está no Colab — envie um VÍDEO (.mp4).")
        caminho = escolher_arquivo()
        if caminho:
            processar(modelo, caminho, salvar_video=True)


if __name__ == "__main__":
    main()
