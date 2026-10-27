"""Lección 1 · Tokens y vocabulario."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=1,
    slug="tokens-y-vocabulario",
    title="Tokens y vocabulario",
    summary=(
        "Un modelo no lee letras: recibe números. El primer paso es decidir qué unidad "
        "de texto cuenta como token y construir un vocabulario con sus identificadores."
    ),
    minutes=10,
    objectives=(
        "Explicar por qué un LLM no puede procesar texto bruto.",
        "Comparar la tokenización por palabras, por subpalabras y por caracteres.",
        "Construir un vocabulario y asignar identificadores a cada token.",
        "Reconocer el problema de las palabras fuera del vocabulario.",
    ),
    blocks=(
        lead(
            "Un modelo de lenguaje parece leer, pero en realidad recibe una secuencia de "
            "números. Entre el texto que escribes y la primera operación matemática hay una "
            "decisión de diseño que lo condiciona todo: <strong>qué trozos de texto cuentan "
            "como unidad</strong>. Esos trozos son los tokens."
        ),
        p(
            "Las redes neuronales suman, multiplican y aplican funciones sobre vectores de "
            "números reales. El texto es categórico: la cadena «gato» no se puede sumar a "
            "«perro». Para cerrar esa distancia se construye un <strong>vocabulario</strong>: "
            "una lista finita de unidades y una correspondencia entre cada unidad y un número "
            "entero, el <strong>token ID</strong>. Tokenizar es partir el texto; codificar es "
            "traducir cada trozo a su identificador."
        ),
        h2("Por qué no basta con separar por espacios"),
        p(
            "La idea más inmediata es tratar cada palabra como un token. El libro lo hace al "
            "principio con un relato corto de Edith Wharton, <em>The Verdict</em>: tras separar "
            "palabras y signos de puntuación, obtiene <strong>4 690 tokens</strong> a partir de "
            "un texto de <strong>20 479 caracteres</strong>. Es un punto de partida útil porque "
            "es fácil de explicar, pero arrastra dos problemas."
        ),
        p(
            "El primero es el tamaño del vocabulario. Un idioma tiene cientos de miles de "
            "palabras y formas flexionadas; si cada una recibe un identificador, la tabla crece "
            "sin control y muchos tokens aparecen una sola vez. El segundo es la "
            "<strong>palabra desconocida</strong>: si el modelo nunca vio «teletransporte» "
            "durante el entrenamiento, el tokenizador no sabe qué número darle. Ese fenómeno se "
            "conoce como <em>out-of-vocabulary</em> (OOV)."
        ),
        table(
            ["Unidad", "Ventaja", "Coste", "Ejemplo"],
            [
                [
                    "<strong>Palabra</strong>",
                    "Tokens interpretables y secuencias cortas",
                    "Vocabulario enorme y palabras desconocidas",
                    "«gato», «duerme», «.»",
                ],
                [
                    "<strong>Subpalabra</strong>",
                    "Equilibrio entre tamaño y cobertura",
                    "Tokens que no coinciden con palabras completas",
                    "«ga», «to», «dor», «mien»",
                ],
                [
                    "<strong>Carácter</strong>",
                    "Vocabulario mínimo y cobertura total",
                    "Secuencias muy largas y menos significado por paso",
                    "«g», «a», «t», «o»",
                ],
            ],
            caption="Tres granularidades para el mismo texto. La elección cambia el vocabulario y la longitud de la secuencia.",
        ),
        p(
            "La tokenización por subpalabras busca el término medio. Un vocabulario de decenas "
            "de miles de piezas puede representar palabras nuevas combinando fragmentos "
            "conocidos. «Tokenización», por ejemplo, puede descomponerse en «token» + «ización». "
            "El modelo no necesita haber visto la palabra completa para construir una "
            "representación razonable."
        ),
        h2("Del texto al identificador"),
        p(
            "Construir un vocabulario es más sencillo de lo que parece. Se recorren los textos "
            "de entrenamiento, se extraen los tokens, se eliminan duplicados y se ordena el "
            "resultado. Después se asigna un entero a cada posición. En el ejemplo del libro, el "
            "vocabulario ronda los <strong>1 159 tokens</strong>; al añadir dos tokens "
            "especiales pasa a <strong>1 161</strong>. Es un vocabulario diminuto comparado con "
            "el de un modelo real, pero suficiente para entender el mecanismo."
        ),
        figure(
            "img/ch02/tokenizacion.svg",
            "Esquema de una frase que se divide en tokens y después se convierte en identificadores numéricos.",
            "El texto se fragmenta en tokens; cada token consulta el vocabulario y devuelve un "
            "identificador. El vocabulario es el puente entre ambos mundos; los IDs de la figura "
            "son ilustrativos.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "La dirección importa. <strong>Codificar</strong> va del texto a los IDs; "
            "<strong>decodificar</strong> recorre el camino inverso. Para decodificar hace falta "
            "un diccionario inverso, de ID a token. Sin él, el modelo podría generar números "
            "correctos y nosotros no sabríamos convertirlos en palabras. En la próxima lección "
            "veremos qué ocurre cuando un token no existe en el vocabulario y cómo se resuelve "
            "con piezas especiales."
        ),
        p(
            "Hay una decisión lingüística que conviene tomar conscientemente: conservar o no las "
            "mayúsculas y los espacios. El libro mantiene las mayúsculas porque ayudan a "
            "distinguir nombres propios y a aprender puntuación; en cambio, elimina los espacios "
            "para simplificar el ejemplo. En un tokenizador real los espacios suelen formar parte "
            "de los tokens, porque aportan estructura al texto."
        ),
        bullets(
            [
                "<strong>Texto</strong>: la cadena original, con mayúsculas y puntuación.",
                "<strong>Tokens</strong>: las unidades que produce la regla de división.",
                "<strong>Vocabulario</strong>: el conjunto ordenado de tokens únicos.",
                "<strong>IDs</strong>: los enteros que representan esos tokens.",
            ]
        ),
        callout(
            "tip",
            "Una regla práctica",
            "Si el vocabulario es pequeño, las secuencias se alargan; si es enorme, la matriz "
            "de embeddings crece y muchas filas se entrenan poco. No hay una granularidad "
            "universalmente correcta: hay un compromiso entre cobertura, longitud y coste.",
        ),
        check(
            "¿Por qué un tokenizador por caracteres no es la solución obvia, si cubre cualquier palabra?",
            "Porque multiplica la longitud de la secuencia y reparte el significado entre muchas "
            "piezas. El modelo tiene que aprender a recomponer palabras desde unidades mínimas, y "
            "cada paso de atención cuesta más. La subpalabra conserva fragmentos con significado "
            "y mantiene la secuencia manejable.",
        ),
        h2("Lo que conviene retener"),
        p(
            "El vocabulario no es una lista de significados: es una tabla de correspondencias. "
            "Dos tokens con IDs cercanos no son necesariamente parecidos; el número es solo una "
            "clave de consulta. El significado aparecerá más adelante, cuando cada ID se "
            "transforme en un vector y ese vector se entrene. Separar ambas ideas evita una "
            "confusión frecuente: el ID no codifica semántica, solo identidad."
        ),
        p(
            "Tampoco conviene olvidar que el tokenizador se elige antes de entrenar y se queda "
            "fijo. Cambiarlo obliga a reconstruir el vocabulario y a reentrenar los embeddings. "
            "Por eso los modelos publican su tokenizador junto con los pesos: no es un detalle "
            "intercambiable, sino parte del contrato de entrada."
        ),
        keypoints(
            [
                "Un LLM no procesa texto bruto: procesa identificadores numéricos.",
                "Tokenizar es dividir el texto; codificar es asignar un ID a cada token.",
                "Palabra, subpalabra y carácter son granularidades con costes distintos.",
                "Un vocabulario grande reduce la longitud, pero encarece los embeddings y sufre OOV.",
                "El ID de un token identifica una pieza; no contiene significado por sí mismo.",
                "El tokenizador forma parte del modelo y no se cambia a la ligera.",
            ]
        ),
    ),
    key_points=(
        "Un LLM necesita números: el tokenizador convierte texto en IDs.",
        "La granularidad por subpalabras equilibra vocabulario y longitud.",
        "Un vocabulario se construye con los tokens únicos del corpus.",
        "Las palabras fuera del vocabulario son el problema OOV.",
    ),
    quiz_id=None,
)
