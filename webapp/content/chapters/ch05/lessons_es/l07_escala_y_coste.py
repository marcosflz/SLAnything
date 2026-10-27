"""Lección 7 · Escala, FLOPs y coste."""

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
)

LESSON = Lesson(
    number=7,
    slug="escala-y-coste",
    title="Escala, FLOPs y coste",
    summary=(
        "La regla 6 · N · D estima el cómputo del preentrenamiento; con el rendimiento "
        "efectivo se traduce en GPU-horas, dinero y requisitos de memoria."
    ),
    minutes=9,
    objectives=(
        "Aplicar la regla FLOPs ≈ 6 · N · D a un modelo pequeño.",
        "Convertir FLOPs en GPU-horas usando el rendimiento efectivo.",
        "Estimar la memoria de pesos, gradientes y estados del optimizador.",
        "Distinguir una estimación de orden de magnitud de un presupuesto real.",
    ),
    blocks=(
        lead(
            "Antes de lanzar un entrenamiento conviene saber si cabe. No hace falta esperar "
            "a la primera factura: con parámetros, tokens y rendimiento del hardware se "
            "obtiene una estimación propia de orden de magnitud. Esa cuenta evita dos extremos: "
            "infravalorar el coste y abandonar, o creer que un portátil va a reproducir GPT-3 "
            "en una tarde."
        ),
        h2("Seis operaciones por par de parámetro y token"),
        p(
            "La regla <strong>FLOPs ≈ 6 · N · D</strong> resume el cómputo de un "
            "entrenamiento transformer. <code>N</code> es el número de parámetros y "
            "<code>D</code> el número de tokens procesados. El factor 6 aproxima las "
            "operaciones por par: en el forward, una multiplicación y una suma por cada "
            "peso y activación; en el backward, aproximadamente el doble para calcular los "
            "gradientes respecto a las activaciones y a los pesos. Es una aproximación, no "
            "una medición: ignora embeddings, normalizaciones, atención cuadrática y "
            "operaciones de memoria."
        ),
        figure(
            "img/ch05/escala-coste.svg",
            "Diagrama con la fórmula 6 · N · D, el ejemplo de 124 millones de parámetros y la comparación de GPU-horas entre modelos.",
            "La misma cuenta permite comparar un modelo didáctico con GPT-3. La escala "
            "cambia en órdenes de magnitud, no en un factor pequeño.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "Para el modelo del libro, con 124 millones de parámetros y 1 000 millones de "
            "tokens, la regla da 6 × 124 × 10⁶ × 10⁹ = 7,44 × 10¹⁷ FLOPs. Si el hardware "
            "sostiene 40 TFLOPS efectivos —40 × 10¹² operaciones por segundo—, el tiempo de "
            "cómputo puro es de unas 5,2 GPU-horas. Es una cifra pequeña comparada con los "
            "grandes modelos, y explica por qué el ejemplo se puede ejecutar en un portátil "
            "en minutos u horas, según el hardware y la implementación."
        ),
        h2("De FLOPs a GPU-horas y euros"),
        p(
            "Una GPU no rinde su pico teórico. La utilización efectiva depende del tamaño de "
            "lote, la memoria, la interconexión y la eficiencia del kernel. Por eso se usa un "
            "rendimiento sostenido, no el número de la caja. La conversión es "
            "<code>GPU-h = FLOPs / (TFLOPS · 10¹² · 3600)</code>. Multiplicando por el precio "
            "por GPU-hora se obtiene el coste de alquiler; quedan fuera la energía, el "
            "almacenamiento, la red y el tiempo de ingeniería."
        ),
        p(
            "El libro cita Llama 2 de 7 000 millones de parámetros: 2 billones de tokens y "
            "184 320 GPU-horas en A100. A 30 dólares por hora de un servidor de 8 A100, la "
            "cuenta aproximada es 184 320 / 8 × 30 ≈ 690 000 dólares. Para GPT-3, con 175 000 "
            "millones de parámetros y 300 000 millones de tokens, la regla da "
            "3,15 × 10²³ FLOPs, unos 2,2 millones de GPU-horas a 40 TFLOPS efectivos. Son "
            "órdenes de magnitud: el número real depende de la infraestructura y de la "
            "época."
        ),
        h2("Memoria: dónde se va"),
        p(
            "El cómputo no es el único límite. En entrenamiento con precisión de 32 bits, "
            "cada parámetro necesita 4 bytes para el peso, 4 para su gradiente y 8 para los "
            "dos momentos de AdamW: 16 bytes por parámetro. El modelo de 124 M ocupa unos "
            "1,98 GB solo en esos estados. Añade activaciones, lotes, buffers y "
            "fragmentación; la memoria real es mayor."
        ),
        p(
            "Las activaciones también cuentan. Una sola instantánea de una activación por "
            "capa, con lote 2, longitud 256, dimensión 768 y 12 capas en fp32, ocupa "
            "2 × 256 × 768 × 12 × 4 bytes ≈ 18,9 MB. El modelo guarda muchas activaciones "
            "intermedias para el backward, y la atención crece con el cuadrado de la longitud. "
            "El <em>gradient checkpointing</em> intercambia memoria por cómputo: recalcula "
            "activaciones durante el backward."
        ),
        callout(
            "warning",
            "Una estimación no es un presupuesto",
            "La regla 6 · N · D y la memoria de 16 bytes por parámetro sirven para comparar "
            "escenarios y descartar ideas inviables. No predicen la factura final: la "
            "utilización real, el precio de la energía, las interrupciones y la "
            "interconexión cambian el resultado. Antes de reservar hardware, mide el "
            "rendimiento efectivo con una ejecución corta y escala desde ahí."
        ),
        py(
            """
N = 124e6
D = 1e9
flops = 6 * N * D
gpu_horas = flops / (40e12 * 3600)

print(f"FLOPs del modelo del libro: {flops:.2e}")
print(f"GPU-horas a 40 TFLOPS: {gpu_horas:.2f}")

N_gpt3 = 175e9
D_gpt3 = 300e9
flops_gpt3 = 6 * N_gpt3 * D_gpt3
gpu_horas_gpt3 = flops_gpt3 / (40e12 * 3600)
print(f"FLOPs de GPT-3: {flops_gpt3:.2e}")
print(f"GPU-horas de GPT-3: {gpu_horas_gpt3:,.0f}")

memoria_pesos = N * 16 / 1e9
activaciones = 2 * 256 * 768 * 12 * 4 / 1e6
print(f"Estados de entrenamiento: {memoria_pesos:.2f} GB")
print(f"Una activación por capa: {activaciones:.1f} MB")
""",
            caption=(
                "Estimación de cómputo, GPU-horas y memoria para el modelo del libro y "
                "GPT-3. Cambia N, D o los TFLOPS para explorar otros escenarios."
            ),
        ),
        lab("cost"),
        p(
            "La calculadora permite mover modelo, tokens, GPUs, precio y rendimiento. "
            "Duplicar parámetros o tokens duplica los FLOPs; añadir GPUs reparte el trabajo, "
            "pero no reduce el coste total si el precio por hora no cambia. La memoria "
            "mostrada cubre pesos, gradientes y estados del optimizador; las activaciones se "
            "suman aparte."
        ),
        check(
            "Un modelo de 1 000 millones de parámetros se entrena con 20 000 millones de "
            "tokens. ¿Cuántos FLOPs estima la regla 6 · N · D?",
            "6 × 10⁹ × 2 × 10¹⁰ = 1,2 × 10²⁰ FLOPs. A 40 TFLOPS efectivos serían "
            "1,2 × 10²⁰ / (40 × 10¹² × 3600) ≈ 833 GPU-horas de cómputo puro. Es una "
            "estimación de orden de magnitud, antes de eficiencia y sobrecargas."
        ),
        keypoints(
            [
                "FLOPs ≈ 6 · N · D estima el cómputo del entrenamiento.",
                "El modelo del libro requiere ≈ 7,44 × 10¹⁷ FLOPs con 1 000 M de tokens.",
                "GPU-horas = FLOPs / (TFLOPS efectivos · 10¹² · 3600).",
                "Llama 2 7B se cita con 184 320 GPU-horas y unos 690 000 dólares.",
                "Entrenar con AdamW en fp32 usa unos 16 bytes por parámetro.",
                "Las activaciones y la atención añaden memoria aparte de los pesos.",
                "Toda estimación debe validarse con una ejecución corta y medida.",
            ]
        ),
    ),
    key_points=(
        "La regla 6 · N · D da una estimación de cómputo, no una medición.",
        "El rendimiento efectivo convierte FLOPs en GPU-horas.",
        "El coste real incluye hardware, energía, red y tiempo de ingeniería.",
        "AdamW en fp32 necesita unos 16 bytes por parámetro.",
        "Las activaciones y la atención condicionan la memoria del lote.",
        "Gradient checkpointing cambia memoria por cómputo adicional.",
    ),
)
