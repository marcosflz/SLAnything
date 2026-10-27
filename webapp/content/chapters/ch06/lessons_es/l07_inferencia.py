"""Lección 7 · Inferencia y umbrales."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=7,
    slug="inferencia-clasificador",
    title="Inferencia y umbrales",
    summary=(
        "El modelo devuelve probabilidades; el umbral convierte esas probabilidades en "
        "decisiones y determina qué tipo de error aceptamos."
    ),
    minutes=10,
    objectives=(
        "Convertir logits en probabilidades y aplicar un umbral de decisión.",
        "Explicar cómo afecta mover el umbral a la precisión y al recall.",
        "Relacionar la calibración con la elección del umbral.",
        "Elegir un umbral a partir del coste de los errores.",
    ),
    blocks=(
        lead(
            "En producción, un clasificador no entrega una etiqueta mágica: entrega una "
            "puntuación. Alguien —una persona o una regla— decide a partir de qué valor se "
            "actúa. Ese valor es el umbral, y no es un detalle técnico menor. Moverlo cambia "
            "cuántos spam se detectan, cuántos mensajes legítimos se bloquean y, en última "
            "instancia, el coste del sistema."
        ),
        h2("La probabilidad no es la decisión"),
        p(
            "La cabeza de clasificación produce dos logits. Softmax los convierte en "
            "probabilidades que suman 1. La regla por defecto es elegir la clase con mayor "
            "probabilidad, lo que equivale a un umbral de <strong>0,5</strong> en el caso "
            "binario. Si la probabilidad de spam supera 0,5, se marca como spam; si no, se "
            "deja pasar. Pero 0,5 no tiene nada de sagrado: es solo el punto en el que dos "
            "clases simétricas se equilibran."
        ),
        p(
            "La <strong>calibración</strong> describe si las probabilidades significan lo que "
            "parecen. Un modelo puede decir 0,9 con una confianza real mucho menor, o "
            "viceversa. Los transformers suelen ser demasiado confiados, sobre todo tras un "
            "finetuning corto. Por eso el umbral se elige empíricamente sobre validación, "
            "comparando la tasa de aciertos y errores en distintos puntos, y no se copia sin "
            "más de otro problema. El test no debe usarse para esta búsqueda: si lo haces, "
            "deja de ser una estimación independiente."
        ),
        h2("Mover el umbral cambia el tipo de error"),
        p(
            "Supón diez mensajes con su probabilidad de spam y su etiqueta real. Con umbral "
            "0,5 se detectan 3 de los 5 spam, pero se marcan 2 ham como spam: precisión "
            "60 %, recall 60 %. Si bajamos el umbral a 0,3, se detectan los 5 spam y no queda "
            "ningún falso negativo, aunque aparecen 3 falsos positivos: precisión 62,5 %, "
            "recall 100 %. Si lo subimos a 0,7, solo se detectan 2 spam y se cuela 1 ham: "
            "precisión 66,7 %, recall 40 %. El mismo modelo, tres políticas distintas."
        ),
        table(
            ["Umbral", "TP", "FP", "FN", "Precisión", "Recall", "F1"],
            [
                ["0,30", "5", "3", "0", "62,5 %", "100 %", "76,9 %"],
                ["0,50", "3", "2", "2", "60,0 %", "60,0 %", "60,0 %"],
                ["0,70", "2", "1", "3", "66,7 %", "40,0 %", "50,0 %"],
            ],
            caption="Efecto de tres umbrales sobre los mismos diez mensajes de ejemplo.",
        ),
        py(
            """
ejemplos = [
    (0.90, 1), (0.80, 1), (0.75, 0), (0.60, 1), (0.55, 0),
    (0.45, 1), (0.40, 1), (0.30, 0), (0.20, 0), (0.10, 0),
]

for umbral in (0.30, 0.50, 0.70):
    tp = fp = fn = 0
    for probabilidad, real in ejemplos:
        prediccion = 1 if probabilidad >= umbral else 0
        if prediccion == 1 and real == 1:
            tp += 1
        elif prediccion == 1 and real == 0:
            fp += 1
        elif prediccion == 0 and real == 1:
            fn += 1

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    print(
        f"Umbral {umbral:.2f}: TP={tp} FP={fp} FN={fn} "
        f"precisión={precision:.3f} recall={recall:.3f} F1={f1:.3f}"
    )
""",
            caption=(
                "Barrido de umbrales sobre diez mensajes. Bajar el umbral suele subir el "
                "recall y bajar la precisión."
            ),
        ),
        callout(
            "warning",
            "La accuracy puede quedarse igual",
            "Al mover el umbral, algunos errores se intercambian: un falso negativo se "
            "convierte en verdadero positivo y un verdadero negativo en falso positivo. El "
            "número total de aciertos puede no cambiar, aunque el tipo de fallo sí. Por eso "
            "hay que mirar la matriz completa y el coste, no solo la accuracy."
        ),
        check(
            "Bajas el umbral de 0,5 a 0,3. ¿Qué esperas que ocurra con el recall y con la "
            "precisión?",
            "El recall sube porque más mensajes superan el umbral y se detectan más spam "
            "reales. La precisión suele bajar porque también entran más ham marcados como "
            "spam. Es un intercambio clásico: se gana cobertura a costa de falsos positivos.",
        ),
        keypoints(
            [
                "El modelo produce probabilidades; el umbral produce decisiones.",
                "0,5 es una convención, no una verdad universal.",
                "Bajar el umbral aumenta el recall y suele reducir la precisión.",
                "Subir el umbral protege la precisión y deja pasar más positivos.",
                "La calibración determina si una probabilidad merece confianza.",
                "El umbral se elige en validación según el coste de cada error.",
            ]
        ),
    ),
    key_points=(
        "Un umbral convierte una puntuación en una acción del sistema.",
        "El umbral por defecto es 0,5, pero no siempre es el óptimo.",
        "Precisión y recall se mueven en direcciones opuestas al ajustar el umbral.",
        "La calibración afecta a la interpretación de las probabilidades.",
        "El umbral se selecciona con validación y se evalúa una vez en test.",
    ),
)
