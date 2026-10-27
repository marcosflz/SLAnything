"""Lección 4 · Pérdida y desbalance."""

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
    number=4,
    slug="perdida-clasificacion",
    title="Pérdida y desbalance",
    summary=(
        "La entropía cruzada convierte la confianza en un error optimizable; el "
        "desbalance obliga a ponderar clases o a mirar métricas por clase."
    ),
    minutes=10,
    objectives=(
        "Calcular la entropía cruzada de una predicción binaria.",
        "Explicar por qué la accuracy es engañosa con clases desbalanceadas.",
        "Comparar submuestreo y pesos de clase como respuestas al desbalance.",
        "Relacionar la pérdida inicial del libro con la calibración del modelo.",
    ),
    blocks=(
        lead(
            "La accuracy cuenta aciertos, pero no es diferenciable: no podemos calcular su "
            "gradiente para actualizar los pesos. El entrenamiento necesita una función "
            "suave que castigue las predicciones equivocadas y, sobre todo, las "
            "equivocadas con exceso de confianza. Esa función es la entropía cruzada. Con "
            "clases desbalanceadas, además, hay que evitar que el modelo aprenda a acertar "
            "siempre la clase mayoritaria."
        ),
        h2("La pérdida que sí se puede optimizar"),
        p(
            "Para una clasificación binaria, la <strong>entropía cruzada</strong> es "
            "<code>-log(p_verdadera)</code>, donde <code>p_verdadera</code> es la "
            "probabilidad que el modelo asigna a la clase correcta. Si el modelo da un 90 % "
            "a la etiqueta correcta, la pérdida es <code>-ln(0,9) ≈ 0,105</code>. Si da un "
            "50 %, sube a <code>0,693</code>, el valor de una moneda justa. Si solo da un "
            "10 %, alcanza <code>2,303</code>. La curva crece muy rápido cuando la respuesta "
            "correcta recibe poca probabilidad: ahí está el castigo a la confianza mal "
            "calibrada."
        ),
        table(
            ["Probabilidad de la clase correcta", "Entropía cruzada", "Lectura"],
            [
                ["0,90", "0,105", "Predicción segura y acertada"],
                ["0,50", "0,693", "Duda propia de una moneda"],
                ["0,10", "2,303", "Error con alta confianza"],
            ],
            caption="Valores de -ln(p) para tres niveles de confianza.",
        ),
        p(
            "En un lote, la pérdida es la media de los valores individuales. El libro calcula "
            "la pérdida inicial antes de ajustar nada, en una estimación de cinco lotes: "
            "3,095 en entrenamiento, 2,583 en validación y 2,322 en prueba. Son valores muy por encima de 0,693 porque el "
            "modelo, recién adaptada la cabeza, reparte mal sus probabilidades. Esa cifra no "
            "mide «cuánto sabe» en abstracto: mide cuánto castiga la función a las respuestas "
            "actuales. Tras cinco épocas, la pérdida de entrenamiento baja a 0,083 y la de "
            "validación a 0,074."
        ),
        h2("Cuando el 95 % no significa nada"),
        p(
            "Imagina un conjunto con 95 mensajes ham y 5 spam. Un modelo que siempre diga "
            "«ham» acierta 95 de 100 y exhibe una accuracy del 95 %. Sin embargo, su "
            "recall sobre spam es cero: no detecta ninguno de los cinco casos que importan. "
            "La accuracy global premia la clase mayoritaria y esconde el fallo. El mismo "
            "efecto aparece en el dataset original del libro, donde el 86,6 % de los mensajes "
            "es ham: un clasificador trivial superaría el 86 % sin aprender nada útil."
        ),
        p(
            "Hay dos familias de soluciones. La primera es cambiar los datos: el libro "
            "submuestrea la clase mayoritaria hasta igualar 747 ejemplos por clase. La "
            "segunda es cambiar la pérdida: se asigna un <strong>peso de clase</strong> "
            "mayor a la clase minoritaria. Una fórmula habitual es "
            "<code>w_c = N / (2 · N_c)</code>, que normaliza los pesos para que su media sea "
            "1. Con un 5 % de positivos, el peso del positivo sería 10 y el del negativo "
            "0,526: el modelo tendría que esforzarse unas 19 veces más para acertar un spam "
            "que un ham. En el dataset del libro, sin submuestrear, el peso del spam sería "
            "aproximadamente 3,7 frente a 0,58 para ham."
        ),
        p(
            "La versión ponderada se implementa multiplicando el término de cada ejemplo "
            "por el peso de su clase antes de promediar el lote. Así, un error en spam "
            "contribuye más al gradiente que un error en ham, y el modelo no puede salir "
            "del paso prediciendo siempre la clase frecuente. El precio es que la pérdida "
            "deja de ser una estimación directa de la accuracy: es un objetivo diseñado "
            "para que el aprendizaje preste atención a lo que nos importa."
        ),
        callout(
            "warning",
            "Cambiar la pérdida no cambia la realidad",
            "Ponderar clases ayuda a que el modelo preste atención a la minoría, pero no "
            "inventa información. Si los spam son ambiguos o están mal etiquetados, un peso "
            "alto solo amplifica el ruido. Antes de tocar la pérdida, revisa etiquetas, "
            "duplicados y solapamiento entre splits."
        ),
        check(
            "Un modelo tiene una accuracy del 95 % y un recall de spam del 0 %. ¿Qué está "
            "pasando y qué métrica mirarías después?",
            "Está prediciendo siempre la clase mayoritaria. La accuracy alta refleja el "
            "desbalance, no la capacidad de detectar spam. Miraría la matriz de confusión y "
            "la precisión/recall de la clase positiva; probablemente también el F1 y el "
            "coste de los falsos negativos.",
        ),
        keypoints(
            [
                "La entropía cruzada es -log de la probabilidad asignada a la clase correcta.",
                "Castiga con fuerza las predicciones erróneas pero seguras.",
                "La pérdida media de un lote es el objetivo que se minimiza.",
                "Con desbalance, una accuracy alta puede ocultar un recall nulo.",
                "El submuestreo equilibra los datos; los pesos de clase equilibran la pérdida.",
                "La pérdida inicial del libro supera 2,3 porque la cabeza nueva está mal calibrada.",
            ]
        ),
    ),
    key_points=(
        "La entropía cruzada sustituye a la accuracy porque es diferenciable.",
        "La confianza equivocada se penaliza de forma no lineal.",
        "La accuracy global no basta cuando las clases están desbalanceadas.",
        "Submuestrear y ponderar clases son estrategias complementarias.",
        "La pérdida inicial mide calibración, no conocimiento del dominio.",
    ),
)
