"""Lección 1 · Instrucciones y ajuste supervisado."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
)

LESSON = Lesson(
    number=1,
    slug="instrucciones-y-sft",
    title="Instrucciones y SFT",
    summary=(
        "El ajuste supervisado de instrucciones enseña a un modelo preentrenado a "
        "responder a peticiones concretas sin perder la tarea de predecir el siguiente token."
    ),
    minutes=11,
    objectives=(
        "Definir el ajuste supervisado de instrucciones y situarlo tras el pretraining.",
        "Explicar qué cambia y qué permanece respecto al entrenamiento original.",
        "Reconocer los objetivos realistas de un SFT pequeño y sus límites.",
        "Distinguir el ajuste completo del ajuste eficiente en parámetros.",
    ),
    blocks=(
        lead(
            "Un modelo preentrenado sabe continuar un texto, pero no necesariamente "
            "obedecer. Si le pides que convierta una frase a pasiva, puede responder con "
            "más instrucciones, repetir el enunciado o inventar un formato. El ajuste "
            "supervisado de instrucciones, o <strong>SFT</strong> por sus siglas en inglés, "
            "le enseña, con ejemplos, qué se espera cuando alguien le pide algo."
        ),
        p(
            "El pretraining optimiza una tarea muy simple: dado un fragmento de texto, "
            "predecir el token siguiente. Con suficientes datos y parámetros, esa tarea "
            "produce un modelo que conoce gramática, estilos y una parte del mundo. Pero el "
            "objetivo no distingue entre una pregunta, una orden y un párrafo cualquiera. "
            "El modelo aprende a continuar, no a colaborar. El SFT conserva exactamente esa "
            "función de pérdida y cambia la distribución de los datos: ahora los ejemplos "
            "tienen la forma de una petición seguida de una respuesta deseada."
        ),
        h2("Qué añade el ajuste supervisado"),
        p(
            "En el experimento del libro se usan <strong>1.100 pares</strong> de instrucción "
            "y respuesta, divididos en 85 % para entrenamiento, 10 % para prueba y 5 % para "
            "validación. Cada par se formatea con una plantilla, se tokeniza y se convierte "
            "en un ejemplo de «siguiente token» donde los tokens de la respuesta son el "
            "objetivo. No hay una arquitectura nueva ni un optimizador distinto: hay un "
            "conjunto de datos distinto y una máscara que decide qué posiciones cuentan. "
            "Esa continuidad es la clave para entender el método y también sus límites."
        ),
        p(
            "El efecto se ve en la práctica. Antes del ajuste, el GPT-2 mediano del libro "
            "genera una sección «Response» que repite la frase original y vuelve a copiar "
            "parte de la instrucción. Después de dos épocas, convierte «The chef cooks the "
            "meal every day» en «The meal is cooked every day by the chef». No ha aprendido "
            "pasiva como una regla gramatical explícita: ha ajustado su distribución para "
            "que, tras esa instrucción y ese formato, la continuación probable sea una "
            "respuesta útil. El SFT moldea el comportamiento; no instala un motor de reglas."
        ),
        callout(
            "warning",
            "SFT no es una garantía de verdad",
            "El ajuste enseña <strong>formato, estilo y pautas de respuesta</strong>. No "
            "convierte al modelo en una base de datos fiable ni elimina las alucinaciones. "
            "Un modelo puede responder con seguridad y equivocarse. La verificación factual, "
            "el filtrado de datos y la evaluación siguen siendo imprescindibles.",
        ),
        h2("Objetivos y límites"),
        p(
            "Un SFT bien planteado persigue cuatro cosas: que el modelo reconozca una "
            "instrucción, que produzca una respuesta en el formato esperado, que aprenda a "
            "terminar con el token de fin de secuencia y que generalice a peticiones no "
            "vistas. No persigue, por sí solo, garantizar la veracidad, la seguridad ni el "
            "conocimiento actualizado. Tampoco sustituye al pretraining: lo especializa. "
            "Cuanto más estrecho es el conjunto de instrucciones, más riesgo hay de que el "
            "modelo pierda capacidades generales o se adapte en exceso a un estilo concreto."
        ),
        p(
            "El coste también importa. El libro ajusta GPT-2 mediano, con 355 millones de "
            "parámetros, porque el modelo pequeño de 124 millones se queda corto para obtener "
            "resultados cualitativamente satisfactorios. En una GPU A100, dos épocas tardan "
            "alrededor de 0,86 minutos; en una CPU Apple M3, unos 15,78 minutos. Son cifras "
            "del experimento del libro, no una promesa para cualquier equipo. Si el "
            "presupuesto aprieta, el ajuste eficiente en parámetros, como LoRA, reduce el "
            "número de pesos entrenables y el coste de memoria."
        ),
        bullets(
            [
                "<strong>Datos:</strong> pares claros, diversos y con respuestas correctas; "
                "la calidad pesa más que rellenar miles de filas.",
                "<strong>Cómputo:</strong> el ajuste completo actualiza todos los pesos; "
                "LoRA entrena adaptadores pequeños y abarata el proceso.",
                "<strong>Evaluación:</strong> la pérdida baja no basta; hay que leer "
                "respuestas y compararlas con referencias en un conjunto reservado.",
            ]
        ),
        check(
            "¿Qué comparte el SFT con el pretraining y qué cambia?",
            "Comparte la función de pérdida de siguiente token y el optimizador. Cambian los "
            "datos —pares de instrucción y respuesta— y la máscara, que decide qué tokens de "
            "la respuesta contribuyen a la pérdida.",
        ),
        keypoints(
            [
                "El pretraining aprende a continuar texto; el SFT aprende a responder.",
                "El SFT no cambia la arquitectura: cambia los datos y el objetivo de la pérdida.",
                "El libro usa 1.100 pares y un GPT-2 mediano de 355 millones de parámetros.",
                "El formato, el estilo y el fin de secuencia se aprenden de los ejemplos.",
                "Un SFT pequeño no garantiza verdad, seguridad ni conocimiento actualizado.",
                "LoRA reduce el coste al entrenar solo una parte pequeña de los pesos.",
            ]
        ),
    ),
    key_points=(
        "El SFT adapta un modelo preentrenado con pares de instrucción y respuesta.",
        "La tarea sigue siendo predecir el siguiente token; cambian los datos y la máscara.",
        "Los objetivos son seguir instrucciones, mantener el formato y saber terminar.",
        "El ajuste completo y LoRA difieren en coste, no en el planteamiento pedagógico.",
    ),
)
