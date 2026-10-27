"""Glosario del capítulo 3 (ES)."""

from webapp.content.schema import GlossaryTerm

GLOSSARY: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="atención",
        definition=(
            "Mecanismo que calcula pesos sobre las posiciones de una secuencia y mezcla sus "
            "representaciones según su relevancia para una consulta. En los LLM, sustituye al "
            "resumen único de los modelos recurrentes."
        ),
        lesson="self-attention",
    ),
    GlossaryTerm(
        term="consulta",
        definition=(
            "Proyección de un token que expresa qué información busca en las demás posiciones. "
            "Se compara con las claves mediante un producto escalar para producir puntuaciones."
        ),
        lesson="consultas-claves-valores",
    ),
    GlossaryTerm(
        term="clave",
        definition=(
            "Proyección de un token que indica qué ofrece a las consultas de los demás tokens. "
            "Las claves se comparan con cada consulta y determinan el reparto de atención."
        ),
        lesson="consultas-claves-valores",
    ),
    GlossaryTerm(
        term="valor",
        definition=(
            "Proyección de un token que contiene el contenido que se mezcla cuando recibe "
            "atención. El vector de contexto es una suma ponderada de valores, no de claves."
        ),
        lesson="consultas-claves-valores",
    ),
    GlossaryTerm(
        term="producto escalar",
        definition=(
            "Operación que multiplica dos vectores componente a componente y suma los productos. "
            "En atención mide la alineación entre una consulta y una clave: cuanto mayor es, más "
            "se parecen en esa dirección."
        ),
        lesson="self-attention",
    ),
    GlossaryTerm(
        term="producto escalado",
        definition=(
            "Variante de la atención que divide las puntuaciones QKᵀ por la raíz de la dimensión "
            "de las claves antes de softmax. Evita que las puntuaciones crezcan con la dimensión "
            "y que la distribución se sature."
        ),
        lesson="producto-escalado",
    ),
    GlossaryTerm(
        term="softmax",
        definition=(
            "Función que convierte una fila de puntuaciones en pesos positivos que suman uno. En "
            "atención se aplica después del escalado y, si es causal, después de la máscara."
        ),
        lesson="producto-escalado",
    ),
    GlossaryTerm(
        term="máscara causal",
        definition=(
            "Restricción que impide a cada posición atender a tokens futuros. Se implementa "
            "sustituyendo las puntuaciones futuras por −∞ antes de softmax, de modo que su peso "
            "quede exactamente en cero."
        ),
        lesson="mascara-causal",
    ),
    GlossaryTerm(
        term="peso de atención",
        definition=(
            "Valor normalizado que indica cuánto contribuye una posición al contexto de otra. "
            "Se calcula para cada entrada y cambia con la frase; no es un parámetro entrenable "
            "del modelo."
        ),
        lesson="self-attention",
    ),
    GlossaryTerm(
        term="puntuación de atención",
        definition=(
            "Resultado sin normalizar de comparar una consulta con una clave, normalmente un "
            "producto escalar. Se escala y se pasa por softmax para obtener los pesos."
        ),
        lesson="self-attention",
    ),
    GlossaryTerm(
        term="cabeza de atención",
        definition=(
            "Una de las atenciones paralelas de un bloque multi-head. Cada cabeza tiene sus "
            "propias proyecciones Q, K y V y trabaja con d_modelo / h dimensiones."
        ),
        lesson="multi-head-attention",
    ),
    GlossaryTerm(
        term="vector de contexto",
        definition=(
            "Representación de un token construida como suma ponderada de los valores de la "
            "secuencia. Sustituye al embedding aislado en las capas siguientes del transformer."
        ),
        lesson="self-attention",
    ),
    GlossaryTerm(
        term="alineación",
        definition=(
            "Correspondencia entre posiciones de dos secuencias, por ejemplo entre las palabras "
            "de una frase y las de su traducción. La atención facilita alineaciones blandas sin "
            "una correspondencia palabra a palabra."
        ),
        lesson="por-que-atencion",
    ),
    GlossaryTerm(
        term="coste cuadrático",
        definition=(
            "Crecimiento del trabajo de atención proporcional a n², porque cada uno de los n "
            "tokens se compara con los n tokens de la secuencia. Se cuenta por cabeza y por capa."
        ),
        lesson="atencion-en-gpt",
    ),
)
