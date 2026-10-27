"""Glosario del capítulo 4 (español)."""

from webapp.content.schema import GlossaryTerm

GLOSSARY_ES: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="LayerNorm",
        definition=(
            "Normalización que centra y escala las activaciones de cada token a lo largo "
            "de la dimensión de embedding. Usa una media y una varianza calculadas por "
            "vector, más un desplazamiento y una escala aprendibles."
        ),
        lesson="layer-normalization",
    ),
    GlossaryTerm(
        term="GELU",
        definition=(
            "Activación suave, Gaussian Error Linear Unit, que pondera cada entrada por la "
            "función de distribución gaussiana. Se aproxima con una tangente hiperbólica y "
            "es la que usa la red feed-forward de GPT-2."
        ),
        lesson="gelu",
    ),
    GlossaryTerm(
        term="feed-forward (FFN)",
        definition=(
            "Subred del bloque transformer formada por dos proyecciones lineales y una "
            "activación. Expande la dimensión de cada token, aplica GELU y vuelve a la "
            "dimensión original, sin mezclar tokens entre sí."
        ),
        lesson="feed-forward",
    ),
    GlossaryTerm(
        term="bloque transformer",
        definition=(
            "Unidad que combina LayerNorm, atención multi-head, una red feed-forward y dos "
            "conexiones residuales. GPT-2 small apila doce bloques idénticos en forma, pero "
            "con pesos distintos."
        ),
        lesson="bloque-transformer",
    ),
    GlossaryTerm(
        term="conexión residual",
        definition=(
            "Suma de la entrada de una subcapa a su salida, x + f(x), que crea un camino "
            "directo para la información y el gradiente. Exige que la entrada y la salida "
            "tengan la misma forma."
        ),
        lesson="conexiones-residuales",
    ),
    GlossaryTerm(
        term="Pre-LN",
        definition=(
            "Disposición que aplica LayerNorm antes de la atención y antes de la red "
            "feed-forward. Es la que usa GPT-2 y suele dar dinámicas de entrenamiento más "
            "estables que Post-LN."
        ),
        lesson="bloque-transformer",
    ),
    GlossaryTerm(
        term="Post-LN",
        definition=(
            "Disposición del transformer original en la que LayerNorm se aplica después de "
            "cada subcapa, no antes. Puede ser más difícil de entrenar en pilas profundas."
        ),
        lesson="layer-normalization",
    ),
    GlossaryTerm(
        term="peso atado",
        definition=(
            "Técnica que reutiliza la matriz de embeddings de tokens como matriz de la "
            "cabeza de salida. En GPT-2 small evita duplicar 38 597 376 parámetros y explica "
            "la diferencia entre 124 y 163 millones."
        ),
        lesson="cabeza-de-salida",
    ),
    GlossaryTerm(
        term="cabeza de salida",
        definition=(
            "Capa lineal final que proyecta cada vector contextual de 768 dimensiones al "
            "tamaño del vocabulario y produce los logits del siguiente token. En GPT-2 no "
            "tiene sesgo."
        ),
        lesson="cabeza-de-salida",
    ),
    GlossaryTerm(
        term="dimensión de embedding (emb_dim)",
        definition=(
            "Número de componentes de cada vector que representa un token; en GPT-2 small "
            "es 768. De ella dependen el tamaño de las proyecciones y buena parte del coste "
            "del modelo."
        ),
        lesson="configuracion-gpt",
    ),
    GlossaryTerm(
        term="proyección QKV",
        definition=(
            "Conjunto de tres transformaciones lineales que convierten cada token en una "
            "consulta, una clave y un valor para la atención. En GPT-2 small cada una "
            "proyecta 768 dimensiones a 768."
        ),
        lesson="bloque-transformer",
    ),
    GlossaryTerm(
        term="corriente residual",
        definition=(
            "Camino principal que atraviesa todos los bloques sumando las salidas de cada "
            "subcapa. Es la metáfora habitual para explicar cómo se acumula y preserva la "
            "información en un transformer profundo."
        ),
        lesson="conexiones-residuales",
    ),
)
