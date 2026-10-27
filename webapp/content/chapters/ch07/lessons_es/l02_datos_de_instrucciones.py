"""Lección 2 · Construir un dataset de instrucciones."""

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
    number=2,
    slug="datos-de-instrucciones",
    title="Construir un dataset",
    summary=(
        "Un conjunto de instrucciones se diseña: cada par debe ser claro, correcto y "
        "diverso, y su procedencia y licencia deben poder explicarse."
    ),
    minutes=10,
    objectives=(
        "Describir la estructura de un par instrucción, entrada y respuesta.",
        "Aplicar criterios de calidad y diversidad a un conjunto pequeño.",
        "Reconocer riesgos de licencia, privacidad y contaminación.",
        "Justificar la partición en entrenamiento, validación y prueba.",
    ),
    blocks=(
        lead(
            "Un dataset de instrucciones no es un montón de frases: es una colección de "
            "promesas sobre cómo debe comportarse el modelo. Si una respuesta es incorrecta, "
            "inconsistente o filtra datos personales, el ajuste aprenderá también eso. Antes "
            "de entrenar, conviene leer los datos como si fueran código de producción."
        ),
        p(
            "El conjunto del libro contiene <strong>1.100 pares</strong> en un JSON de unos "
            "204 KB. Cada entrada tiene tres campos: <code>instruction</code>, que describe "
            "la tarea; <code>input</code>, un contexto opcional que puede estar vacío; y "
            "<code>output</code>, la respuesta deseada. Un ejemplo es pedir la ortografía "
            "correcta de «Ocassion» y responder «The correct spelling is 'Occasion.'». Otro "
            "par no necesita entrada: «What is an antonym of 'complicated'?» se responde "
            "directamente. La plantilla debe saber omitir la sección de entrada cuando no "
            "aporta nada."
        ),
        h2("Anatomía de un par"),
        table(
            ["Campo", "Función", "Ejemplo"],
            [
                ["instruction", "Tarea que se pide", "Corrige la ortografía."],
                ["input", "Contexto opcional", "Ocassion"],
                ["output", "Respuesta de referencia", "The correct spelling is 'Occasion.'"],
            ],
            caption="Los tres campos de una entrada típica. La entrada puede estar vacía.",
            note="El formato exacto cambia entre datasets; lo importante es que la plantilla sea coherente.",
        ),
        p(
            "La partición del libro es 85 % de entrenamiento, 10 % de prueba y 5 % de "
            "validación: 935, 110 y 55 ejemplos. La validación se usa para observar la "
            "pérdida y detectar sobreajuste durante el entrenamiento; la prueba se reserva "
            "para la evaluación final. Si se mezclan ambos usos, se toman decisiones con "
            "información que debería ser invisible y la métrica deja de ser honesta. En "
            "conjuntos pequeños, además, una sola fila rara puede mover mucho la media."
        ),
        h2("Calidad, diversidad y licencias"),
        p(
            "La calidad empieza por la corrección: una respuesta mala enseña un error. Sigue "
            "por la claridad: instrucciones ambiguas producen objetivos ambiguos. Y termina "
            "por la consistencia: si dos ejemplos casi idénticos reciben respuestas "
            "incompatibles, el modelo recibe ruido. Conviene revisar duplicados, longitudes "
            "extremas, marcas de formato que se cuelan en el texto y respuestas que no "
            "responden a lo que se pregunta. En un conjunto de 1.100 pares, una revisión "
            "manual por muestreo es viable; en uno de 52.002, como el Alpaca original, hace "
            "falta un proceso de filtrado más sistemático."
        ),
        p(
            "La diversidad evita que el modelo aprenda un único guion. Un conjunto útil "
            "mezcla tareas de transformación, preguntas abiertas, extracción, resumen, "
            "clasificación y corrección; varía la longitud y el tono; incluye ejemplos con y "
            "sin contexto; y cubre distintos niveles de dificultad. También debe parecerse a "
            "las peticiones reales que se esperan en producción, no solo a las tareas "
            "cómodas de escribir. Si todas las respuestas empiezan igual, el modelo aprenderá "
            "esa muletilla antes que la tarea."
        ),
        p(
            "La procedencia es parte de la calidad. Antes de usar un dataset, comprueba su "
            "licencia, las condiciones de la fuente y si las respuestas se generaron con otro "
            "modelo cuyos términos limitan el uso. Revisa también datos personales, textos "
            "con copyright y ejemplos que puedan contener sesgos. Que un archivo esté "
            "publicado en un repositorio no significa que pueda usarse sin restricciones. "
            "Documenta la versión, la fecha y el filtro aplicado: sin trazabilidad, un "
            "resultado no se puede reproducir ni auditar."
        ),
        callout(
            "warning",
            "La contaminación también se entrena",
            "Si una pregunta del conjunto de prueba aparece en el de entrenamiento, la "
            "evaluación mide memoria, no generalización. Separa los conjuntos antes de "
            "cualquier aumento de datos y comprueba que no comparten instrucciones casi "
            "idénticas. El mismo cuidado vale para los benchmarks públicos que se usen como "
            "referencia.",
        ),
        check(
            "¿Por qué no conviene usar el conjunto de prueba para decidir cuándo parar el entrenamiento?",
            "Porque esas decisiones introducen información del conjunto de prueba en el "
            "modelo: se elige la configuración que mejor puntúa en él y la métrica final deja "
            "de estimar el rendimiento en datos nuevos. Para eso está la validación.",
        ),
        keypoints(
            [
                "Cada par tiene instrucción, entrada opcional y respuesta de referencia.",
                "La plantilla debe omitir la sección de entrada cuando está vacía.",
                "La partición del libro es 935 / 55 / 110 ejemplos (85 / 5 / 10 %).",
                "La calidad exige respuestas correctas, claras y consistentes.",
                "La diversidad de tareas y formatos mejora la generalización.",
                "Licencias, privacidad y contaminación se revisan antes de entrenar.",
            ]
        ),
    ),
    key_points=(
        "Un dataset de instrucciones se diseña y se audita, no solo se descarga.",
        "Instrucción, entrada opcional y respuesta forman el par de entrenamiento.",
        "La validación guía decisiones; la prueba se reserva para la evaluación final.",
        "Calidad, diversidad, licencia y privacidad son requisitos del dato.",
    ),
)
