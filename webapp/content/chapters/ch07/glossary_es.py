"""Glosario del capítulo 7 (ES)."""

from webapp.content.schema import GlossaryTerm

GLOSSARY_ES: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="ajuste supervisado de instrucciones",
        definition=(
            "Entrenamiento que adapta un modelo preentrenado con pares de instrucción y "
            "respuesta, manteniendo la pérdida de siguiente token pero cambiando los datos y "
            "la máscara. También se abrevia SFT."
        ),
        lesson="instrucciones-y-sft",
    ),
    GlossaryTerm(
        term="par instrucción-respuesta",
        definition=(
            "Unidad de datos del SFT: una petición, un contexto opcional y una respuesta de "
            "referencia. La calidad y la diversidad de estos pares condicionan el comportamiento "
            "aprendido."
        ),
        lesson="datos-de-instrucciones",
    ),
    GlossaryTerm(
        term="plantilla de chat",
        definition=(
            "Función que convierte roles y mensajes en una secuencia de texto con marcadores. "
            "Debe ser la misma en entrenamiento e inferencia para no cambiar la distribución "
            "de entrada."
        ),
        lesson="plantillas-chat",
    ),
    GlossaryTerm(
        term="enmascaramiento de pérdida",
        definition=(
            "Sustitución de ciertos objetivos por un valor que la función de pérdida ignora, "
            "para que no contribuyan al entrenamiento. Se usa con el relleno y, opcionalmente, "
            "con la instrucción."
        ),
        lesson="mascara-de-perdida",
    ),
    GlossaryTerm(
        term="ignore_index",
        definition=(
            "Valor especial que cross_entropy descarta al calcular la pérdida. En PyTorch vale "
            "-100 por defecto, y por eso se usa para marcar el relleno de los objetivos."
        ),
        lesson="mascara-de-perdida",
    ),
    GlossaryTerm(
        term="función de ensamblado",
        definition=(
            "Función que recibe una lista de ejemplos y construye un lote: rellena secuencias, "
            "desplaza los objetivos y aplica la máscara. En PyTorch se pasa a DataLoader como "
            "collate_fn."
        ),
        lesson="mascara-de-perdida",
    ),
    GlossaryTerm(
        term="LLM juez",
        definition=(
            "Modelo de lenguaje usado para puntuar respuestas según una rúbrica, a menudo con "
            "una referencia. Es escalable, pero aproxima el juicio humano y puede tener sesgos "
            "de longitud, orden o modelo."
        ),
        lesson="evaluar-instrucciones",
    ),
    GlossaryTerm(
        term="par de preferencia",
        definition=(
            "Dos respuestas a la misma petición, una preferida y otra rechazada. Es la señal "
            "que usan RLHF y DPO para aprender criterios de calidad que una única referencia "
            "no captura."
        ),
        lesson="preferencias-y-seguridad",
    ),
    GlossaryTerm(
        term="DPO",
        definition=(
            "Optimización directa de preferencias: ajusta el modelo con pares preferida/"
            "rechazada sin entrenar un modelo de recompensa separado. Mantiene una referencia "
            "y un parámetro que limita el alejamiento."
        ),
        lesson="preferencias-y-seguridad",
    ),
    GlossaryTerm(
        term="modelo de recompensa",
        definition=(
            "Modelo que asigna una puntuación a una respuesta a partir de comparaciones "
            "humanas. RLHF lo usa para guiar la optimización de la política; un reward model "
            "mal calibrado puede ser explotado."
        ),
        lesson="preferencias-y-seguridad",
    ),
)

__all__ = ["GLOSSARY_ES"]
