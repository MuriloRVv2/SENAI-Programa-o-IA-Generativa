# ==============================================================================
#  EXEMPLO INTERMEDIÁRIO 1  —  "DE QUEM É ESSE ROSTO?"  (Reconhecimento facial)
# ==============================================================================
#
#  OBJETIVO: agora não basta achar o rosto — queremos saber DE QUEM ele é.
#  É o pulo do gato entre DETECTAR e RECONHECER.
#
#  RELEMBRANDO:
#    * DETECTAR (Etapa 1)  = "tem um rosto aqui" (não sei de quem)
#    * RECONHECER (agora)  = "esse rosto é da ANA!"
#
#  ANALOGIA: imagina que cada rosto vira uma "impressão digital" de 128 números
#  (a gente chama de "embedding"). Rostos da MESMA pessoa têm impressões
#  parecidas; de pessoas diferentes, bem diferentes. Reconhecer é só comparar:
#  "essa impressão digital nova parece com a da Ana ou com a do João?".
#  É tipo um crachá invisível que o rosto carrega.
#
#  COMO FUNCIONA AQUI:
#    1) Você dá algumas fotos "conhecidas" (1 por pessoa) numa pasta.
#    2) O programa aprende a impressão digital de cada uma.
#    3) Você manda uma foto nova e ele diz quem é (ou "Desconhecido").
#
#  COMO RODAR:
#    - Colab: instale com  !pip install face_recognition
#    - PC: veja o GUIA_INSTALACAO (o dlib pode dar trabalho no Windows).
#      Se travar no Windows, rode este exemplo no Colab.
# ==============================================================================

import os
import cv2
from util_ambiente import mostrar_imagem, escolher_arquivo, estou_no_colab

try:
    import face_recognition
except ImportError:
    print("A biblioteca 'face_recognition' não está instalada.")
    print("No Colab rode:  !pip install face_recognition")
    print("No PC veja o GUIA_INSTALACAO.md (seção do dlib).")
    raise SystemExit


# Pasta onde ficam as fotos "conhecidas" (1 foto por pessoa).
# O NOME DO ARQUIVO vira o nome da pessoa. Ex: ana.jpg -> "ana"
PASTA_CONHECIDOS = "rostos_conhecidos"


def aprender_rostos_conhecidos():
    """
    Lê todas as fotos da pasta 'rostos_conhecidos' e guarda a "impressão
    digital" (encoding) de cada pessoa, junto com o nome dela.
    """
    nomes = []
    impressoes = []

    if not os.path.isdir(PASTA_CONHECIDOS):
        os.makedirs(PASTA_CONHECIDOS, exist_ok=True)
        print(f"Criei a pasta '{PASTA_CONHECIDOS}'.")
        print("Coloque lá fotos com o nome da pessoa (ex: ana.jpg, joao.png) e rode de novo.")
        return nomes, impressoes

    for arquivo in os.listdir(PASTA_CONHECIDOS):
        caminho = os.path.join(PASTA_CONHECIDOS, arquivo)
        imagem = face_recognition.load_image_file(caminho)
        codigos = face_recognition.face_encodings(imagem)

        if len(codigos) == 0:
            print(f"  (pulei '{arquivo}': não achei rosto nela)")
            continue

        nome = os.path.splitext(arquivo)[0]  # tira a extensão (.jpg, .png)
        nomes.append(nome)
        impressoes.append(codigos[0])  # pega o primeiro rosto da foto
        print(f"  Aprendi o rosto de: {nome}")

    return nomes, impressoes


def reconhecer_em_foto(nomes, impressoes):
    """Recebe uma foto NOVA e marca quem é cada pessoa."""
    print("\nEscolha a foto que você quer ANALISAR (pode ter várias pessoas):")
    caminho = escolher_arquivo()
    if not caminho:
        print("Nenhum arquivo escolhido.")
        return

    # Carrega a imagem nos dois formatos: um pro face_recognition, outro pro OpenCV desenhar.
    imagem_rgb = face_recognition.load_image_file(caminho)
    imagem_bgr = cv2.cvtColor(imagem_rgb, cv2.COLOR_RGB2BGR)

    # Acha todos os rostos e suas impressões digitais.
    locais = face_recognition.face_locations(imagem_rgb)
    codigos = face_recognition.face_encodings(imagem_rgb, locais)

    print(f">> Achei {len(locais)} rosto(s) na foto.")

    for (topo, dir_, baixo, esq), codigo in zip(locais, codigos):
        # Compara a impressão nova com as conhecidas.
        comparacoes = face_recognition.compare_faces(impressoes, codigo, tolerance=0.5)
        nome = "Desconhecido"

        if True in comparacoes:
            # Pega o nome da pessoa que mais combinou.
            indice = comparacoes.index(True)
            nome = nomes[indice]

        # Desenha o quadrado e escreve o nome.
        cor = (0, 255, 0) if nome != "Desconhecido" else (0, 0, 255)
        cv2.rectangle(imagem_bgr, (esq, topo), (dir_, baixo), cor, 2)
        cv2.putText(imagem_bgr, nome, (esq, topo - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)

    mostrar_imagem(imagem_bgr, "Reconhecimento facial")
    cv2.imwrite("reconhecimento_resultado.jpg", imagem_bgr)
    print("Salvei o resultado como 'reconhecimento_resultado.jpg'.")


def main():
    print("=" * 60)
    print(" EXEMPLO INTERMEDIÁRIO 1 — Reconhecimento facial (quem é?)")
    print("=" * 60)

    print("\n[1/2] Aprendendo os rostos conhecidos...")
    nomes, impressoes = aprender_rostos_conhecidos()

    if len(nomes) == 0:
        print("\nNenhum rosto conhecido cadastrado ainda. Coloque fotos na pasta e rode de novo.")
        return

    print("\n[2/2] Vamos reconhecer numa foto nova!")
    reconhecer_em_foto(nomes, impressoes)


if __name__ == "__main__":
    main()
