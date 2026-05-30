"""
Modelo de ML para prever a prioridade de uma tarefa
com base no título e descrição.

Pipeline:
  texto → TF-IDF → Naive Bayes → prioridade (baixa/media/alta)
"""

import os
import joblib
import numpy as np
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

MODEL_PATH = Path(__file__).parent / "artifacts" / "prioridade_model.pkl"
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

# Dados de treinamento — em produção viria do banco
DADOS_TREINO = [
    # (texto, prioridade)
    ("bug critico sistema fora do ar producao", "alta"),
    ("corrigir erro pagamento cliente bloqueado", "alta"),
    ("servidor caindo deploy urgente", "alta"),
    ("falha segurança vulnerabilidade critica", "alta"),
    ("prazo entrega amanha reuniao diretoria", "alta"),
    ("cliente aguardando resposta urgente", "alta"),
    ("implementar nova funcionalidade sprint", "media"),
    ("refatorar codigo modulo usuario", "media"),
    ("escrever testes unitarios servico", "media"),
    ("revisar pull request colega", "media"),
    ("atualizar documentacao api", "media"),
    ("melhorar performance query banco", "media"),
    ("criar dashboard relatorio mensal", "media"),
    ("organizar arquivos projeto", "baixa"),
    ("ler artigo sobre nova tecnologia", "baixa"),
    ("atualizar dependencias versao menor", "baixa"),
    ("limpar comentarios codigo antigo", "baixa"),
    ("renomear variaveis padrao", "baixa"),
    ("adicionar emoji readme", "baixa"),
    ("explorar biblioteca interessante", "baixa"),
]


def _preparar_dados():
    textos = [t for t, _ in DADOS_TREINO]
    labels = [l for _, l in DADOS_TREINO]
    return textos, labels


def treinar_modelo() -> Pipeline:
    textos, labels = _preparar_dados()

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=500,
            stop_words=None,
        )),
        ("clf", MultinomialNB(alpha=0.5)),
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        textos, labels, test_size=0.2, random_state=42
    )
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred, zero_division=0))

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Modelo salvo em {MODEL_PATH}")
    return pipeline


def carregar_modelo() -> Pipeline:
    if not MODEL_PATH.exists():
        print("Modelo não encontrado — treinando...")
        return treinar_modelo()
    return joblib.load(MODEL_PATH)


_modelo: Pipeline | None = None


def prever_prioridade(titulo: str, descricao: str = "") -> dict:
    global _modelo
    if _modelo is None:
        _modelo = carregar_modelo()

    texto = f"{titulo} {descricao}".lower().strip()
    prioridade = _modelo.predict([texto])[0]
    probabilidades = _modelo.predict_proba([texto])[0]
    classes = _modelo.classes_

    confianca = {c: round(float(p), 3) for c, p in zip(classes, probabilidades)}

    return {
        "prioridade_sugerida": prioridade,
        "confianca": confianca,
        "confianca_maxima": round(float(max(probabilidades)), 3),
    }
