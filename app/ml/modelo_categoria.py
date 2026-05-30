"""
Modelo de ML para categorizar tarefas automaticamente
com base no título e descrição.

Categorias: desenvolvimento, bug, documentacao,
            reuniao, estudo, devops, design, outro
"""

import joblib
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

MODEL_PATH = Path(__file__).parent / "artifacts" / "categoria_model.pkl"
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

DADOS_TREINO = [
    # desenvolvimento
    ("implementar endpoint usuario api rest",           "desenvolvimento"),
    ("criar funcionalidade carrinho compras",           "desenvolvimento"),
    ("desenvolver modulo autenticacao jwt",             "desenvolvimento"),
    ("adicionar paginacao listagem produtos",           "desenvolvimento"),
    ("refatorar servico pagamento",                     "desenvolvimento"),
    ("criar migration banco dados",                     "desenvolvimento"),
    # bug
    ("corrigir erro login usuarios",                    "bug"),
    ("fix bug calculo total pedido",                    "bug"),
    ("resolver problema lentidao query",                "bug"),
    ("bug tela branca producao",                        "bug"),
    ("corrigir falha envio email",                      "bug"),
    ("erro 500 rota checkout",                          "bug"),
    # documentacao
    ("escrever documentacao api swagger",               "documentacao"),
    ("atualizar readme projeto",                        "documentacao"),
    ("documentar arquitetura sistema",                  "documentacao"),
    ("criar wiki onboarding novos devs",                "documentacao"),
    ("descrever fluxo autenticacao",                    "documentacao"),
    # reuniao
    ("reuniao planejamento sprint",                     "reuniao"),
    ("call alinhamento cliente produto",                "reuniao"),
    ("retrospectiva time",                              "reuniao"),
    ("dailystandup equipe",                             "reuniao"),
    ("apresentacao resultado stakeholders",             "reuniao"),
    # estudo
    ("estudar fastapi documentacao oficial",            "estudo"),
    ("ler artigo machine learning",                     "estudo"),
    ("assistir curso kubernetes",                       "estudo"),
    ("pesquisar biblioteca grafico python",             "estudo"),
    ("explorar nova versao postgresql",                 "estudo"),
    # devops
    ("configurar pipeline ci cd github actions",        "devops"),
    ("subir container docker producao",                 "devops"),
    ("configurar monitoramento prometheus grafana",     "devops"),
    ("setup kubernetes cluster",                        "devops"),
    ("backup banco dados automatico",                   "devops"),
    # design
    ("criar wireframe tela dashboard",                  "design"),
    ("revisar prototipo figma",                         "design"),
    ("definir paleta cores sistema",                    "design"),
    ("melhorar ux formulario cadastro",                 "design"),
    # outro
    ("organizar mesa escritorio",                       "outro"),
    ("comprar cafe escritorio",                         "outro"),
    ("responder email rh",                              "outro"),
]


def treinar_modelo() -> Pipeline:
    textos = [t for t, _ in DADOS_TREINO]
    labels = [l for _, l in DADOS_TREINO]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=800)),
        ("clf",   LogisticRegression(max_iter=1000, C=1.0, random_state=42)),
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        textos, labels, test_size=0.2, random_state=42, stratify=labels
    )
    pipeline.fit(X_train, y_train)

    print(classification_report(pipeline.predict(X_test), y_test, zero_division=0))
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Modelo salvo em {MODEL_PATH}")
    return pipeline


def carregar_modelo() -> Pipeline:
    if not MODEL_PATH.exists():
        return treinar_modelo()
    return joblib.load(MODEL_PATH)


_modelo: Pipeline | None = None


def prever_categoria(titulo: str, descricao: str = "") -> dict:
    global _modelo
    if _modelo is None:
        _modelo = carregar_modelo()

    texto = f"{titulo} {descricao}".lower().strip()
    categoria = _modelo.predict([texto])[0]
    probabilidades = _modelo.predict_proba([texto])[0]
    classes = _modelo.classes_

    top3 = sorted(
        zip(classes, probabilidades),
        key=lambda x: x[1], reverse=True
    )[:3]

    return {
        "categoria_sugerida": categoria,
        "top3": [{"categoria": c, "confianca": round(float(p), 3)} for c, p in top3],
        "confianca_maxima": round(float(max(probabilidades)), 3),
    }
