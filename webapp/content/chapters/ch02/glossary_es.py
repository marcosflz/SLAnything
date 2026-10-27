"""Glosario del capítulo 2 (ES)."""

from webapp.content.schema import GlossaryTerm

GLOSSARY: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="BPE",
        definition=(
            "Byte pair encoding: algoritmo que construye un vocabulario de subpalabras "
            "fusionando iterativamente los pares de símbolos más frecuentes de un corpus."
        ),
        lesson="byte-pair-encoding",
    ),
    GlossaryTerm(
        term="fusión",
        definition=(
            "Operación de BPE que convierte un par de símbolos adyacentes en un único símbolo "
            "nuevo. Cada fusión añade una entrada al vocabulario."
        ),
        lesson="byte-pair-encoding",
    ),
    GlossaryTerm(
        term="subpalabra",
        definition=(
            "Fragmento de una palabra que el tokenizador trata como unidad. Permite representar "
            "términos nuevos combinando piezas conocidas."
        ),
        lesson="tokens-y-vocabulario",
    ),
    GlossaryTerm(
        term="vocabulario",
        definition=(
            "Conjunto finito y ordenado de tokens que un modelo puede representar, junto con la "
            "correspondencia entre cada token y su identificador."
        ),
        lesson="tokens-y-vocabulario",
    ),
    GlossaryTerm(
        term="ID de token",
        definition=(
            "Entero que identifica un token dentro del vocabulario. Es una clave de consulta, no "
            "una representación semántica."
        ),
        lesson="tokens-y-vocabulario",
    ),
    GlossaryTerm(
        term="token especial",
        definition=(
            "Token que no representa una palabra corriente y cumple una función estructural, "
            "como marcar un documento, el final de una secuencia o el relleno de un lote."
        ),
        lesson="tokens-especiales",
    ),
    GlossaryTerm(
        term="fuera del vocabulario",
        definition=(
            "Situación de una pieza de texto que no tiene entrada en el vocabulario del "
            "tokenizador. Sin subpalabras ni un token desconocido, provoca un error de codificación."
        ),
        lesson="tokens-especiales",
    ),
    GlossaryTerm(
        term="decodificación",
        definition=(
            "Proceso inverso a la codificación: convertir una secuencia de IDs en tokens y unir "
            "esos tokens para reconstruir texto."
        ),
        lesson="tokens-especiales",
    ),
    GlossaryTerm(
        term="ventana deslizante",
        definition=(
            "Técnica que recorta una secuencia larga en fragmentos de longitud fija y avanza un "
            "paso entre fragmentos para generar ejemplos de entrenamiento."
        ),
        lesson="ventana-deslizante",
    ),
    GlossaryTerm(
        term="stride",
        definition=(
            "Número de tokens que avanza la ventana entre un ejemplo y el siguiente. Un stride "
            "menor produce más solapamiento y más ejemplos."
        ),
        lesson="ventana-deslizante",
    ),
    GlossaryTerm(
        term="par entrada-objetivo",
        definition=(
            "Par formado por una secuencia de entrada y la misma secuencia desplazada un token, "
            "que se usa como objetivo para predecir el siguiente token."
        ),
        lesson="pares-entrada-objetivo",
    ),
    GlossaryTerm(
        term="similitud coseno",
        definition=(
            "Medida de la dirección compartida por dos vectores: el producto escalar dividido "
            "por el producto de sus normas. Va de −1 a 1 e ignora la longitud."
        ),
        lesson="embeddings-y-significado",
    ),
    GlossaryTerm(
        term="matriz de embeddings",
        definition=(
            "Tabla de tamaño vocabulario × dimensión cuyas filas son los vectores aprendidos de "
            "los tokens. La capa de embeddings selecciona una fila por ID."
        ),
        lesson="vocabulario-y-embeddings",
    ),
    GlossaryTerm(
        term="embedding posicional",
        definition=(
            "Vector que se suma al embedding del token para indicar su posición en la secuencia. "
            "Sin él, la atención no distingue el orden de las palabras."
        ),
        lesson="repaso-texto",
    ),
)
