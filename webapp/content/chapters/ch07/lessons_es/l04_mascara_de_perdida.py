"""Lección 4 · Enmascarar la pérdida."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=4,
    slug="mascara-de-perdida",
    title="Enmascarar la pérdida",
    summary=(
        "En un lote, las secuencias se rellenan y los objetivos se desplazan. La máscara "
        "decide qué posiciones contribuyen a la pérdida y cuáles se ignoran con -100."
    ),
    minutes=11,
    objectives=(
        "Explicar por qué se rellena un lote hasta la secuencia más larga.",
        "Construir los objetivos desplazados y localizar las posiciones de relleno.",
        "Justificar el valor -100 y la conservación de un token de fin.",
        "Distinguir el enmascaramiento de relleno del enmascaramiento de instrucción.",
    ),
    blocks=(
        lead(
            "Una secuencia de instrucciones tiene una longitud distinta de la siguiente. "
            "Para procesarlas juntas, el lote se rellena hasta la más larga, pero el modelo "
            "no debe aprender a predecir relleno. La solución es una máscara: las posiciones "
            "de relleno se sustituyen por un valor que la función de pérdida ignora."
        ),
        p(
            "El proceso del libro tiene cinco pasos: aplicar la plantilla, tokenizar, "
            "rellenar el lote, crear los objetivos desplazados y sustituir el relleno por "
            "<code>-100</code>. El desplazamiento es el mismo del pretraining: "
            "si la entrada es [A, B, C], el objetivo es [B, C, EOS]. El modelo aprende a "
            "predecir cada token a partir de los anteriores. La novedad es que ahora hay "
            "varias secuencias por lote y que algunas terminan antes que otras."
        ),
        h2("Qué posición entra en la pérdida"),
        p(
            "Imagina un lote con una secuencia de tres tokens y otra de cinco. La primera "
            "se rellena con dos posiciones adicionales. Sus objetivos, antes de enmascarar, "
            "podrían ser <code>[B, C, EOS, EOS, EOS]</code>. El primer EOS es informativo: "
            "enseña al modelo a terminar la respuesta. Los dos siguientes son solo relleno. "
            "Si se contaran, el modelo aprendería a emitir EOS una y otra vez y la pérdida "
            "se diluiría con posiciones que no forman parte de la respuesta."
        ),
        figure(
            "img/ch07/mascara-perdida.svg",
            "Diagrama de una secuencia con contexto enmascarado, respuesta activa y posiciones de relleno marcadas con -100.",
            "En la variante solo-respuesta, solo las posiciones verdes contribuyen. La "
            "instrucción puede enmascararse o no; el primer EOS se conserva y el relleno "
            "posterior se ignora con -100.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "El valor <strong>-100</strong> no es arbitrario: es el <code>ignore_index</code> "
            "predeterminado de <code>cross_entropy</code> en PyTorch. La función de pérdida "
            "descarta cualquier objetivo igual a -100, así que el número de posiciones "
            "activas varía entre lotes. Esto explica una aparente colisión: GPT-2 usa el "
            "mismo ID, 50256, para el fin de secuencia y para el relleno. La colisión es "
            "deliberada y se resuelve en los objetivos: se conserva un EOS y se enmascaran "
            "los demás. En la entrada, en cambio, el relleno sigue siendo 50256 para que el "
            "modelo pueda procesar el lote."
        ),
        h2("Instrucción enmascarada: opcional y discutido"),
        p(
            "El enmascaramiento de relleno es necesario. El de la instrucción es otra cosa: "
            "consiste en poner -100 también en los tokens de la petición para que la pérdida "
            "solo se calcule sobre la respuesta. La intuición es razonable: queremos que el "
            "modelo aprenda a responder, no a memorizar la pregunta. El libro no lo aplica "
            "por defecto y lo deja como ejercicio. La investigación no es concluyente: hay "
            "trabajos que defienden enmascarar y otros que obtienen mejores resultados "
            "entrenando también sobre la instrucción, porque así el modelo aprende la "
            "relación completa entre petición y respuesta."
        ),
        p(
            "Antes de elegir, mide. Si enmascaras la instrucción, la pérdida solo refleja la "
            "respuesta y puede reducir el sobreajuste a formulaciones concretas; si no la "
            "enmascaras, la pérdida incluye la petición y el modelo recibe una señal más "
            "rica, aunque también más fácil de memorizar. No hay una respuesta universal: "
            "depende del dataset, del tamaño del modelo y de la evaluación. Lo que sí es "
            "obligatorio es que la máscara sea coherente con la plantilla y que se documente."
        ),
        py(
            """
import math

PAD = 50256
IGNORE = -100

def preparar_objetivos(objetivos):
    vistos = 0
    salida = []
    for token in objetivos:
        if token == PAD:
            vistos += 1
            salida.append(PAD if vistos == 1 else IGNORE)
        else:
            salida.append(token)
    return salida

def perdida_media(probabilidades, objetivos):
    activas = []
    for i, (p, y) in enumerate(zip(probabilidades, objetivos), start=1):
        if y == IGNORE:
            print(f"posición {i}: objetivo {y:>6}  -> ignorada")
        else:
            valor = -math.log(p)
            activas.append(valor)
            print(f"posición {i}: objetivo {y:>6}  -> pérdida {valor:.4f}")
    return sum(activas) / len(activas)

objetivos = preparar_objetivos([120, 340, PAD, PAD, PAD])
probabilidades = [0.80, 0.50, 0.01, 0.01, 0.01]
print("objetivos preparados:", objetivos)
print(f"pérdida media: {perdida_media(probabilidades, objetivos):.4f}")
""",
            caption=(
                "Demostración con pérdidas didácticas: el primer EOS se conserva y el "
                "relleno posterior se ignora. Cambia los valores y comprueba la media."
            ),
        ),
        callout(
            "note",
            "Máscara no es truncado",
            "El límite de longitud, por ejemplo 1024 tokens para GPT-2, corta las secuencias "
            "que no caben. La máscara no corta: decide qué posiciones ya presentes "
            "contribuyen a la pérdida. Son dos controles distintos y conviene registrarlos "
            "por separado.",
        ),
        check(
            "¿Por qué se conserva un token EOS en los objetivos en lugar de enmascararlo todo?",
            "Porque el modelo debe aprender a terminar la respuesta. Si todos los EOS se "
            "sustituyeran por -100, no recibiría señal para cerrar la generación y podría "
            "continuar indefinidamente.",
        ),
        keypoints(
            [
                "Cada lote se rellena hasta su secuencia más larga, no hasta la del dataset.",
                "Los objetivos se desplazan una posición a la derecha.",
                "El primer EOS se conserva; el relleno posterior se marca con -100.",
                "cross_entropy ignora -100 por defecto, así que solo cuenta lo activo.",
                "La colisión entre EOS y relleno se resuelve en el tensor de objetivos.",
                "Enmascarar la instrucción es opcional, discutido y debe medirse.",
            ]
        ),
    ),
    key_points=(
        "El relleno no debe contribuir a la pérdida: se marca con -100.",
        "El primer EOS se conserva para aprender a terminar la respuesta.",
        "La máscara de relleno es obligatoria; la de instrucción es una decisión experimental.",
        "Máscara y truncado son controles distintos.",
    ),
)
