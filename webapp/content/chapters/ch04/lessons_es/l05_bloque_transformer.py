"""Lección 5 · El bloque transformer."""

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
)

LESSON = Lesson(
    number=5,
    slug="bloque-transformer",
    title="El bloque transformer",
    summary=(
        "El ensamblaje completo: LayerNorm, atención multi-head, residual, LayerNorm, "
        "red feed-forward y residual, con la misma forma de entrada y salida."
    ),
    minutes=12,
    objectives=(
        "Ordenar las seis operaciones de un bloque transformer Pre-LN.",
        "Explicar dónde se aplica cada conexión residual y qué exige.",
        "Comprobar que la forma [batch, tokens, 768] se conserva.",
        "Relacionar el bloque con los doce que apila GPT-2 small.",
    ),
    blocks=(
        lead(
            "Ya tienes las piezas sueltas: LayerNorm, atención, GELU, red feed-forward y "
            "conexiones residuales. El bloque transformer las ordena en una secuencia "
            "repetible. Esa secuencia es el corazón de GPT: doce copias con los mismos "
            "tensores de entrada y salida, pero con pesos distintos, convierten una "
            "secuencia de vectores en otra secuencia de vectores más rica en contexto."
        ),
        h2("La secuencia del bloque"),
        p(
            "El bloque Pre-LN que usa GPT-2 sigue este orden. Primero guarda la entrada "
            "<code>x</code> y la normaliza con <code>norm1</code>. Después aplica la "
            "atención multi-head, que mezcla información entre posiciones. Suma el "
            "resultado a la entrada original: <code>x = x + attention(norm1(x))</code>. "
            "A continuación guarda ese nuevo <code>x</code>, lo normaliza con "
            "<code>norm2</code>, pasa por la red feed-forward y suma otra vez: "
            "<code>x = x + ffn(norm2(x))</code>. El libro añade dropout después de cada "
            "subcapa durante el entrenamiento."
        ),
        figure(
            "img/ch04/bloque-gpt.svg",
            "Diagrama del bloque transformer: LayerNorm, atención multi-head, suma residual, LayerNorm, red feed-forward y segunda suma residual.",
            "El bloque conserva la forma de la entrada: cada subcapa transforma el "
            "contenido, pero no el número de tokens ni la dimensión del vector.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "La clave está en las dos sumas. La primera residual rodea la atención; la "
            "segunda, la FFN. Ambas necesitan que la salida de la subcapa tenga exactamente "
            "la misma forma que su entrada. Por eso la atención proyecta de 768 a 768 y la "
            "FFN vuelve a 768 después de expandir. Sin esa coincidencia, la suma no sería "
            "posible y el bloque tendría que recurrir a otra operación para combinar los "
            "caminos. La forma <code>[batch, tokens, 768]</code> se mantiene de principio a "
            "fin."
        ),
        p(
            "Esa repetición es lo que convierte una operación local en un modelo profundo. "
            "Cada bloque recibe la corriente residual del anterior, la normaliza, la "
            "enriquece con atención y la transforma con la FFN. Ningún bloque necesita "
            "saber cuántos le siguen: su contrato es siempre el mismo, una secuencia de "
            "vectores de 768 dimensiones. Esa uniformidad permite cambiar el número de "
            "capas sin reescribir la arquitectura y es la razón por la que el mismo código "
            "sirve para GPT-2 small y para variantes más grandes."
        ),
        h2("Pre-LN y forma constante"),
        p(
            "El orden importa. En Pre-LN, la normalización ocurre antes de la subcapa; la "
            "suma residual ocurre después, sobre la entrada sin normalizar. Eso deja un "
            "camino directo —la propia <code>x</code>— que atraviesa el bloque sin pasar "
            "por la atención ni por la FFN. En Post-LN, la normalización se aplicaría "
            "después de la suma, dentro del camino principal. GPT-2 eligió Pre-LN porque "
            "facilita el entrenamiento de pilas profundas; el libro lo señala al comentar "
            "que Post-LN suele dar dinámicas peores."
        ),
        p(
            "Cada bloque de GPT-2 small contiene unos 7,09 millones de parámetros: 2,36 M "
            "de atención, 4,72 M de FFN y 3 072 de las dos LayerNorm. Doce bloques suman "
            "unos 85,03 M. El bloque no cambia la longitud de la secuencia ni la dimensión "
            "del embedding; lo que cambia es el contenido de cada vector, que pasa a "
            "incorporar información del contexto. La forma es la misma, pero el significado "
            "no: un vector de «gato» al entrar y al salir no codifica lo mismo."
        ),
        lab("gpt-block"),
        callout(
            "note",
            "Un bloque no es un modelo",
            "El bloque transformer es la unidad repetible, no el GPT completo. Al modelo "
            "le faltan los embeddings de entrada, la normalización final y la cabeza de "
            "salida. El bloque se limita a transformar la secuencia que recibe; la "
            "arquitectura completa decide cómo entrar y cómo convertir el resultado en "
            "logits.",
        ),
        check(
            "¿Por qué la conexión residual de la atención se suma a la entrada original y "
            "no a la salida de LayerNorm?",
            "Porque el residual debe conservar un camino directo con la información de "
            "partida. La LayerNorm prepara la entrada para la atención, pero la suma se "
            "hace con la <code>x</code> sin normalizar que existía antes de la subcapa. Así "
            "el gradiente y la información original pueden atravesar el bloque sin "
            "depender de la transformación aprendida.",
        ),
        keypoints(
            [
                "El bloque Pre-LN ordena: LayerNorm, atención, residual, LayerNorm, FFN y residual.",
                "La atención mezcla tokens; la FFN transforma cada token por separado.",
                "Las dos conexiones residuales exigen que entrada y salida compartan forma.",
                "La forma [batch, tokens, 768] se conserva en todo el bloque.",
                "Doce bloques suman unos 85,03 M de parámetros en GPT-2 small.",
                "El bloque transforma el contenido contextual, no la forma del tensor.",
            ]
        ),
    ),
    key_points=(
        "Un bloque transformer combina dos subcapas con normalización y residuales.",
        "El orden Pre-LN es LN → atención → residual → LN → FFN → residual.",
        "Las sumas residuales necesitan que las formas coincidan.",
        "La forma de la secuencia se conserva; el contenido se vuelve contextual.",
        "GPT-2 small apila doce bloques de unos 7,09 M de parámetros cada uno.",
        "El bloque no es el modelo completo: faltan embeddings y cabeza de salida.",
    ),
)
