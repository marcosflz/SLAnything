"""Lección 2 · Tokens especiales y decodificación."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    quote,
    table,
)

LESSON = Lesson(
    number=2,
    slug="tokens-especiales",
    title="Tokens especiales y decodificación",
    summary=(
        "Los vocabularios necesitan piezas que no son palabras: una para lo desconocido, "
        "otra para separar documentos y otras para ordenar lotes. Aquí vemos cómo se usan "
        "y por qué decodificar no siempre devuelve el texto original."
    ),
    minutes=9,
    objectives=(
        "Explicar el papel de <|unk|> y <|endoftext|>.",
        "Distinguir tokens de inicio, fin y relleno.",
        "Describir el proceso de decodificación y sus límites.",
        "Comprobar cuándo un round-trip texto → IDs → texto es fiel.",
    ),
    blocks=(
        lead(
            "En la lección anterior construimos un vocabulario con las palabras del corpus. "
            "¿Qué pasa cuando llega una palabra que no estaba? Un tokenizador ingenuo se "
            "detiene con un error. Un tokenizador útil necesita una salida: un token especial "
            "que diga «esto no lo conozco»."
        ),
        p(
            "El libro muestra el fallo con una frase: <code>«Hello, do you like tea?»</code>. "
            "La palabra «Hello» no aparece en <em>The Verdict</em>, así que no tiene ID y la "
            "consulta del diccionario lanza un <code>KeyError</code>. Es una consecuencia de "
            "haber construido el vocabulario con un corpus limitado. La lección práctica es "
            "doble: conviene entrenar con textos diversos y conviene tener un plan para lo que "
            "quede fuera."
        ),
        h2("Dos tokens que cambian el contrato"),
        p(
            "La primera versión del tokenizador se amplía con <strong><code>&lt;|unk|&gt;</code></strong> "
            "(de <em>unknown</em>) y <strong><code>&lt;|endoftext|&gt;</code></strong>. El primero "
            "sustituye cualquier pieza que no esté en el vocabulario. El segundo marca una "
            "frontera: el final de un documento y el comienzo de otro. Cuando se concatenan "
            "varias fuentes para entrenar, esos marcadores impiden que el modelo aprenda una "
            "continuidad que no existe."
        ),
        p(
            "Al añadirlos, el vocabulario del ejemplo pasa de 1 159 a <strong>1 161</strong> "
            "entradas. En el ejemplo del libro los dos tokens nuevos ocupan los IDs 1159 y 1160, "
            "al final de la lista ordenada. El orden es una convención, no una propiedad mágica: "
            "lo importante es que el mismo mapa se use al entrenar y al inferir."
        ),
        table(
            ["Token", "Función", "Cuándo aparece", "Riesgo si falta"],
            [
                [
                    "<code>&lt;|unk|&gt;</code>",
                    "Representa una pieza desconocida",
                    "Palabra o símbolo fuera del vocabulario",
                    "El codificador falla o pierde la entrada",
                ],
                [
                    "<code>&lt;|endoftext|&gt;</code>",
                    "Separa documentos o marca el final",
                    "Entre dos textos independientes",
                    "El modelo mezcla fuentes sin frontera",
                ],
                [
                    "<code>[BOS]</code> / <code>[EOS]</code>",
                    "Inicio y fin de secuencia",
                    "Tareas que necesitan delimitar el texto",
                    "El modelo no sabe dónde empieza o acaba",
                ],
                [
                    "<code>[PAD]</code>",
                    "Rellena secuencias de distinta longitud",
                    "Lotes con ejemplos de tamaños diferentes",
                    "No se pueden apilar en un tensor rectangular",
                ],
            ],
            caption="Tokens especiales habituales. No todos los modelos usan todos.",
            note=(
                "GPT-2 y la familia GPT usan un único token especial, &lt;|endoftext|&gt;, con el "
                "ID 50 256 en un vocabulario de 50 257 entradas. El relleno se hace con ese mismo "
                "token y una máscara de atención evita que el modelo lo tenga en cuenta."
            ),
        ),
        p(
            "Hay una diferencia importante entre el tokenizador didáctico y el de GPT. El "
            "primero necesita <code>&lt;|unk|&gt;</code> porque su vocabulario es una lista "
            "cerrada de palabras. El segundo usa BPE y puede descomponer cualquier palabra en "
            "subpalabras o bytes, de modo que casi nunca se queda sin representación. Aun así, "
            "conserva <code>&lt;|endoftext|&gt;</code> como separador explícito."
        ),
        h2("Decodificar: el camino de vuelta"),
        p(
            "Decodificar es consultar el diccionario inverso y unir los tokens. Si los IDs son "
            "válidos, el resultado debería parecerse mucho al texto de partida. «Parecerse» no "
            "significa «ser idéntico». El tokenizador simple une con espacios y luego los "
            "elimina antes de la puntuación; ese postprocesado mejora la legibilidad, pero puede "
            "cambiar detalles de espaciado. Y si algún token era <code>&lt;|unk|&gt;</code>, la "
            "palabra original se ha perdido para siempre."
        ),
        p(
            "Por eso hablamos de <strong>round-trip</strong> (ida y vuelta). Un tokenizador es "
            "fiel si <code>decode(encode(texto)) == texto</code> para el texto en cuestión. Los "
            "tokenizadores de bytes suelen cumplir esta propiedad; los que normalizan "
            "mayúsculas, eliminan espacios o sustituyen palabras desconocidas, no. Antes de "
            "usar un tokenizador en producción conviene probar frases con acentos, signos "
            "dobles, emoji y palabras inventadas."
        ),
        quote(
            "El vocabulario define lo que el modelo puede nombrar; los tokens especiales definen "
            "lo que puede hacer cuando algo se queda fuera.",
            "Idea central de esta lección",
        ),
        callout(
            "warning",
            "El round-trip puede fallar sin dar error",
            "Una decodificación puede devolver un texto perfectamente legible y, aun así, "
            "distinto del original. Si el tokenizador colapsa dos palabras desconocidas en el "
            "mismo <code>&lt;|unk|&gt;</code>, el modelo no puede recuperar cuál era cuál. La "
            "pérdida es silenciosa: por eso se comprueba con ejemplos, no se supone.",
        ),
        p(
            "Los tokens de relleno merecen un comentario aparte. Para entrenar por lotes, todas "
            "las secuencias de un batch deben tener la misma longitud. La solución habitual es "
            "añadir <code>[PAD]</code> al final de las más cortas y acompañar el lote con una "
            "máscara que indique qué posiciones son reales. Sin esa máscara, el modelo trataría "
            "el relleno como texto y la función de pérdida penalizaría predicciones sobre "
            "posiciones artificiales."
        ),
        check(
            "Tienes la frase «Hola, mundo» y el tokenizador devuelve <|unk|>, «,», «mundo». ¿Qué ha pasado y qué se ha perdido?",
            "«Hola» no estaba en el vocabulario y se sustituyó por el token desconocido. Al "
            "decodificar obtendrás algo como «&lt;|unk|&gt;, mundo». Los IDs permiten reconstruir "
            "la estructura, pero no la palabra original: la información se perdió al codificar.",
        ),
        h2("Diseñar el contrato de entrada"),
        p(
            "Elegir tokens especiales es diseñar un contrato. Si el modelo va a recibir varios "
            "documentos, necesita una frontera. Si va a procesar lotes, necesita relleno y "
            "máscara. Si va a generar texto y detenerse, necesita una señal de fin. Añadir "
            "tokens que nunca se usan no ayuda; al contrario, diluye el vocabulario y ocupa "
            "filas de la matriz de embeddings que recibirán pocos gradientes."
        ),
        p(
            "En el resto del capítulo veremos cómo BPE reduce la dependencia de "
            "<code>&lt;|unk|&gt;</code> y cómo las secuencias de IDs se agrupan en ventanas para "
            "entrenar. De momento quédate con la idea: un tokenizador no solo parte texto; "
            "también decide qué se puede representar, qué se pierde y cómo se delimita el "
            "contexto."
        ),
        keypoints(
            [
                "&lt;|unk|&gt; representa piezas que no están en el vocabulario.",
                "&lt;|endoftext|&gt; separa documentos y, en GPT, también marca el final.",
                "[BOS], [EOS] y [PAD] son convenciones frecuentes, no obligatorias.",
                "Decodificar exige un diccionario inverso de ID a token.",
                "El round-trip es fiel solo si el tokenizador no normaliza ni pierde información.",
                "Un token desconocido puede hacer que la vuelta sea legible pero no exacta.",
            ]
        ),
    ),
    key_points=(
        "Los tokens especiales cubren situaciones que las palabras no cubren.",
        "<|unk|> evita el fallo ante vocabulario cerrado; BPE lo hace casi innecesario.",
        "<|endoftext|> separa fuentes y marca el final en los modelos GPT.",
        "Decodificar reconstruye texto, pero no garantiza un round-trip exacto.",
    ),
    quiz_id=None,
)
