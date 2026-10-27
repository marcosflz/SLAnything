"""Lección 8 · Repaso y autoevaluación."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=8,
    slug="repaso-texto",
    title="Repaso y autoevaluación",
    summary=(
        "El capítulo completo en un mapa: de la cadena de texto al tensor que entra en el "
        "transformer. Ocho ideas, una tabla de conexiones y un quiz de diez preguntas."
    ),
    minutes=10,
    objectives=(
        "Reordenar el pipeline de preparación de texto sin consultar las lecciones.",
        "Conectar tokenización, BPE, ventanas, pares y embeddings.",
        "Detectar qué paso necesita una segunda visita.",
        "Comprobar el aprendizaje con la autoevaluación del capítulo.",
    ),
    blocks=(
        lead(
            "Has recorrido el capítulo 2. Al principio, el texto era una cadena de caracteres; "
            "al final, es un tensor de forma <code>(lote, contexto, dimensión)</code> que un "
            "transformer puede procesar. Este repaso no añade conceptos nuevos: ordena los que "
            "ya tienes y señala las conexiones que suelen romperse."
        ),
        p(
            "El pipeline completo cabe en una línea: <strong>texto → tokens → IDs → ventanas → "
            "pares x/y → embeddings → tensor de entrada</strong>. Cada flecha es una decisión. "
            "Tokenizar por palabras o por subpalabras cambia el vocabulario. Elegir un stride "
            "cambia el número de ejemplos. Elegir una dimensión cambia la memoria. Si puedes "
            "justificar cada flecha, puedes explicar el capítulo."
        ),
        h2("Las ocho ideas del capítulo"),
        bullets(
            [
                "<strong>Un LLM no procesa texto bruto.</strong> Necesita IDs y vectores; el "
                "tokenizador es la primera pieza del modelo.",
                "<strong>La granularidad importa.</strong> Palabra, subpalabra y carácter "
                "equilibran cobertura, longitud y tamaño del vocabulario.",
                "<strong>Los tokens especiales cubren huecos.</strong> <code>&lt;|unk|&gt;</code>, "
                "<code>&lt;|endoftext|&gt;</code> y <code>[PAD]</code> resuelven situaciones que "
                "las palabras no resuelven.",
                "<strong>BPE construye subpalabras por frecuencia.</strong> Fusiona pares "
                "frecuentes y permite representar palabras nuevas.",
                "<strong>La ventana deslizante crea ejemplos.</strong> Contexto y stride "
                "determinan cuántos fragmentos se obtienen y cuánto se solapan.",
                "<strong>El objetivo es la entrada desplazada.</strong> Una ventana de L tokens "
                "produce L predicciones, no una.",
                "<strong>El embedding es una consulta a una matriz.</strong> La fila del ID es "
                "el vector; la matriz se aprende.",
                "<strong>La geometría no es semántica.</strong> Coseno y vecinos son útiles, "
                "pero heredan sesgos y no garantizan sinonimia.",
            ],
            ordered=True,
        ),
        p(
            "Tres pares que conviene no confundir. Primero, <strong>token frente a ID</strong>: "
            "el token es la pieza de texto; el ID es su clave numérica. Segundo, <strong>ventana "
            "de entrenamiento frente a ventana de contexto</strong>: la primera es el fragmento "
            "que se usa en un paso; la segunda es el máximo que el modelo puede procesar. "
            "Tercero, <strong>embedding estático frente a representación contextual</strong>: el "
            "primero es una fila fija; la segunda depende de la frase y la produce el "
            "transformer."
        ),
        h2("El pipeline en una tabla"),
        table(
            ["Paso", "Entrada", "Salida", "Pregunta de control"],
            [
                ["Tokenizar", "Texto", "Lista de tokens", "¿Qué unidades he elegido?"],
                ["Codificar", "Tokens", "IDs", "¿El vocabulario cubre el dominio?"],
                ["Ventana", "IDs", "Fragmentos de L tokens", "¿Cuánto se solapan?"],
                ["Emparejar", "Fragmento", "x e y desplazados", "¿Cuántas predicciones salen?"],
                ["Embedding", "IDs", "Matriz de vectores", "¿Cuántos parámetros hay?"],
                ["Posición", "Vectores", "Vectores con orden", "¿Cómo sabe el modelo dónde está?"],
            ],
            caption="El pipeline y una pregunta para comprobar cada transición.",
        ),
        p(
            "La última fila merece un comentario. La capa de embeddings asigna el mismo vector "
            "a un token esté donde esté. Para que el modelo distinga «gato come pescado» de "
            "«pescado come gato», hace falta información posicional. Los GPT añaden un "
            "embedding de posición al de token; ambos tienen la misma dimensión y se suman. En "
            "el capítulo 3, la atención usará esa suma como punto de partida."
        ),
        check(
            "Explica en dos frases por qué una ventana de 256 tokens genera 256 predicciones y no una.",
            "Porque la salida del transformer tiene una posición por token de entrada y cada "
            "posición produce una distribución sobre el vocabulario. La pérdida compara cada "
            "posición con el token siguiente, así que se aprovechan las 256 posiciones en un "
            "solo paso hacia delante.",
        ),
        callout(
            "success",
            "Ahora te toca",
            "Abre la <strong>autoevaluación del capítulo 2</strong>: diez preguntas con "
            "explicación. Necesitas un <strong>80 %</strong> —ocho de diez— para considerar el "
            "capítulo superado. Si fallas alguna, vuelve a la lección correspondiente; el quiz "
            "se puede repetir sin penalización.",
        ),
        p(
            "Antes de pulsar «empezar», haz un último ejercicio mental. Imagina el corpus «El "
            "gato duerme. El perro duerme.» y recorre el pipeline: tokens, IDs, una ventana de "
            "seis, pares desplazados, una matriz de embeddings de tamaño vocabulario × "
            "dimensión. Si puedes escribir las formas de los tensores y justificar el "
            "desplazamiento, estás listo para el capítulo 3. Si algo se resiste, no sigas: "
            "vuelve a esa lección. El siguiente capítulo da por sabido todo esto."
        ),
        p(
            "El capítulo 3 empieza justo donde termina este: con un tensor de embeddings y una "
            "pregunta pendiente, cómo decide el modelo a qué tokens prestar atención. La "
            "preparación de datos no es un trámite; es la mitad del trabajo. Un pipeline claro "
            "hace que los errores del modelo sean depurables. Un pipeline opaco convierte "
            "cualquier resultado raro en una caja negra."
        ),
        keypoints(
            [
                "El pipeline es texto → tokens → IDs → ventanas → pares → embeddings.",
                "Cada decisión de tokenización cambia vocabulario, longitud y coste.",
                "El objetivo de entrenamiento es la entrada desplazada un token.",
                "La ventana de entrenamiento no es el contexto máximo del modelo.",
                "Los embeddings estáticos se complementan con información posicional y contextual.",
                "El quiz requiere un 80 % y puede repetirse sin penalización.",
            ]
        ),
    ),
    key_points=(
        "El capítulo convierte texto bruto en tensores listos para el transformer.",
        "Tokenización, BPE y ventanas son decisiones con consecuencias medibles.",
        "Los pares x/y hacen explícita la tarea de predecir el siguiente token.",
        "El embedding es una consulta aprendida; la posición se añade aparte.",
    ),
    quiz_id="quiz-capitulo-2",
)
