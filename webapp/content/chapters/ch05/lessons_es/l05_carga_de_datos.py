"""Lección 5 · Data loaders y batches."""

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
    slug="carga-de-datos",
    title="Data loaders y batches",
    summary=(
        "El cargador convierte un texto continuo en ventanas de tokens y las agrupa en "
        "lotes; stride, shuffling y drop_last cambian lo que ve el modelo."
    ),
    minutes=9,
    objectives=(
        "Explicar cómo se construyen las ventanas de entrada y de objetivo.",
        "Distinguir context length de stride y describir su efecto.",
        "Elegir drop_last y shuffle de forma distinta para entrenamiento y validación.",
        "Interpretar las formas y el número de lotes de un corpus pequeño.",
    ),
    blocks=(
        lead(
            "El modelo no lee un libro de principio a fin como una persona. El cargador "
            "corta el texto en ventanas, las agrupa en lotes y las entrega en un orden "
            "controlado. Esa preparación parece mecánica, pero decide cuánta información "
            "recibe cada paso y cuánto se repite el corpus."
        ),
        h2("Ventanas y desplazamiento"),
        p(
            "Una ventana es una secuencia de <code>T</code> tokens. Su objetivo es la misma "
            "secuencia desplazada una posición: si la ventana contiene los tokens 10 a 265, "
            "el objetivo contiene los tokens 11 a 266. Así cada posición de la ventana "
            "enseña a predecir la siguiente. El <strong>stride</strong> o desplazamiento "
            "indica cuántos tokens avanza el inicio de una ventana a la siguiente. En el "
            "libro, la longitud de contexto y el stride valen 256, de modo que las ventanas "
            "no se solapan. Un stride menor produciría más ventanas y más ejemplos, a cambio "
            "de repetir texto y aumentar el coste por época."
        ),
        p(
            "La longitud de contexto no es solo un límite de memoria: también define cuánto "
            "contexto ve el modelo en cada predicción. Con 256 tokens, el modelo puede "
            "condicionar el siguiente token en los 256 anteriores. Al aumentar la longitud, "
            "crece el coste de atención y de activaciones. Por eso el ejemplo del libro "
            "reduce la configuración de GPT-2 de 1 024 a 256 tokens para que el entrenamiento "
            "quepa en un portátil. Al final del capítulo, al cargar los pesos de GPT-2, se "
            "vuelve a 1 024."
        ),
        h2("El split y los lotes"),
        p(
            "Antes de crear los cargadores, el texto se divide en entrenamiento y validación. "
            "El libro usa un 90 % para entrenar y un 10 % para validar. El cuento <em>The "
            "Verdict</em> tiene 20 479 caracteres y 5 145 tokens; con ventanas de 256 y lote "
            "de 2, el cargador de entrenamiento produce 9 lotes y el de validación, 1. Son "
            "números pequeños porque el objetivo es ejecutar el ejemplo en minutos, no "
            "reproducir la escala de un LLM comercial."
        ),
        table(
            ["Ajuste", "Entrenamiento", "Validación", "Motivo"],
            [
                ["batch_size", "2", "2", "Mismo formato de tensor en ambos"],
                ["max_length", "256", "256", "Longitud de contexto del modelo"],
                ["stride", "256", "256", "Ventanas sin solapamiento"],
                ["shuffle", "True", "False", "Mezclar en train; conservar el orden al evaluar"],
                ["drop_last", "True", "False", "Formas estables en train; no perder datos en val"],
            ],
            caption="Configuración de los data loaders del capítulo 5.",
            note=(
                "El valor de batch_size=2 es didáctico. En producción son frecuentes los "
                "lotes de 1 024 o más, según la memoria disponible."
            ),
        ),
        p(
            "El <strong>shuffling</strong> mezcla las ventanas al inicio de cada época. Sin "
            "mezcla, el orden fijo puede introducir correlaciones entre lotes consecutivos: "
            "el optimizador ve primero todo un capítulo y luego otro, y la trayectoria se "
            "resiente. En validación no se mezcla, para que la evaluación sea reproducible y "
            "comparable entre épocas. El parámetro <code>drop_last</code> se activa en "
            "entrenamiento para descartar un último lote incompleto; así todos los lotes "
            "tienen la misma forma y no se hace una actualización con muy pocos ejemplos. En "
            "validación se deja en <code>False</code> para no perder esa parte del corpus."
        ),
        callout(
            "note",
            "El texto también puede tener longitudes variables",
            "El libro usa ventanas de longitud fija por simplicidad y eficiencia. En la "
            "práctica, entrenar con secuencias de longitudes variables puede ayudar a "
            "generalizar a entradas más diversas, siempre que el lote se rellene o se "
            "empaquete con cuidado. La decisión afecta al rendimiento y a la calidad; no hay "
            "una única respuesta correcta."
        ),
        h2("Qué puede salir mal"),
        p(
            "Un error frecuente es construir las ventanas con el objetivo desalineado: si se "
            "usa la misma secuencia como entrada y como objetivo, el modelo aprende a copiar "
            "y la pérdida puede bajar de forma engañosa. Otro error es mezclar el conjunto de "
            "validación con el de entrenamiento; entonces la métrica de validación deja de "
            "medir generalización. También conviene revisar las formas: entrada y objetivo "
            "deben tener <code>[B, T]</code>, y los logits del modelo, "
            "<code>[B, T, V]</code>. Una comprobación de una línea antes de entrenar ahorra "
            "horas de depuración."
        ),
        p(
            "El número de trabajadores del cargador, <code>num_workers</code>, controla "
            "cuántos procesos preparan lotes en paralelo. En el ejemplo se usa 0 porque el "
            "corpus es diminuto y crear procesos costaría más que el trabajo útil. En un "
            "corpus grande, unos pocos trabajadores evitan que la GPU espere datos. La regla "
            "es medir: si el uso de GPU baja entre pasos, el cuello de botella puede estar en "
            "el cargador."
        ),
        check(
            "¿Por qué el data loader de entrenamiento usa drop_last=True y el de validación "
            "drop_last=False?",
            "En entrenamiento interesa que todos los lotes tengan la misma forma y evitar "
            "una actualización con un lote residual muy pequeño; por eso se descarta el "
            "último lote incompleto. En validación interesa evaluar todo el conjunto, así que "
            "se conserva ese lote aunque tenga menos ejemplos."
        ),
        keypoints(
            [
                "Cada ventana contiene una secuencia y su objetivo es la misma secuencia desplazada.",
                "El stride decide el solapamiento entre ventanas consecutivas.",
                "El libro divide el corpus al 90 % para entrenar y al 10 % para validar.",
                "The Verdict tiene 20 479 caracteres y 5 145 tokens en el ejemplo.",
                "Shuffle se activa en entrenamiento y se desactiva en validación.",
                "drop_last=True evita lotes incompletos en entrenamiento.",
                "Comprueba siempre las formas [B, T] de entrada y objetivo.",
            ]
        ),
    ),
    key_points=(
        "Las ventanas convierten texto continuo en pares entrada-objetivo.",
        "El stride controla el solapamiento y el número de ejemplos.",
        "Entrenamiento y validación usan ajustes distintos de shuffle y drop_last.",
        "Las formas de entrada y objetivo deben ser [B, T].",
        "El cargador no debe filtrar datos de validación al entrenamiento.",
        "num_workers se elige midiendo el coste de preparación de lotes.",
    ),
)
