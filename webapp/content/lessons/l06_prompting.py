"""Lección 6 · Zero-shot y few-shot."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    code,
    figure,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=6,
    slug="zero-shot-y-few-shot",
    title="Zero-shot y few-shot",
    summary=(
        "Cómo pedir tareas nuevas sin tocar los pesos: la instrucción y los ejemplos "
        "del prompt condicionan la respuesta del modelo."
    ),
    minutes=10,
    objectives=(
        "Distinguir zero-shot, one-shot y few-shot.",
        "Explicar por qué los ejemplos del prompt no equivalen a un entrenamiento.",
        "Construir un prompt con instrucciones y ejemplos resueltos.",
        "Relacionar el comportamiento emergente con la escala y la diversidad de datos.",
    ),
    blocks=(
        lead(
            "Un modelo base no nace sabiendo obedecer. Pero puede resolver una tarea que "
            "nunca vio si se la formulamos en el prompt: una instrucción, unos ejemplos y "
            "una entrada. La clave es que el contexto condiciona la siguiente predicción."
        ),
        p(
            "Pedir una tarea <strong>zero-shot</strong> es describirla sin ningún ejemplo: "
            "«Clasifica el sentimiento de esta reseña». <strong>One-shot</strong> añade un "
            "ejemplo resuelto y <strong>few-shot</strong>, unos pocos. En los tres casos el "
            "mecanismo es idéntico: el texto del prompt entra en la ventana de contexto y "
            "desplaza la distribución de probabilidad hacia el formato deseado. No hay "
            "descenso de gradiente ni actualización de pesos. Es un aprendizaje <em>en "
            "contexto</em>, temporal: si cierras la conversación, desaparece. Un ejemplo "
            "cotidiano: pedir «traduce esta frase» sin más es zero-shot; enseñar dos "
            "traducciones antes de la frase objetivo es few-shot. One-shot es el caso "
            "intermedio, con un solo ejemplo. La frontera entre one-shot y few-shot es "
            "difusa; lo importante es cuántos ejemplos ve el modelo, no la etiqueta."
        ),
        figure(
            "img/ch01/fig_1_6_zero_few_shot.png",
            "Comparación entre completar texto, resolver una tarea zero-shot y resolverla con ejemplos few-shot.",
            "En few-shot, los ejemplos viven dentro del propio input. El modelo no se "
            "reentrena: cambia lo que ve antes de responder.",
            credit="Figura 1.6 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        callout(
            "warning",
            "Few-shot no es finetuning",
            "En few-shot el modelo <strong>no modifica sus pesos</strong>. Los ejemplos "
            "ocupan la ventana de contexto y condicionan la probabilidad de la siguiente "
            "respuesta. El finetuning, en cambio, entrena con datos etiquetados y cambia los "
            "pesos de forma permanente. Confundir ambos conceptos lleva a esperar una "
            "memoria que el prompt no proporciona. El finetuning exige datos, cómputo y "
            "evaluación; few-shot solo exige espacio en el contexto.",
        ),
        h2("Construir el prompt"),
        code(
            "text",
            """
# Zero-shot
Clasifica el sentimiento como positivo, negativo o neutro.
Reseña: «El producto llegó roto y el soporte no respondió.»
Sentimiento:

# Few-shot
Clasifica el sentimiento como positivo, negativo o neutro.
Reseña: «Me encanta este producto.»
Sentimiento: positivo
Reseña: «No funciona y llegó tarde.»
Sentimiento: negativo
Reseña: «Es un producto normal.»
Sentimiento: neutro
Reseña: «El producto llegó roto y el soporte no respondió.»
Sentimiento:
""",
            caption="La misma tarea con cero ejemplos y con tres. El formato de salida se aprende del propio patrón.",
        ),
        lab("prompt"),
        py(
            """
INSTRUCCION = "Clasifica el sentimiento como positivo, negativo o neutro."
EJEMPLOS = [
    ("Me encanta este producto.", "positivo"),
    ("No funciona y llegó tarde.", "negativo"),
    ("Es un producto normal.", "neutro"),
]
ENTRADA = "El envío fue rápido, pero la caja llegó rota."

