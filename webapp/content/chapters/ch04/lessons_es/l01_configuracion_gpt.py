"""Lección 1 · Configurar un GPT pequeño."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=1,
    slug="configuracion-gpt",
    title="Configurar un GPT pequeño",
    summary=(
        "Las siete claves de GPT-2 small, qué controla cada una y de dónde salen los "
        "124 millones de parámetros que el libro usa como modelo de trabajo."
    ),
    minutes=10,
    objectives=(
        "Interpretar cada clave de la configuración GPT_CONFIG_124M.",
        "Calcular los parámetros de embeddings, atención y red feed-forward.",
        "Distinguir el modelo de 124 M con pesos atados del de 163 M sin atar.",
        "Explicar por qué un GPT pequeño basta para aprender la arquitectura.",
    ),
    blocks=(
        lead(
            "Un GPT no empieza con una idea abstracta, sino con un puñado de números. La "
            "configuración de GPT-2 small cabe en un diccionario de siete claves y, sin "
            "embargo, determina cuántos tokens puede leer el modelo, cuántas capas "
            "atraviesa la información y cuántos parámetros hay que entrenar. En esta "
            "lección leerás esa configuración y comprobarás de dónde sale la cifra de "
            "124 millones."
        ),
        h2("Siete números que definen el modelo"),
        p(
            "El libro llama a ese diccionario <code>GPT_CONFIG_124M</code>. No es una "
            "caja negra: cada entrada tiene una consecuencia directa sobre la forma de los "
            "tensores y sobre el coste. La tabla resume las siete claves y lo que controla "
            "cada una. Los valores son los del GPT-2 small descrito por Radford y "
            "colaboradores; el libro corrige la cifra original de 117 millones y trabaja "
            "con 124 millones."
        ),
        table(
            ["Clave", "Valor", "Qué controla"],
            [
                ["<code>vocab_size</code>", "50 257", "Tokens distintos que el modelo puede leer y predecir."],
                ["<code>context_length</code>", "1 024", "Máximo de posiciones que caben en la ventana."],
                ["<code>emb_dim</code>", "768", "Componentes de cada vector de token."],
                ["<code>n_heads</code>", "12", "Cabezas de atención que trabajan en paralelo."],
                ["<code>n_layers</code>", "12", "Bloques transformer apilados."],
                ["<code>drop_rate</code>", "0,1", "Fracción de activaciones que se apaga al entrenar."],
                ["<code>qkv_bias</code>", "False", "Si las proyecciones Q, K y V llevan sesgo."],
            ],
            caption="La configuración de GPT-2 small, con los nombres que usa el libro.",
            note=(
                "La dimensión de cada cabeza es 768 / 12 = 64. No es una clave aparte: se "
                "deduce de emb_dim y n_heads."
            ),
        ),
        p(
            "La combinación no es arbitraria. Una dimensión de 768 repartida entre 12 "
            "cabezas deja 64 componentes por cabeza, suficientes para que cada una "
            "especialice un tipo de relación. Doce capas permiten componer "
            "transformaciones, y 1 024 posiciones cubren textos cortos o conversaciones "
            "breves. El dropout del 10 % regulariza; <code>qkv_bias</code> se desactiva al "
            "principio, aunque el libro lo revisa al cargar los pesos de GPT-2."
        ),
        h2("De dónde salen los 124 millones"),
        p(
            "La cifra no se memoriza: se calcula. Los embeddings de tokens ocupan "
            "50 257 × 768 = 38 597 376 parámetros; los posicionales, 1 024 × 768 = 786 432. "
            "Cada bloque contiene cuatro proyecciones de atención de 768 × 768 —tres para "
            "Q, K y V, una para la salida—, una red feed-forward que expande a 3 072 y "
            "vuelve a 768, y dos LayerNorm. El bloque completo ronda los 7,09 millones de "
            "parámetros; doce bloques, unos 85,03 millones. Sumando embeddings y la "
            "normalización final se llega a 124 412 160, siempre que la cabeza de salida "
            "reutilice la matriz de embeddings. El cálculo siguiente lo comprueba paso a "
            "paso; es un cálculo propio a partir de las dimensiones del libro."
        ),
        py(
            """
