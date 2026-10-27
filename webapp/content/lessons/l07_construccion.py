"""Lección 7 · Cómo se construye un LLM."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=7,
    slug="como-se-construye",
    title="Cómo se construye un LLM",
    summary=(
        "El mapa del libro: tokenización, embeddings, atención, arquitectura GPT, "
        "pretraining, clasificación e instrucciones, con el coste como brújula."
    ),
    minutes=8,
    objectives=(
        "Recorrer las etapas de construcción de un LLM.",
        "Situar cada capítulo del libro en el pipeline completo.",
        "Explicar por qué se empieza con un modelo pequeño.",
        "Estimar el coste de entrenamiento con la regla FLOPs ≈ 6 · N · D.",
    ),
    blocks=(
        lead(
            "El libro no empieza con un modelo de 175 000 millones de parámetros. Empieza "
            "con una versión pequeña que cabe en un portátil y se puede entender línea a "
            "línea. La escala llega después; primero, las piezas."
        ),
        p(
            "El objetivo es construir un GPT de unos <strong>124 millones de "
            "parámetros</strong>, un tamaño comparable al de GPT-2 small. No es un producto "
            "final: es un <strong>vehículo didáctico</strong>. Tiene los mismos componentes "
            "que un modelo grande —tokenización, embeddings, atención, bloques transformer y "
            "cabeza de salida—, pero se puede entrenar y depurar en hardware de consumo. "
            "Entender cada pieza importa más que reproducir el coste de GPT-3. Cuando haga "
            "falta capacidad, se pueden cargar pesos abiertos ya entrenados."
        ),
        figure(
            "img/ch01/fig_1_9_roadmap.png",
            "Las tres etapas del libro: construir la arquitectura y preparar los datos, preentrenar el modelo base y especializarlo con finetuning.",
            "Construir, preentrenar y especializar: las tres etapas que organizan los "
            "capítulos 2 a 7.",
            credit="Figura 1.9 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        h2("El plan, capítulo a capítulo"),
        table(
            ["Cap.", "Pregunta que responde", "Lo que te llevas"],
            [
                ["<strong>1</strong>", "¿Qué es un LLM y cómo encaja todo?", "El mapa mental de este capítulo"],
                ["<strong>2</strong>", "¿Cómo convertimos texto en números?", "Tokenizador, embeddings y ventana deslizante"],
                ["<strong>3</strong>", "¿Cómo mira el modelo el contexto?", "Self-attention, atención causal y multi-head"],
                ["<strong>4</strong>", "¿Cómo se ensambla GPT?", "Arquitectura completa y generación de texto"],
                ["<strong>5</strong>", "¿Cómo se entrena?", "Bucle de entrenamiento, evaluación y modelo base"],
                ["<strong>6</strong>", "¿Cómo se clasifica texto?", "Finetuning para clasificación"],
                ["<strong>7</strong>", "¿Cómo sigue instrucciones?", "Instruction tuning y alineación"],
            ],
            caption="El roadmap del libro, de los datos a las instrucciones.",
            note=(
                "Los capítulos 2 a 4 preparan datos y arquitectura; el 5 ejecuta el "
                "pretraining; el 6 y el 7 especializan el modelo base."
            ),
        ),
        p(
            "El orden no es casual. Sin tokenizador no hay números; sin embeddings no hay "
            "representaciones; sin atención no hay contexto; sin un bloque GPT completo no "
            "hay nada que entrenar. El pretraining produce un <strong>modelo base</strong> "
            "capaz de completar texto. La clasificación y el instruction tuning lo "
            "especializan para tareas concretas. Cada etapa reutiliza el trabajo de la "
            "anterior. Cada capítulo produce una pieza ejecutable, no solo apuntes."
        ),
        lab("cost"),
        py(
            """
N = 175e9
D = 300e9
FLOPs = 6 * N * D
GPUS = {
    "A100 (40 TFLOPS efectivos)": 40,
    "H100 (150 TFLOPS efectivos)": 150,
}
PRECIO_GPU_HORA = 2.0

print(f"FLOPs de entrenamiento: {FLOPs:.2e}")
for gpu, tflops in GPUS.items():
    horas = FLOPs / (tflops * 1e12 * 3600)
    print(f"{gpu:32} {horas:>12,.0f} GPU-horas  ${horas * PRECIO_GPU_HORA:,.0f}")
print("Regla de oro: FLOPs ≈ 6 · N · D; son estimaciones de orden de magnitud.")
""",
            caption=(
                "La regla 6 · N · D en acción. Cambia N, D o el precio para ver "
                "cuánto crece la factura."
            ),
        ),
        p(
            "El coste de entrenamiento se estima con <strong>FLOPs ≈ 6 · N · D</strong>, "
            "donde <em>N</em> es el número de parámetros y <em>D</em> el número de tokens. "
            "Con esa regla, GPT-3 (175 000 millones de parámetros, 300 000 millones de "
            "tokens) ronda los 2,2 millones de GPU-hora en A100 y unos 4,4 millones de "
            "dólares. El modelo educativo (124 millones de parámetros, 1 000 millones de "
            "tokens) cabe en unas 7 GPU-hora en una RTX 4090 y unos 3,5 dólares. Son "
            "estimaciones de orden de magnitud, no presupuestos: la utilización real, la "
            "interconexión y el precio de la energía cambian la factura."
        ),
        p(
            "Para seguir el libro no necesitas una GPU de datacenter. Los primeros capítulos "
            "y el finetuning pequeño funcionan en un portátil; una GPU acelera el "
            "entrenamiento, pero no es imprescindible para entender el código. Lo que sí "
            "hace falta es constancia y curiosidad crítica: un LLM produce texto plausible, "
            "no necesariamente verdadero. La calculadora del laboratorio permite cambiar "
            "modelo, tokens, hardware y precio para ver el efecto de cada variable."
        ),
        callout(
            "warning",
            "No intentes esto en tu portátil",
            "Entrenar GPT-3 desde cero requiere miles de GPU durante semanas y millones de "
            "dólares. El libro entrena modelos pequeños para que puedas ejecutar el código y "
            "entender cada pieza. Si necesitas un modelo capaz sin pagar el pretraining, "
            "carga pesos abiertos (Llama, Mistral, GPT-2) y finetunea.",
        ),
        check(
            "¿Por qué el libro construye un modelo de ~124 M de parámetros en lugar de "
            "reproducir GPT-3?",
            "Porque el objetivo es entender el pipeline completo con un modelo que se puede "
            "entrenar y depurar en hardware asequible. La arquitectura es la misma; después "
            "se pueden cargar pesos abiertos para evitar el coste del pretraining a gran "
            "escala.",
        ),
        keypoints(
            [
                "El libro construye un GPT pequeño (~124 M) para entender cada componente.",
                "El pipeline va de los tokens y embeddings a la atención y la arquitectura GPT.",
                "El pretraining produce un modelo base; el finetuning lo especializa.",
                "El coste crece con parámetros y tokens: FLOPs ≈ 6 · N · D.",
                "Para usar un modelo capaz sin entrenar desde cero, se reutilizan pesos abiertos.",
            ]
        ),
    ),
    key_points=(
        "Se aprende construyendo un GPT pequeño, no reproduciendo GPT-3.",
        "Tokenización, embeddings, atención y arquitectura preceden al pretraining.",
        "La clasificación y las instrucciones son etapas de finetuning.",
        "El coste de entrenamiento escala con parámetros y tokens (6 · N · D).",
    ),
)
