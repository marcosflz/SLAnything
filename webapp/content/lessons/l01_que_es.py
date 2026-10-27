"""Lección 1 · ¿Qué es un LLM?"""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
    quote,
    table,
)

LESSON = Lesson(
    number=1,
    slug="que-es-un-llm",
    title="¿Qué es un LLM?",
    summary=(
        "Un modelo de lenguaje es una red neuronal entrenada para predecir el siguiente "
        "token. Aquí entendemos qué significa “grande” y de dónde viene esta tecnología."
    ),
    minutes=10,
    objectives=(
        "Definir qué es un large language model sin recurrir a la magia.",
        "Explicar las dos dimensiones de “grande”: parámetros y datos.",
        "Situar los LLM dentro de la jerarquía de la inteligencia artificial.",
        "Estimar la memoria que ocupa un modelo según su precisión.",
    ),
    blocks=(
        lead(
            "Antes de definir nada, hagamos lo que hace un modelo de lenguaje. Lee esta "
            "frase y completa el final en tu cabeza: <em>«El sol se ocultaba detrás de las "
            "montañas y el cielo se tiñó de…»</em>."
        ),
        p(
            "Probablemente pensaste en <strong>naranja</strong>, <strong>rojo</strong> o "
            "<strong>púrpura</strong>. No aplicaste una regla explícita: tu experiencia con "
            "el lenguaje produjo una distribución de finales plausibles. Ese es, en esencia, "
            "el motor de un LLM."
        ),
        callout(
            "info",
            "La idea central del capítulo",
            "Un LLM es una red neuronal enorme entrenada para <strong>predecir el siguiente "
            "token</strong>. Traducir, resumir, programar o conversar emergen de esa tarea y "
            "de la escala.",
        ),
        h2("Una definición útil"),
        p(
            "Un <strong>large language model</strong> es una red neuronal profunda entrenada "
            "con cantidades masivas de texto para <strong>entender, generar y responder</strong> "
            "lenguaje humano. Cuando decimos que “entiende”, queremos decir que procesa y "
            "genera texto de forma coherente y contextualmente relevante; no que tenga "
            "conciencia ni comprensión humana."
        ),
        p(
            "La palabra “grande” se refiere a dos cosas a la vez: los <strong>parámetros</strong> "
            "—los pesos ajustables de la red— y los <strong>datos</strong> con los que se "
            "entrena. Un modelo con muchos parámetros pero pocos datos no aprende bien; uno "
            "con muchos datos pero poca capacidad tampoco."
        ),
        table(
            ["Dimensión", "Qué significa", "Ejemplo"],
            [
                ["<strong>Parámetros</strong>", "Pesos ajustables de la red", "GPT-3: 175 000 millones"],
                ["<strong>Datos</strong>", "Corpus de entrenamiento", "GPT-3: ~300 000 millones de tokens"],
            ],
            caption="Las dos dimensiones de “grande”.",
        ),
        h2("La jerarquía de la IA"),
        p(
            "Los LLM no son un campo aparte: son una aplicación concreta de deep learning. "
            "La figura 1.1 del libro sitúa la IA, el machine learning, el deep learning, la "
            "IA generativa y los LLM en capas sucesivas."
        ),
        figure(
            "img/ch01/fig_1_1_jerarquia_ia.png",
            "Diagrama de la jerarquía: inteligencia artificial, machine learning, deep learning, IA generativa y LLM.",
            "La IA es el paraguas; el machine learning son algoritmos que aprenden de datos; "
            "el deep learning usa redes de varias capas; GenAI crea contenido nuevo; los LLM "
            "son un caso particular centrado en texto.",
            credit="Figura 1.1 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        p(
            "La diferencia práctica entre machine learning tradicional y deep learning está "
            "en las características. En ML tradicional, una persona diseña a mano las "
            "variables relevantes: frecuencia de “gratis”, número de signos de exclamación, "
            "mayúsculas. En deep learning, la red aprende esas representaciones a partir de "
            "los datos."
        ),
        h2("El lenguaje como interfaz"),
        p(
            "La razón por la que los LLM se extendieron tan rápido es que <strong>el lenguaje "
            "es la interfaz de casi todo</strong>. Si una tarea se puede formular como “leer "
            "texto y producir texto”, un modelo puede intentarla sin cambiar de arquitectura. "
            "La figura 1.2 muestra la interfaz conversacional: el usuario escribe una "
            "instrucción y el modelo produce una respuesta."
        ),
        figure(
            "img/ch01/fig_1_2_chatgpt.png",
            "Interfaz conversacional de ChatGPT: el usuario escribe una instrucción y el modelo responde.",
            "La interfaz es simple; la responsabilidad está en el modelo y en cómo se usa su "
            "respuesta. Una salida fluida no es lo mismo que una salida verdadera.",
            credit="Figura 1.2 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
        ),
        table(
            ["Tarea", "Entrada", "Salida", "Ejemplo"],
            [
                ["Traducción", "Texto en un idioma", "Texto en otro", "«Buenos días» → «Good morning»"],
                ["Resumen", "Documento largo", "Versión breve", "Resumen de un contrato"],
                ["Sentimiento", "Reseña", "Etiqueta", "Positivo / negativo / neutro"],
                ["Generación", "Instrucción o inicio", "Texto nuevo", "Artículo, cuento, código"],
                ["Preguntas y respuestas", "Pregunta + contexto", "Respuesta", "Soporte técnico"],
                ["Asistentes", "Conversación", "Respuesta", "ChatGPT, Gemini, Copilot"],
            ],
            caption="Aplicaciones típicas. La misma arquitectura, distintas instrucciones.",
        ),
        callout(
            "tip",
            "La idea que hay que llevarse",
            "El mismo modelo base puede traducir, resumir o clasificar <strong>sin "
            "reentrenarse</strong>: basta con cambiar el prompt. Eso es posible porque durante "
            "el pretraining aprendió patrones generales del lenguaje, no una tarea única.",
        ),
        check(
            "¿Por qué el mismo modelo puede traducir y resumir sin reentrenarse?",
            "Porque el pretraining le dio patrones generales del lenguaje y la tarea se "
            "expresa como texto de entrada → texto de salida. La instrucción en el prompt "
            "selecciona el comportamiento; no hace falta actualizar los pesos.",
        ),
        h2("La escala tiene un precio"),
        p(
            "Cada parámetro ocupa memoria. En inferencia con precisión de 16 bits, un modelo "
            "necesita aproximadamente <strong>2 bytes por parámetro</strong> solo para los "
            "pesos. GPT-3, con 175 000 millones de parámetros, ocupa unos <strong>350 GB</strong> "
            "antes de contar activaciones y caché. Entrenar es aún más caro: hay que guardar "
            "gradientes y estados del optimizador."
        ),
        table(
            ["Modelo", "Parámetros", "Pesos 16 bits", "Pesos 8 bits", "Pesos 4 bits", "Entrenamiento aprox."],
            [
                ["GPT-2 small (el del libro)", "124 M", "0,25 GB", "0,12 GB", "0,06 GB", "2 GB"],
                ["GPT-2 XL", "1,5 B", "3 GB", "1,5 GB", "0,75 GB", "24 GB"],
                ["Llama 3.1 8B", "8 B", "16 GB", "8 GB", "4 GB", "128 GB"],
                ["Llama 3.1 70B", "70 B", "140 GB", "70 GB", "35 GB", "1,1 TB"],
                ["GPT-3", "175 B", "350 GB", "175 GB", "87,5 GB", "2,8 TB"],
            ],
            caption="Órdenes de magnitud, no medidas exactas.",
            note=(
                "2 bytes por parámetro en 16 bits, 1 en 8 bits y 0,5 en 4 bits. Para "
                "entrenamiento se estiman unos 16 bytes por parámetro (pesos fp32, gradientes "
                "y estados de Adam). Las activaciones y la caché añaden memoria adicional."
            ),
        ),
        lab("memory"),
        py(
            """
MODELOS = {
    "GPT-2 small (124 M)": 124e6,
    "GPT-2 XL (1,5 B)": 1.5e9,
    "Llama 3.1 8B": 8e9,
    "GPT-3 (175 B)": 175e9,
}

def memoria_gb(parametros, bytes_por_parametro):
    return parametros * bytes_por_parametro / 1e9

print(f"{'Modelo':24} {'16 bits':>9} {'8 bits':>9} {'4 bits':>9}")
print("-" * 58)
for nombre, parametros in MODELOS.items():
    print(
        f"{nombre:24} "
        f"{memoria_gb(parametros, 2):>7.1f} GB "
        f"{memoria_gb(parametros, 1):>7.1f} GB "
        f"{memoria_gb(parametros, 0.5):>7.1f} GB"
    )
""",
            caption=(
                "Calcula la memoria de los pesos según la precisión. Cambia los "
                "modelos o añade uno propio y vuelve a ejecutar."
            ),
        ),
        callout(
            "tip",
            "Antes de seguir · 30 segundos",
            "¿Por qué crees que predecir la siguiente palabra puede enseñar gramática o "
            "razonamiento? Guarda tu hipótesis; la revisaremos al final del capítulo.",
        ),
        check(
            "¿Qué dos cosas miden el “large” de un large language model?",
            "El número de parámetros (la capacidad de la red) y la cantidad y diversidad de "
            "datos de entrenamiento. Ninguna de las dos basta por separado.",
        ),
        quote(
            "Un LLM no devuelve una única palabra: devuelve una probabilidad para cada token "
            "posible y elige una.",
            "Idea que desarrollaremos en la lección 5",
        ),
        keypoints(
            [
                "Un LLM es una red neuronal entrenada para predecir el siguiente token.",
                "“Grande” significa muchos parámetros y muchos datos, no una sola cosa.",
                "Los LLM son deep learning aplicado al lenguaje, no un campo separado.",
                "La escala tiene un coste directo en memoria y cómputo.",
            ]
        ),
    ),
    key_points=(
        "Un LLM es una red neuronal entrenada para predecir el siguiente token.",
        "“Grande” significa muchos parámetros y muchos datos.",
        "Los LLM son una aplicación de deep learning, no un campo aparte.",
        "La escala se paga en memoria y cómputo.",
    ),
)
