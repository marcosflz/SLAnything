"""Lección 6 · Accuracy, precisión y recall."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=6,
    slug="metricas",
    title="Accuracy, precisión y recall",
    summary=(
        "La matriz de confusión separa aciertos y errores por clase; precisión, recall y "
        "F1 resumen aspectos distintos del rendimiento."
    ),
    minutes=11,
    objectives=(
        "Construir una matriz de confusión binaria a partir de predicciones y etiquetas.",
        "Calcular accuracy, precisión, recall y F1.",
        "Elegir la métrica adecuada según el coste de cada error.",
        "Interpretar una matriz 2×2 con un ejemplo numérico.",
    ),
    blocks=(
        lead(
            "Un clasificador puede parecer excelente con una sola cifra y ser inútil para el "
            "problema real. La accuracy mezcla todos los aciertos, pero no distingue si el "
            "modelo detecta spam o si simplemente acierta los mensajes legítimos. Para "
            "decidir con criterio hay que abrir la caja: contar verdaderos positivos, falsos "
            "positivos, falsos negativos y verdaderos negativos."
        ),
        h2("La matriz de confusión"),
        p(
            "En una clasificación binaria, cada predicción cae en una de cuatro casillas. Un "
            "<strong>verdadero positivo</strong> (TP) es un spam que el modelo marca como "
            "spam. Un <strong>falso positivo</strong> (FP) es un mensaje legítimo marcado "
            "como spam. Un <strong>falso negativo</strong> (FN) es un spam que se cuela como "
            "legítimo. Un <strong>verdadero negativo</strong> (TN) es un mensaje legítimo "
            "clasificado como tal. La matriz 2×2 ordena esas cantidades y hace visibles los "
            "dos tipos de error, que la accuracy suma sin distinguir."
        ),
        figure(
            "img/ch06/matriz-confusion.svg",
            "Matriz de confusión 2×2 con verdaderos positivos, falsos positivos, falsos negativos y verdaderos negativos, y las fórmulas de accuracy, precisión, recall y F1.",
            "La matriz de confusión separa los aciertos y los errores por clase. Las "
            "métricas derivadas responden a preguntas distintas sobre el mismo recuento.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "Tomemos un ejemplo con 200 mensajes: 40 spam detectados (TP), 10 mensajes "
            "legítimos marcados como spam (FP), 20 spam que pasan desapercibidos (FN) y 130 "
            "mensajes legítimos correctamente clasificados (TN). Hay 60 spam reales y 140 "
            "ham reales. El modelo acierta 170 de 200. Esas cifras son inventadas para el "
            "ejercicio, pero la estructura es la misma que la del capítulo."
        ),
        h2("Cuatro formas de resumir"),
        p(
            "La <strong>accuracy</strong> o exactitud es <code>(TP + TN) / total</code>: "
            "170/200 = <strong>85,0 %</strong>. La <strong>precisión</strong> responde a "
            "«de todo lo que marqué como spam, ¿cuánto lo era?»: "
            "<code>TP / (TP + FP)</code> = 40/50 = <strong>80,0 %</strong>. El "
            "<strong>recall</strong> o exhaustividad responde a «de todo el spam real, "
            "¿cuánto detecté?»: <code>TP / (TP + FN)</code> = 40/60 = "
            "<strong>66,7 %</strong>. El <strong>F1</strong> es la media armónica de "
            "precisión y recall: <code>2 · P · R / (P + R)</code> ≈ <strong>72,7 %</strong>. "
            "La media armónica castiga los valores bajos, así que un F1 alto exige que ambas "
            "métricas sean razonables."
        ),
        table(
            ["Métrica", "Fórmula", "Ejemplo", "Pregunta que responde"],
            [
                ["Accuracy", "(TP + TN) / total", "85,0 %", "¿Cuántas predicciones acerté en total?"],
                ["Precisión", "TP / (TP + FP)", "80,0 %", "¿Cuánto de lo marcado como spam era spam?"],
                ["Recall", "TP / (TP + FN)", "66,7 %", "¿Cuánto del spam real detecté?"],
                ["F1", "2PR / (P + R)", "72,7 %", "¿Cómo equilibro precisión y recall?"],
            ],
            caption="Las cuatro métricas sobre la matriz TP=40, FP=10, FN=20, TN=130.",
        ),
        py(
            """
etiquetas = [1] * 60 + [0] * 140   # 60 spam y 140 ham
predicciones = [1] * 40 + [0] * 20 + [1] * 10 + [0] * 130

tp = sum(1 for real, pred in zip(etiquetas, predicciones) if real == 1 and pred == 1)
fp = sum(1 for real, pred in zip(etiquetas, predicciones) if real == 0 and pred == 1)
fn = sum(1 for real, pred in zip(etiquetas, predicciones) if real == 1 and pred == 0)
tn = sum(1 for real, pred in zip(etiquetas, predicciones) if real == 0 and pred == 0)

total = len(etiquetas)
exactitud = (tp + tn) / total
precision = tp / (tp + fp) if tp + fp else 0.0
recall = tp / (tp + fn) if tp + fn else 0.0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

print(f"TP={tp}  FP={fp}  FN={fn}  TN={tn}")
print(f"Exactitud: {exactitud:.3f}")
print(f"Precisión: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1:        {f1:.3f}")
""",
            caption=(
                "Cálculo de la matriz de confusión y de las cuatro métricas sin usar "
                "librerías externas."
            ),
        ),
        callout(
            "note",
            "La métrica depende del coste",
            "Si un falso positivo hace que se pierda un mensaje importante, prioriza la "
            "precisión. Si un falso negativo deja pasar una amenaza, prioriza el recall. El "
            "F1 es un buen resumen cuando ambos errores pesan parecido, pero no sustituye a "
            "una matriz de costes cuando las consecuencias son muy distintas."
        ),
        check(
            "Con TP=40, FP=10 y FN=20, ¿por qué el recall es 66,7 % y no 80 %?",
            "Porque el recall divide los verdaderos positivos entre todos los positivos "
            "reales, que incluyen los falsos negativos: 40 / (40 + 20) = 0,667. El 80 % es "
            "la precisión, que divide entre las predicciones positivas: 40 / (40 + 10).",
        ),
        keypoints(
            [
                "La matriz de confusión separa TP, FP, FN y TN.",
                "La accuracy puede ocultar un mal rendimiento en la clase minoritaria.",
                "La precisión mide la pureza de las predicciones positivas.",
                "El recall mide la cobertura de los positivos reales.",
                "El F1 combina precisión y recall con una media armónica.",
                "La métrica elegida debe reflejar el coste de cada tipo de error.",
            ]
        ),
    ),
    key_points=(
        "Accuracy, precisión y recall responden a preguntas diferentes.",
        "La matriz de confusión es la base de todas las métricas binarias.",
        "La precisión penaliza los falsos positivos; el recall, los falsos negativos.",
        "El F1 resume el equilibrio entre precisión y recall.",
        "El coste del error decide qué métrica priorizar.",
    ),
)
