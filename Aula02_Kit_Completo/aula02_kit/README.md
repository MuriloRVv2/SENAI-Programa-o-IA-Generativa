# Aula 02 — Aprendizado de Máquina (Kit Completo)

Material prático para iniciantes absolutos. Cobre os **3 tipos de aprendizado**
(supervisionado, não supervisionado e por reforço), além de coleta de dados,
pré-processamento, avaliação de modelos e um projeto completo com Scikit-learn.

## 📁 Estrutura do projeto

```
aula02_kit/
├── codigo/
│   ├── gerar_dados.py        # cria as 3 bases de exemplo (CSV)
│   ├── preprocessamento.py   # carregar, limpar, encoding, dividir, normalizar
│   ├── treinamento.py        # classificação, regressão, KMeans, reforço
│   ├── avaliacao.py          # métricas + gráficos
│   ├── main.py               # PROJETO COMPLETO (roda tudo)
│   └── requirements.txt
├── dados/
│   ├── clientes.csv          # agrupamento (KMeans)
│   ├── vendas.csv            # regressão (preço de imóvel)
│   └── classificacao.csv     # classificação (aprovar crédito)
└── graficos/                 # imagens geradas ao rodar o projeto
```

## ⚙️ Instalação

```bash
cd codigo
pip install -r requirements.txt
```

## ▶️ Execução

```bash
# (opcional) recriar as bases de dados
python gerar_dados.py

# rodar o projeto completo (as 4 partes)
python main.py
```

Cada módulo também roda sozinho para testes:
`python preprocessamento.py`, `python treinamento.py`.

## 📊 As 3 bases de dados

### clientes.csv — *agrupamento*
| coluna | significado |
|--------|-------------|
| id_cliente | identificador único |
| idade | idade do cliente |
| gasto_mensal | quanto gasta por mês (R$) |
| visitas_semana | visitas à loja por semana |

Usada para o **KMeans** descobrir perfis de clientes sem rótulos.

### vendas.csv — *regressão*
| coluna | significado |
|--------|-------------|
| area_m2 | área do imóvel |
| quartos | número de quartos |
| idade_imovel | anos desde a construção |
| garagem | tem garagem (1) ou não (0) |
| preco_mil | **alvo**: preço em mil R$ |

Usada para **prever um número** (o preço) com Regressão Linear.

### classificacao.csv — *classificação*
| coluna | significado |
|--------|-------------|
| idade | idade do solicitante |
| renda_mil | renda mensal (mil R$) |
| dividas_mil | dívidas atuais (mil R$) |
| anos_emprego | anos no emprego atual |
| tem_imovel | possui imóvel (sim/não) |
| aprovado | **alvo**: crédito aprovado (1) ou negado (0) |

Contém valores faltantes e uma coluna de texto **de propósito**, para praticar
limpeza e encoding. Usada para **classificar** (aprovar/negar crédito).

## ✅ Resultados esperados (aproximados)

- Classificação: Accuracy ~95%, F1 ~97%
- Regressão: R² ~98%, MAE ~13 mil R$
- Agrupamento: 3 perfis bem separados de clientes
- Reforço: o agente aprende a ir sempre à direita até o objetivo
