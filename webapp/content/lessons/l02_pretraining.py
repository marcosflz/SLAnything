"""Lección 2 · Las dos etapas."""

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
    number=2,
    slug="pretraining-y-finetuning",
    title="Las dos etapas",
    summary=(
        "El pretraining enseña el idioma con texto sin etiquetar; el finetuning "
        "especializa el modelo con datos etiquetados y más pequeños."
    ),
    minutes=10,
    objectives=(
        "Explicar la predicción del siguiente token y por qué es autosupervisada.",
        "Distinguir el modelo base del modelo especializado mediante finetuning.",
        "Diferenciar finetuning de prompt engineering: cambiar pesos frente a cambiar el contexto.",
        "Construir pares entrada→objetivo a partir de una secuencia de tokens.",
    ),
    blocks=(
        lead(
            "Casi todos los LLM modernos se construyen en dos etapas: una cara y general, "
            "otra comparativamente barata y específica. Entender qué aprende el modelo en "
            "cada una evita dos errores frecuentes: creer que ya «sabe» seguir instrucciones "
            "desde el primer día y confundir ajustar los pesos con escribir un buen prompt."
        ),
        h2("La primera etapa: pretraining"),
        p(
            "En el pretraining, el modelo recorre un corpus enorme —páginas web, libros, "
            "Wikipedia, código— y se entrena para una única tarea: predecir el siguiente "
            "token. No hay un humano anotando cada frase. Si la secuencia es «El gato duerme "
            "sobre el sofá», la entrada es «El gato duerme sobre el» y el objetivo es «sofá». "
            "La etiqueta es el propio texto: entrada y objetivo salen de la misma secuencia, "
            "solo que desplazados una posición. Esto es <strong>aprendizaje "
            "autosupervisado</strong>: el dato trae consigo su propia respuesta. En la "
            "práctica, el modelo no procesa una frase cada vez, sino secuencias largas, "
            "y calcula una predicción en todas las posiciones a la vez; una máscara causal le "
            "impide mirar tokens futuros. De cada pasaje se obtienen muchísimos ejemplos sin "
            "coste de etiquetado. El resultado es un <strong>modelo base</strong> o "
            "<em>foundation model</em>: sabe completar texto y ha absorbido gramática, estilos "
            "y una parte considerable de conocimiento factual, pero todavía no es un asistente "
            "fiable. Para acertar en contextos diversos, la red debe aprender regularidades que "
            "van mucho más allá del token inmediato: la predicción es la excusa, la "
            "representación es el premio."
        ),
        figure(
            "img/ch01/fig_1_3_pretraining_finetuning.png",
            "Diagrama de las dos etapas: pretraining con texto sin etiquetar y finetuning con un dataset etiquetado.",
            "El pretraining usa texto sin etiquetar y la tarea de predecir el siguiente token. "
            "El finetuning parte de ese modelo base y usa un dataset etiquetado más pequeño.",
            credit="Figura 1.3 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        p(
            "El <strong>finetuning</strong> ajusta los pesos del modelo base con un dataset más "
            "pequeño y etiquetado. Hay dos variantes habituales. El <em>instruction tuning</em> "
            "usa pares de instrucción y respuesta —«Resume este informe» → resumen correcto— y "
            "enseña al modelo a seguir órdenes. La clasificación usa texto y una etiqueta —un "
            "correo y «spam» o «no spam»— y lo especializa en una categoría concreta. En ambos "
            "casos los pesos cambian; el modelo no se limita a leer ejemplos en el prompt. En la "
            "práctica no se parte de cero: se reutilizan pesos abiertos y se adaptan, mucho más "
            "barato que preentrenar. ChatGPT añade además un proceso de alineación con "
            "retroalimentación humana (RLHF), que veremos más adelante."
        ),
        callout(
            "info",
            "No confundas tres cosas",
            "El <strong>pretraining</strong> aprende el idioma con datos masivos y etiquetas "
            "gratuitas. El <strong>finetuning</strong> especializa con datos pequeños y "
            "etiquetas caras. El <strong>prompt engineering</strong> —incluido el few-shot— no "
            "toca los pesos: coloca instrucciones y ejemplos en el contexto para condicionar la "
            "respuesta. En few-shot, el modelo «aprende» solo mientras dura la conversación; al "
            "cerrarla, no queda rastro en los pesos. Lo veremos en la lección 6."
        ),
        table(
            ["Dimensión", "Pretraining", "Finetuning", "Prompt engineering"],
            [
                ["Qué cambia", "Los pesos, desde cero", "Los pesos, desde un modelo base", "Nada: solo el contexto"],
                ["Datos", "Corpus enorme sin etiquetar", "Dataset pequeño y etiquetado", "Instrucciones y ejemplos en el prompt"],
                ["Objetivo", "Predecir el siguiente token", "Seguir instrucciones o clasificar", "Resolver la tarea en el momento"],
                ["Coste", "Muy alto", "Moderado", "Casi nulo"],
            ],
            caption="Tres formas de adaptar un modelo. Solo las dos primeras modifican los pesos.",
        ),
        py(
            """
tokens = ["El", "gato", "duerme", "sobre", "el", "sofá", "."]

pares = []
for posicion in range(1, len(tokens)):
    entrada = tokens[:posicion]
    objetivo = tokens[posicion]
    pares.append((entrada, objetivo))

for entrada, objetivo in pares[:3]:
    print(" ".join(entrada), "->", objetivo)
print(f"\\n{len(pares)} pares construidos con una sola frase.")
""",
            caption=(
                "Cada posición genera un par; el objetivo ya estaba en el texto. "
                "Ejecuta el ejemplo y cambia la frase."
            ),
        ),
        p(
            "En el laboratorio «Etiquetas» vas a fabricar esos pares a mano. Eliges una frase, "
            "marcas qué token actúa como objetivo y compruebas que la entrada es todo lo "
            "anterior. El ejercicio hace visible lo que suele quedar oculto: el pretraining no "
            "necesita anotadores porque la supervisión viaja dentro del propio texto."
        ),
        lab("labels"),
        check(
            "¿Por qué decimos que el pretraining es autosupervisado si nadie etiqueta el corpus?",
            "Porque la etiqueta se obtiene del propio dato: el token que sigue en la secuencia. "
            "Entrada y objetivo son la misma frase desplazada una posición, así que cada "
            "fragmento de texto genera ejemplos sin anotación humana.",
        ),
        keypoints(
            [
                "El pretraining predice el siguiente token sobre un corpus enorme y sin etiquetar.",
                "La etiqueta es el propio texto: entrada y objetivo salen de la misma secuencia.",
                "El finetuning ajusta los pesos con datos etiquetados más pequeños para especializar el modelo.",
                "Few-shot y prompt engineering no cambian los pesos; el finetuning sí.",
            ]
        ),
    ),
    key_points=(
        "El pretraining es autosupervisado: la etiqueta es el siguiente token del propio texto.",
        "El modelo base aprende lenguaje; el finetuning lo especializa con datos etiquetados.",
        "El finetuning modifica pesos; el prompt engineering solo condiciona el contexto.",
        "Few-shot no es entrenamiento: los ejemplos desaparecen al cerrar la conversación.",
    ),
)
