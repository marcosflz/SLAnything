"""Lección 6 · Evaluar y generar."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
)

LESSON = Lesson(
    number=6,
    slug="evaluacion-y-generacion",
    title="Evaluar y generar",
    summary=(
        "La pérdida de validación detecta el sobreajuste; las estrategias de decodificación "
        "controlan cuánta variedad tiene el texto que produce el modelo."
    ),
    minutes=11,
    objectives=(
        "Comparar la pérdida de entrenamiento con la de validación.",
        "Reconocer el sobreajuste y proponer medidas para reducirlo.",
        "Distinguir evaluación numérica de inspección cualitativa.",
        "Explicar greedy decoding, temperatura y top-k.",
    ),
    blocks=(
        lead(
            "Un modelo puede mejorar su pérdida de entrenamiento y, al mismo tiempo, "
            "empeorar en texto nuevo. Evaluar bien exige dos miradas: una curva de "
            "validación que no se engaña y una muestra generada que se pueda leer. La "
            "primera detecta el sobreajuste; la segunda revela qué tipo de texto produce el "
            "modelo."
        ),
        h2("Dos curvas, una decisión"),
        p(
            "La pérdida de entrenamiento se calcula con los mismos datos que actualizan los "
            "pesos. La de validación se calcula con texto que el modelo no ha visto. Al "
            "principio ambas bajan: el modelo aprende regularidades útiles. Cuando la de "
            "entrenamiento sigue bajando y la de validación se estanca o sube, el modelo "
            "empieza a memorizar detalles del corpus. En el ejemplo del libro, tras diez "
            "épocas la pérdida de entrenamiento es 0,391 y la de validación, 6,452. La "
            "brecha es enorme porque el corpus es minúsculo y el modelo lo ha visto muchas "
            "veces."
        ),
        p(
            "La evaluación se hace con <code>model.eval()</code> para desactivar el dropout "
            "y con <code>torch.no_grad()</code> para no construir gradientes. También se "
            "puede limitar el número de lotes evaluados con <code>num_batches</code>, lo que "
            "acelera el seguimiento durante el entrenamiento. Esa estimación parcial es "
            "ruidosa, pero suficiente para detectar tendencias. Al final conviene evaluar "
            "todos los lotes del conjunto de validación."
        ),
        p(
            "En el libro, la pérdida de validación se estanca a partir de la segunda época. "
            "Eso no significa que el modelo sea inútil: significa que ya no generaliza mejor "
            "con más pasadas sobre ese corpus. La perplejidad de validación, "
            "exp(6,452) ≈ 633, sigue siendo alta, pero es mucho menor que la inicial. La "
            "conclusión práctica es que el tamaño y la variedad de los datos importan tanto "
            "como el número de épocas."
        ),
        h2("Qué hacer si la validación se estanca"),
        p(
            "La primera medida es conseguir más datos o más variedad. La segunda es reducir "
            "la capacidad efectiva: bajar el número de parámetros, aumentar el dropout o "
            "subir el weight decay. También se puede aplicar <em>early stopping</em>: "
            "guardar el checkpoint con mejor pérdida de validación y detener el entrenamiento "
            "cuando deja de mejorar durante varias evaluaciones. En corpus grandes, una sola "
            "época puede ser suficiente; en uno pequeño, diez épocas casi garantizan "
            "memorización."
        ),
        p(
            "No conviene elegir hiperparámetros mirando el conjunto de validación una y otra "
            "vez. Si se ajusta con él, se contamina y deja de ser una estimación honesta. "
            "Para decisiones importantes se reserva un tercer conjunto de prueba, que se usa "
            "una sola vez al final. La validación sirve para tomar decisiones durante el "
            "desarrollo; el test, para reportar el resultado."
        ),
        h2("Generar no es evaluar"),
        p(
            "La pérdida mide la probabilidad del token correcto, pero no dice si el texto "
            "generado es útil, original o seguro. Para generar, el modelo parte de un "
            "contexto y elige un token; lo añade y repite. La estrategia más simple es "
            "<strong>greedy decoding</strong>: elegir siempre el token más probable con "
            "<code>argmax</code>. Es determinista y suele producir texto repetitivo, porque "
            "no explora alternativas. El modelo entrenado con <em>The Verdict</em> llega a "
            "copiar pasajes literales del cuento cuando se usa greedy."
        ),
        p(
            "La <strong>temperatura</strong> divide los logits antes del softmax. Por debajo "
            "de 1, la distribución se agudiza y el modelo se vuelve conservador; por encima "
            "de 1, se aplana y aparecen opciones menos probables. El <strong>top-k</strong> "
            "recorta la cola: conserva los <code>k</code> logits mayores, pone el resto a "
            "menos infinito y renormaliza. Así se evita muestrear un token absurdo con una "
            "probabilidad ínfima. En el libro, una temperatura de 1,4 con top-k 25 produce un "
            "texto distinto del pasaje memorizado, más variado y también más arriesgado."
        ),
        callout(
            "warning",
            "Una muestra bonita no demuestra que el modelo sea bueno",
            "Puedes encontrar una generación afortunada y concluir que el modelo ha "
            "aprendido. Es una muestra de tamaño uno. La evaluación seria combina pérdida en "
            "un conjunto reservado, varias generaciones con la misma configuración y, si es "
            "posible, una tarea con criterio objetivo. La perplejidad tampoco mide verdad, "
            "utilidad ni seguridad: solo mide cuánta probabilidad concede a los tokens "
            "reales."
        ),
        check(
            "La pérdida de entrenamiento baja de 1,2 a 0,3, pero la de validación sube de 2,1 "
            "a 2,8. ¿Qué está ocurriendo y qué harías?",
            "El modelo se está sobreajustando: mejora en los datos que ve y pierde "
            "generalización. Revisaría el tamaño y la variedad del corpus, reduciría las "
            "épocas o aplicaría early stopping, y probaría más dropout o weight decay. "
            "También comprobaría que no hay fuga de datos entre entrenamiento y validación."
        ),
        keypoints(
            [
                "La pérdida de validación mide generalización; la de entrenamiento, ajuste.",
                "Una brecha creciente entre ambas es la señal típica de sobreajuste.",
                "En el libro, la validación se estanca en 6,452 mientras el train baja a 0,391.",
                "Más datos, dropout, weight decay y early stopping combaten el sobreajuste.",
                "Greedy decoding es determinista, pero tiende a repetir y memorizar.",
                "Temperatura y top-k controlan la variedad y el riesgo al muestrear.",
                "Una generación aislada no sustituye a una evaluación sistemática.",
            ]
        ),
    ),
    key_points=(
        "Entrenamiento y validación miden cosas distintas: ajuste y generalización.",
        "La divergencia de las curvas indica sobreajuste.",
        "Evaluar requiere model.eval() y torch.no_grad().",
        "Greedy, temperatura y top-k son estrategias de decodificación, no de entrenamiento.",
        "La perplejidad no mide verdad ni utilidad.",
        "Una muestra afortunada no basta como evidencia.",
    ),
)
