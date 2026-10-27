"""Lección 3 · Plantillas de chat."""

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
    number=3,
    slug="plantillas-chat",
    title="Plantillas de chat",
    summary=(
        "Una plantilla de chat convierte roles y mensajes en una secuencia de tokens con "
        "marcadores. El modelo solo ve el texto; la estructura debe ser explícita y constante."
    ),
    minutes=12,
    objectives=(
        "Identificar los roles system, user y assistant en una conversación.",
        "Comparar los estilos Alpaca y ChatML y sus marcadores.",
        "Explicar por qué entrenamiento e inferencia deben compartir plantilla.",
        "Construir y revisar una plantilla con un ejemplo ejecutable.",
    ),
    blocks=(
        lead(
            "Un modelo no ve «roles»: ve una secuencia de tokens. La plantilla de chat es "
            "el contrato que traduce una conversación a esa secuencia. Decide dónde empieza "
            "cada turno, quién habla, dónde termina la respuesta y qué texto debe aprender "
            "el modelo. Si el contrato cambia entre el entrenamiento y el uso real, el "
            "modelo recibe una entrada distinta de la que aprendió a interpretar."
        ),
        p(
            "El libro compara dos estilos. El estilo <strong>Alpaca</strong> usa secciones "
            "en texto plano: una instrucción, una entrada opcional y una respuesta, "
            "delimitadas por <code>### Instruction:</code>, <code>### Input:</code> y "
            "<code>### Response:</code>. El estilo <strong>Phi-3</strong> usa tokens "
            "especiales de turno, una idea similar a la de ChatML: marcan el inicio y el fin "
            "de cada turno, por ejemplo "
            "&lt;|im_start|&gt; y &lt;|im_end|&gt;. Ambos enfoques funcionan; lo importante "
            "es que la plantilla sea inequívoca y se aplique igual en todos los ejemplos."
        ),
        figure(
            "img/ch07/plantilla-chat.svg",
            "Esquema de una conversación con turnos de sistema, usuario y asistente, delimitados por tokens especiales y con la zona de respuesta marcada como entrenable.",
            "La plantilla convierte roles en marcadores. La zona verde es la que suele "
            "contribuir a la pérdida; el resto es contexto.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        h2("Roles, marcadores y formato"),
        code(
            "text",
            """
<|im_start|>system
Eres un asistente breve y preciso.<|im_end|>
<|im_start|>user
Convierte a pasiva: «El chef cocina la cena».<|im_end|>
<|im_start|>assistant
La cena es cocinada por el chef.<|im_end|>
""",
            caption="Una conversación ChatML. Los tokens especiales separan los turnos y el modelo aprende a cerrar el suyo.",
        ),
        p(
            "La conversación anterior tiene tres roles. El sistema no es un adorno: fija el "
            "marco de la respuesta, el tono y los límites. El usuario aporta la tarea. El "
            "asistente produce la respuesta que se quiere enseñar. En ChatML, cada turno se "
            "abre y se cierra con un marcador; en Alpaca, la cabecera <code>### Response:</code> "
            "señala dónde empieza la zona que el modelo debe aprender. Si el tokenizador no "
            "reconoce un marcador como especial, lo dividirá en varios tokens y el modelo verá "
            "una secuencia distinta; conviene comprobar el vocabulario antes de dar la plantilla "
            "por buena."
        ),
        p(
            "En Alpaca, la instrucción y la respuesta se separan con cabeceras y líneas en "
            "blanco. Si el campo de entrada está vacío, la sección <code>### Input:</code> se "
            "omite; incluirla vacía añade ruido y enseña un patrón que no aporta información. "
            "En ChatML, el turno de sistema fija el comportamiento general, el de usuario "
            "contiene la petición y el de asistente, la respuesta. Un mismo diálogo puede "
            "representarse en ambos estilos, pero no conviene mezclarlos dentro de un mismo "
            "entrenamiento sin una razón medida."
        ),
        lab("chat-template"),
        h2("Consistencia entre entrenamiento e inferencia"),
        p(
            "La plantilla forma parte del modelo tanto como los pesos. Si entrenas con "
            "Alpaca y en producción envías ChatML, el modelo ve marcadores que nunca asoció "
            "a una tarea; si entrenas sin turno de sistema y luego añades uno largo, también "
            "cambias la distribución. Lo mismo ocurre con los espacios, los saltos de línea "
            "y el token de fin: una diferencia aparentemente trivial puede desplazar la "
            "respuesta. Guarda la plantilla junto al checkpoint, versiónala y pruébala con "
            "casos de referencia antes de desplegar. Una prueba útil consiste en renderizar el "
            "mismo caso con la plantilla antigua y la nueva y comparar los IDs; si cambian, la "
            "actualización no es inocua. Documenta también la versión del tokenizador."
        ),
        py(
            """
INSTRUCCION = "Convierte a pasiva: «El chef cocina la cena cada día»."
RESPUESTA = "La cena es cocinada cada día por el chef."

def chatml(instruccion, respuesta):
    return (
        "<|im_start|>system\\nEres un asistente breve.\\n<|im_end|>\\n"
        "<|im_start|>user\\n" + instruccion + "\\n<|im_end|>\\n"
        "<|im_start|>assistant\\n" + respuesta + "\\n<|im_end|>"
    )

def alpaca(instruccion, respuesta):
    return (
        "A continuación se describe una tarea. Escribe una respuesta que la complete.\\n\\n"
        "### Instrucción:\\n" + instruccion + "\\n\\n"
        "### Respuesta:\\n" + respuesta
    )

for nombre, texto in (("ChatML", chatml(INSTRUCCION, RESPUESTA)),
                      ("Alpaca", alpaca(INSTRUCCION, RESPUESTA))):
    print("=" * 10, nombre, "=" * 10)
    print(texto)
    print()
""",
            caption=(
                "Dos plantillas para el mismo par. Cambia el texto de la instrucción y "
                "observa cómo se conservan los marcadores."
            ),
        ),
        callout(
            "tip",
            "La plantilla también es código",
            "Trátala como una función versionada: recibe roles y devuelve texto; tiene "
            "pruebas con casos vacíos, acentos y respuestas largas. Si la generas con "
            "concatenaciones, revisa los saltos de línea y no dejes que el texto del usuario "
            "pueda imitar los marcadores del sistema sin escapes o validación. Un cambio de "
            "plantilla sin pruebas es un cambio de modelo encubierto.",
        ),
        check(
            "¿Por qué no basta con que la plantilla de inferencia «se parezca» a la de entrenamiento?",
            "Porque el modelo aprende asociaciones exactas entre marcadores, espacios y "
            "respuestas. Una diferencia de formato cambia la secuencia de tokens y puede "
            "llevar a respuestas peores aunque el contenido de la petición sea el mismo.",
        ),
        keypoints(
            [
                "La plantilla traduce roles y mensajes a una secuencia de tokens.",
                "Alpaca usa cabeceras; ChatML y Phi-3 usan tokens especiales de turno.",
                "La sección de entrada se omite cuando el campo está vacío.",
                "Entrenamiento e inferencia deben usar la misma plantilla y tokenizador.",
                "La plantilla se versiona y se prueba como cualquier otro componente.",
                "Un formato ambiguo permite que el texto del usuario imite marcadores.",
            ]
        ),
    ),
    key_points=(
        "Los roles no existen para el modelo: existen los marcadores que los representan.",
        "Alpaca y ChatML son estilos distintos; mezclarlos sin medir introduce ruido.",
        "La plantilla debe ser idéntica en entrenamiento e inferencia.",
        "La plantilla es un artefacto versionado y testeable.",
    ),
)
