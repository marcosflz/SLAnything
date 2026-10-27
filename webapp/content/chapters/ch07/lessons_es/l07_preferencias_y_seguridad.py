"""Lección 7 · Preferencias, RLHF y seguridad."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    table,
)

LESSON = Lesson(
    number=7,
    slug="preferencias-y-seguridad",
    title="Preferencias, RLHF y seguridad",
    summary=(
        "El SFT imita una respuesta; las preferencias comparan dos. RLHF y DPO optimizan "
        "esa señal, y la seguridad exige datos negativos, evaluación y supervisión."
    ),
    minutes=11,
    objectives=(
        "Explicar qué añade una señal de preferencia frente a una respuesta imitada.",
        "Comparar RLHF con DPO y reconocer el papel del modelo de referencia.",
        "Diseñar ejemplos negativos y criterios de rechazo sin caer en el exceso.",
        "Identificar límites de seguridad que el ajuste no puede garantizar.",
    ),
    blocks=(
        lead(
            "El SFT enseña una respuesta correcta, pero no le dice al modelo qué hacer "
            "cuando dos respuestas son posibles y una es claramente mejor. Las preferencias "
            "añaden esa comparación: ante una misma petición, se muestra una respuesta "
            "preferida y otra rechazada. Es una señal más difícil de recoger y más cercana "
            "a lo que queremos que el modelo haga en producción."
        ),
        p(
            "Una respuesta imitada tiene un objetivo fijo: el modelo aprende a reproducir "
            "los tokens de la referencia. Una preferencia no dice «escribe exactamente "
            "esto», sino «entre estas dos salidas, esta es mejor». Esa diferencia importa "
            "porque muchas tareas no tienen una única respuesta correcta. Un resumen puede "
            "ser más claro sin ser idéntico; una explicación puede ser más útil sin ser más "
            "larga. La preferencia captura criterios como claridad, utilidad, tono o "
            "seguridad que una referencia única no expresa bien."
        ),
        h2("De recompensas a preferencias"),
        p(
            "El enfoque clásico de <strong>RLHF</strong> (aprendizaje por refuerzo con "
            "retroalimentación humana) tiene dos piezas. Primero se entrena un "
            "<strong>modelo de recompensa</strong> que asigna una puntuación a una respuesta "
            "a partir de comparaciones humanas. Después se optimiza la política del modelo "
            "para maximizar esa recompensa, normalmente con PPO y una penalización que evita "
            "alejarse demasiado del modelo de referencia. Es potente, pero también complejo: "
            "hay varios modelos en juego, el entrenamiento es inestable y la política puede "
            "explotar los fallos del reward model."
        ),
        p(
            "<strong>DPO</strong> (optimización directa de preferencias) simplifica el "
            "proceso. En lugar de entrenar un modelo de recompensa separado y ejecutar un "
            "bucle de refuerzo, optimiza directamente el modelo con pares de respuestas "
            "preferida y rechazada, manteniendo una referencia y un parámetro que controla "
            "cuánto puede alejarse. Es más sencillo de implementar y de reproducir, y por eso "
            "se ha popularizado. No es magia: sigue dependiendo de la calidad de las "
            "preferencias, del modelo de referencia y de la evaluación. El libro lo propone "
            "como paso opcional después del SFT y remite al cuaderno de DPO de su repositorio."
        ),
        table(
            ["Enfoque", "Señal", "Piezas principales", "Riesgo típico"],
            [
                ["SFT", "Respuesta de referencia", "Modelo y datos", "Imitar sesgos o errores"],
                ["RLHF", "Comparaciones humanas", "Reward model, política, referencia", "Explotar la recompensa"],
                ["DPO", "Pares preferida/rechazada", "Modelo, referencia, beta", "Sobreajustar preferencias"],
            ],
            caption="Tres formas de enseñar comportamiento. No son excluyentes: DPO suele aplicarse después de un SFT.",
            note="La calidad del dato y la evaluación siguen siendo el factor común.",
        ),
        h2("Seguridad y límites"),
        p(
            "Las preferencias también sirven para enseñar qué no hacer. Un par puede mostrar "
            "una respuesta que rechaza una petición dañina y otra que la acepta; el modelo "
            "aprende a preferir la primera. Pero los ejemplos negativos no bastan. Hay que "
            "cubrir distintos tipos de daño, desde contenido ilegal hasta instrucciones "
            "peligrosas, pasando por la exfiltración de datos o la manipulación. Y hay que "
            "hacerlo sin enseñar un rechazo indiscriminado: un modelo que se niega a todo es "
            "seguro solo en apariencia y resulta inútil."
        ),
        p(
            "La seguridad de un sistema no termina en los pesos. Un atacante puede introducir "
            "instrucciones maliciosas en un documento, en una página web o en el propio "
            "historial de la conversación; es lo que se conoce como inyección de prompts. "
            "También puede buscar sesgos, filtrar información o provocar respuestas "
            "peligrosas mediante combinaciones extrañas. La defensa combina datos, "
            "entrenamiento, filtros de entrada y salida, límites de herramientas, "
            "monitorización y revisión humana. Ninguna capa es suficiente por separado, y "
            "ninguna promete riesgo cero."
        ),
        p(
            "Evaluar seguridad es distinto de evaluar utilidad. Hacen falta pruebas "
            "adversarias, un conjunto de casos reservados, criterios explícitos y una "
            "persona responsable de decidir qué se considera aceptable. Conviene medir tanto "
            "los falsos negativos —daño que se deja pasar— como los falsos positivos "
            "—rechazos innecesarios—. Y conviene repetir la evaluación cuando cambian el "
            "modelo, la plantilla, las herramientas o la política de uso. La seguridad es un "
            "proceso continuo, no un adjetivo que se añade al final."
        ),
        callout(
            "danger",
            "El ajuste no es una barrera de seguridad",
            "Enseñar negativas mejora el comportamiento esperado, pero no convierte al "
            "modelo en infalible. Un sistema responsable necesita amenazas modeladas, "
            "pruebas de penetración, límites de permisos, registro de decisiones y una vía "
            "de escalado humana. No publiques un modelo solo porque «no dijo nada malo» en "
            "una prueba de diez preguntas.",
        ),
        check(
            "¿Qué diferencia práctica hay entre RLHF y DPO?",
            "RLHF entrena un modelo de recompensa y optimiza la política con refuerzo; DPO "
            "optimiza directamente el modelo con pares de respuestas preferidas y "
            "rechazadas, usando una referencia. DPO suele ser más simple, pero ambos "
            "dependen de la calidad de las preferencias.",
        ),
        keypoints(
            [
                "El SFT imita una respuesta; las preferencias comparan dos.",
                "RLHF usa un modelo de recompensa y optimización por refuerzo.",
                "DPO aprende directamente de pares preferida/rechazada.",
                "La señal de preferencia captura criterios sin una única respuesta correcta.",
                "Los ejemplos negativos deben cubrir daños sin enseñar rechazo indiscriminado.",
                "La seguridad incluye datos, filtros, permisos, monitorización y personas.",
            ]
        ),
    ),
    key_points=(
        "Las preferencias añaden una señal de comparación que el SFT no tiene.",
        "RLHF y DPO son enfoques distintos para optimizar esa señal.",
        "La seguridad se evalúa con casos adversarios y supervisión humana.",
        "Ningún ajuste garantiza un sistema seguro por sí solo.",
    ),
)
