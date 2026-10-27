"""Lección 5 · Entrenar sin romper el modelo."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=5,
    slug="entrenamiento-clasificador",
    title="Entrenar sin romper el modelo",
    summary=(
        "Un ritmo de aprendizaje bajo, pocas capas entrenables y una parada basada en "
        "validación permiten adaptar el modelo sin destruir lo que ya sabía."
    ),
    minutes=11,
    objectives=(
        "Justificar una tasa de aprendizaje baja en el finetuning.",
        "Interpretar las curvas de pérdida y accuracy de entrenamiento y validación.",
        "Aplicar parada temprana y restaurar el mejor checkpoint.",
        "Reconocer señales de sobreajuste y de olvido catastrófico.",
    ),
    blocks=(
        lead(
            "El finetuning se parece más a afinar un instrumento que a construirlo de nuevo. "
            "El modelo ya sabe lenguaje; lo que buscamos es una corrección limitada. Si "
            "aplicamos una tasa de aprendizaje alta o entrenamos todas las capas durante "
            "demasiado tiempo, el clasificador puede mejorar en el lote de entrenamiento y, "
            "a la vez, perder capacidades generales que no necesitábamos tocar."
        ),
        h2("Un ajuste fino, no un reinicio"),
        p(
            "El libro entrena con <strong>AdamW</strong>, una tasa de aprendizaje de "
            "<code>5e-5</code> y un decaimiento de pesos de <code>0,1</code>. El lote es de "
            "8 mensajes y el número de épocas, 5. La tasa es baja en comparación con muchos "
            "entrenamientos desde cero: los pesos de partida ya son valiosos y conviene "
            "moverlos poco en cada paso. El decaimiento de pesos añade una penalización a "
            "pesos grandes y actúa como regularización."
        ),
        p(
            "Solo se actualizan la cabeza nueva, la última capa del transformer y la "
            "normalización final. El resto permanece congelado. Esta decisión reduce el "
            "número de parámetros que reciben gradiente, acelera el entrenamiento y limita "
            "el daño que un lote ruidoso puede hacer en capas tempranas. El libro tarda unos "
            "<strong>5,65 minutos</strong> en un MacBook Air con chip M3 y menos de medio "
            "minuto en una GPU V100 o A100. Son cifras del capítulo, no una promesa para "
            "cualquier hardware."
        ),
        h2("Leer las curvas y parar a tiempo"),
        p(
            "Durante el entrenamiento se registran la pérdida y la accuracy de entrenamiento "
            "y validación. Al final de la primera época, el modelo ronda el 70 % de accuracy "
            "en entrenamiento y el 72,5 % en validación, con una pérdida que ya ha caído con "
            "fuerza. En la época 4 alcanza el 100 % en entrenamiento y el 97,5 % en "
            "validación. La evaluación completa, sin limitarse a cinco lotes, da "
            "<strong>97,21 % en entrenamiento, 97,32 % en validación y 95,67 % en "
            "prueba</strong>."
        ),
        table(
            ["Época", "Pérdida train", "Pérdida val", "Accuracy train", "Accuracy val"],
            [
                ["1", "0,523", "0,557", "70,0 %", "72,5 %"],
                ["2", "0,409", "0,353", "82,5 %", "85,0 %"],
                ["3", "0,340", "0,306", "90,0 %", "90,0 %"],
                ["4", "0,222", "0,137", "100 %", "97,5 %"],
                ["5", "0,083", "0,074", "100 %", "97,5 %"],
            ],
            caption=(
                "Resumen de las curvas del libro. Las accuracies intermedias se estiman "
                "sobre cinco lotes; la evaluación final usa el conjunto completo."
            ),
            note="Cifras de Raschka, Build a Large Language Model (From Scratch), capítulo 6.",
        ),
        p(
            "La <strong>parada temprana</strong> consiste en vigilar una métrica de "
            "validación y detener el entrenamiento cuando deja de mejorar durante varias "
            "evaluaciones. No basta con quedarse con el último estado: conviene guardar el "
            "checkpoint con la mejor pérdida o el mejor F1 de validación y restaurarlo al "
            "final. En el ejemplo del libro la pérdida de validación sigue bajando hasta la "
            "época 5, así que no hay señal de sobreajuste; en otro dataset, la curva podría "
            "girar antes."
        ),
        p(
            "El sobreajuste se reconoce por una brecha creciente: la pérdida de entrenamiento "
            "baja mientras la de validación sube. El <strong>olvido catastrófico</strong> es "
            "otro riesgo: el modelo se especializa tanto que pierde capacidades generales. "
            "Una tasa baja, menos épocas y capas congeladas reducen ambos peligros, pero no "
            "los eliminan. Si el clasificador solo ve mensajes de un dominio, su vocabulario "
            "efectivo se estrecha."
        ),
        callout(
            "tip",
            "Guarda el mejor, no el último",
            "Una práctica sencilla y robusta: después de cada época, evalúa en validación y "
            "guarda una copia de los pesos si la métrica elegida mejora. Al terminar, "
            "restaura esa copia. Así el número de épocas deja de ser una apuesta y se "
            "convierte en un presupuesto máximo."
        ),
        check(
            "La pérdida de entrenamiento baja, pero la de validación empieza a subir. ¿Qué "
            "está ocurriendo y qué harías?",
            "Es la señal típica de sobreajuste: el modelo memoriza el entrenamiento y pierde "
            "capacidad de generalizar. Detendría el entrenamiento, restauraría el checkpoint "
            "con mejor validación y probaría más regularización, menos épocas o más datos.",
        ),
        keypoints(
            [
                "El finetuning usa una tasa de aprendizaje baja para no destruir los pesos previos.",
                "Congelar capas reduce cómputo y riesgo de olvido catastrófico.",
                "El libro usa AdamW, lr=5e-5, weight_decay=0,1, lotes de 8 y 5 épocas.",
                "La accuracy final del libro es 97,21 % train, 97,32 % val y 95,67 % test.",
                "La parada temprana vigila validación, no entrenamiento.",
                "Se restaura el mejor checkpoint, no necesariamente el último.",
            ]
        ),
    ),
    key_points=(
        "El finetuning modifica poco un modelo que ya sabe lenguaje.",
        "Una tasa baja y capas congeladas protegen el conocimiento previo.",
        "La validación decide cuándo parar y qué checkpoint conservar.",
        "Una brecha creciente entre train y val indica sobreajuste.",
        "El número de épocas es un presupuesto, no una receta universal.",
    ),
)