VOCAB = 50_257
CONTEXT = 1_024
EMB = 768
LAYERS = 12

tok_emb = VOCAB * EMB
pos_emb = CONTEXT * EMB
qkv = 3 * EMB * EMB                 # qkv_bias=False
out_proj = EMB * EMB + EMB          # la proyección de salida sí lleva sesgo
attn = qkv + out_proj
ffn = EMB * (4 * EMB) + 4 * EMB + (4 * EMB) * EMB + EMB
ln = 2 * EMB                        # scale y shift de una LayerNorm
block = attn + ffn + 2 * ln
tied = tok_emb + pos_emb + LAYERS * block + ln
head = VOCAB * EMB
untied = tied + head

print(f"Embeddings: {tok_emb:,} + {pos_emb:,} = {tok_emb + pos_emb:,}")
print(f"Atención por bloque: {attn:,} (QKV {qkv:,} + salida {out_proj:,})")
print(f"FFN por bloque: {ffn:,}")
print(f"Bloque completo: {block:,}")
print(f"12 bloques + embeddings + LN final: {tied:,}")
print(f"Cabeza de salida: {head:,}")
print(f"Sin atar pesos: {untied:,}")
print(f"Memoria fp32 sin atar: {untied * 4 / 1024**2:.2f} MB")
""",
            caption=(
                "Conteo de parámetros de GPT-2 small. La última línea aplica 4 bytes por "
                "parámetro en coma flotante de 32 bits."
            ),
        ),
        p(
            "El resultado coincide con el libro: 124 412 160 parámetros con pesos atados y "
            "163 009 536 sin atarlos. La diferencia son exactamente los 38 597 376 de la "
            "cabeza de salida, que duplica la tabla de embeddings. En coma flotante de 32 "
            "bits, el modelo sin atar ocupa 621,83 MB; solo guardar los pesos ya es un "
            "ejercicio de memoria. El libro implementa la cabeza separada para poder "
            "entrenar y comparar, y deja la compartición de pesos para el capítulo 6, "
            "cuando carga los pesos preentrenados."
        ),
        callout(
            "note",
            "124 M no es un número redondo",
            "El total exacto es 124 412 160. Si ves 163 009 536, no es un error: es el "
            "mismo modelo con una cabeza de salida independiente. La diferencia entre "
            "ambas cifras —38,6 M— es la matriz que proyecta 768 dimensiones al "
            "vocabulario. GPT-2 original reutiliza la matriz de embeddings para ahorrar "
            "memoria y cómputo.",
        ),
        check(
            "Si la cabeza de salida tiene 38,6 M de parámetros, ¿por qué el modelo se "
            "considera de 124 M y no de 163 M?",
            "Porque en la arquitectura original de GPT-2 la cabeza de salida comparte los "
            "pesos con la tabla de embeddings de tokens. No son 38,6 M adicionales, sino "
            "la misma matriz reutilizada. Al contarlos por separado, como hace la "
            "implementación del libro, aparecen los 163 M.",
        ),
        keypoints(
            [
                "La configuración de GPT-2 small se resume en siete claves: vocabulario, contexto, dimensión, cabezas, capas, dropout y sesgo QKV.",
                "Cada token se representa con 768 dimensiones y cada cabeza de atención trabaja con 64.",
                "Los embeddings de tokens aportan 38 597 376 parámetros; los posicionales, 786 432.",
                "La atención y la FFN de cada bloque suman unos 7,09 M de parámetros; doce bloques, unos 85,03 M.",
                "Con pesos atados el total es 124 412 160; con cabeza separada, 163 009 536.",
                "El modelo pequeño no es una versión de juguete: es la misma arquitectura, con dimensiones manejables.",
            ]
        ),
    ),
    key_points=(
        "La configuración fija vocabulario, contexto, dimensión, cabezas y capas.",
        "Los embeddings de tokens son la tabla más grande del modelo.",
        "La atención y la FFN se repiten en cada uno de los doce bloques.",
        "El total exacto con pesos atados es 124 412 160 parámetros.",
        "La cabeza separada añade 38,6 M y lleva el total a 163 009 536.",
        "Un GPT pequeño permite entender y entrenar la misma arquitectura.",
    ),
)