lineas = [f"Instrucción: {INSTRUCCION}"]
for i, (entrada, salida) in enumerate(EJEMPLOS, start=1):
    lineas.append(f"\\nEjemplo {i}:\\nEntrada: {entrada}\\nSalida: {salida}")
lineas.append(f"\\nEntrada: {ENTRADA}\\nSalida:")
prompt = "\\n".join(lineas).strip()

print(prompt)
print(f"\\nTokens aproximados del prompt: {len(prompt.split())}")
""",
            caption=(
                "Construye un prompt few-shot. Prueba a quitar ejemplos, cambiar "
                "la instrucción o añadir un ejemplo mal etiquetado."
            ),
        ),
        p(
            "Un buen prompt fija el formato de salida, da ejemplos representativos y evita "
            "instrucciones ambiguas. El orden también importa: los ejemplos más parecidos a "
            "la entrada objetivo suelen ayudar más. Coloca la instrucción al principio, deja "
            "la entrada objetivo al final y marca con claridad dónde empieza la respuesta, "
            "por ejemplo con «Salida:». Y hay un límite práctico: cada ejemplo consume tokens "
            "de la ventana de contexto, así que más no siempre es mejor; llega un punto en que "
            "el coste crece y la señal se diluye. Un ejemplo mal etiquetado, además, enseña el "
            "error. Con documentos largos, a veces conviene resumir o recuperar solo los "
            "fragmentos relevantes antes de construir el prompt."
        ),
        h2("Comportamiento emergente"),
        p(
            "GPT fue entrenado para predecir texto, no para traducir. Sin embargo, cuando el "
            "modelo es suficientemente grande y ha visto suficientes textos multilingües, la "
            "traducción <strong>emerge</strong> como una capacidad que nadie programó de "
            "forma explícita. Lo mismo ocurre con resumir, corregir ortografía o resolver "
            "problemas sencillos. Emergente no significa mágico: la capacidad aparece como "
            "consecuencia de la escala y de la diversidad de los datos. Que sea difícil de "
            "predecir no la vuelve inexplicable, y muchas capacidades «emergentes» dependen "
            "de cómo se evalúan; la frontera sigue siendo objeto de debate. Esta es la "
            "observación que popularizó GPT-3: un mismo modelo, sin reentrenarse, puede "
            "resolver tareas nuevas con unos pocos ejemplos. No es una capacidad ilimitada: "
            "depende de la calidad de los datos y del tamaño del modelo. En lugar de programar "
            "una tarea por cada objetivo, se aprovechan representaciones generales del "
            "lenguaje. La consecuencia práctica es enorme: un solo modelo puede resolver "
            "tareas muy distintas sin un modelo distinto para cada una."
        ),
        check(
            "¿Qué diferencia hay entre few-shot y finetuning?",
            "Few-shot añade ejemplos al contexto y no altera los pesos; el efecto dura lo que "
            "dura la conversación. El finetuning entrena con datos etiquetados y modifica los "
            "pesos de forma permanente.",
        ),
        keypoints(
            [
                "Zero-shot da solo la instrucción; one-shot y few-shot añaden ejemplos.",
                "Los ejemplos condicionan el contexto, no actualizan los pesos.",
                "Few-shot es temporal; el finetuning es un cambio permanente en los pesos.",
                "El comportamiento emergente surge de la escala y de datos diversos, no de una tarea programada.",
                "Más ejemplos consumen más contexto y no garantizan mejores respuestas.",
            ]
        ),
    ),
    key_points=(
        "Zero-shot, one-shot y few-shot se distinguen por el número de ejemplos del prompt.",
        "Few-shot no entrena: condiciona la siguiente predicción con el contexto.",
        "El finetuning sí cambia los pesos y persiste fuera de la conversación.",
        "La escala y los datos multilingües explican capacidades emergentes como traducir.",
    ),
)
