"""Lección 3 · El bucle de entrenamiento."""

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
    number=3,
    slug="bucle-de-entrenamiento",
    title="El bucle de entrenamiento",
    summary=(
        "Cinco operaciones repetidas por lote —zero_grad, forward, pérdida, backward y "
        "step— convierten un GPT aleatorio en un modelo que empieza a escribir."
    ),
    minutes=12,
    objectives=(
        "Ordenar correctamente las operaciones de un paso de entrenamiento.",
        "Distinguir el bucle de lotes del bucle de épocas.",
        "Explicar qué hace backward y qué actualiza el optimizador.",
        "Interpretar la pérdida de entrenamiento y la de validación del ejemplo del libro.",
    ),
    blocks=(
        lead(
            "Un GPT no aprende por inspiración: repite un procedimiento muy corto miles de "
            "veces. Cada lote pasa por las mismas cinco operaciones y cada operación tiene "
            "un orden. Cambiar el orden no es un detalle de estilo; puede hacer que el "
            "modelo no aprenda o que los gradientes se acumulen sin control."
        ),
        h2("El paso, operación a operación"),
        p(
            "El ciclo empieza con <code>optimizer.zero_grad()</code>, que vacía los "
            "gradientes del paso anterior. Después se ejecuta el <strong>forward</strong>: el "
            "modelo recibe el lote de entrada y produce logits. Con los logits y los objetivos "
            "se calcula la pérdida mediante entropía cruzada. A continuación, "
            "<code>loss.backward()</code> recorre la red hacia atrás y deja en cada parámetro "
            "el gradiente de la pérdida. Por último, <code>optimizer.step()</code> usa esos "
            "gradientes para actualizar los pesos. El lote siguiente vuelve a empezar."
        ),
        figure(
            "img/ch05/bucle-entrenamiento.svg",
            "Diagrama circular con las cinco operaciones del entrenamiento: lote, forward, backward, step y zero_grad, dentro del bucle de épocas.",
            "El bucle interno recorre los lotes. Al terminarlo se cierra una época y se evalúa "
            "el modelo con datos que no han participado en la actualización.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "La pérdida es un escalar, pero contiene la información de todas las posiciones "
            "del lote. <code>backward()</code> aplica la regla de la cadena desde ese escalar "
            "hasta cada peso. No actualiza nada: solo calcula derivadas. La actualización "
            "ocurre en <code>step()</code>, que consulta los gradientes y la tasa de "
            "aprendizaje. Esta separación permite inspeccionar o recortar los gradientes "
            "antes de aplicarlos."
        ),
        h2("Épocas, evaluación y muestras"),
        p(
            "El bucle externo recorre las <strong>épocas</strong>. Una época es una pasada "
            "completa por el conjunto de entrenamiento. Dentro de cada época, el cargador "
            "entrega los lotes en orden o mezclados. Al final de una época se suele evaluar "
            "el modelo y generar una muestra de texto para comprobar si el avance numérico se "
            "traduce en algo legible. En el ejemplo del libro, el modelo se entrena durante "
            "diez épocas con AdamW, una tasa de 0,0004 y un decaimiento de pesos de 0,1. La "
            "pérdida de entrenamiento baja de 9,781 a 0,391; la de validación baja de 9,933 "
            "a 6,452 y se estanca mucho antes. El proceso tarda unos cinco minutos en un "
            "portátil."
        ),
        p(
            "La evaluación se hace con <code>model.eval()</code> y dentro de "
            "<code>torch.no_grad()</code>. El primer cambio desactiva el dropout; el segundo "
            "evita construir el grafo de gradientes, porque no vamos a actualizar nada. "
            "Mientras se entrena, <code>model.train()</code> reactiva el dropout. Olvidar el "
            "cambio de modo produce resultados inestables y difíciles de reproducir: el "
            "mismo lote puede dar pérdidas distintas según el modo activo."
        ),
        callout(
            "warning",
            "Zero_grad va antes, no después",
            "Si olvidas <code>zero_grad()</code>, los gradientes del lote anterior se suman a "
            "los del actual. El paso efectivo se vuelve más grande y menos predecible. "
            "PyTorch no limpia los gradientes automáticamente porque la acumulación es una "
            "técnica legítima; la responsabilidad es del bucle. La regla práctica es vaciar "
            "al principio de cada iteración, salvo que estés acumulando a propósito."
        ),
        py(
            """
import math

vocabulario = ["azul", "verde", "rojo"]
objetivo = 1
logits = [2.0, 0.2, -0.5]
tasa = 0.8

def softmax(valores):
    maximo = max(valores)
    exponenciales = [math.exp(v - maximo) for v in valores]
    total = sum(exponenciales)
    return [v / total for v in exponenciales]

for paso in range(1, 11):
    probabilidades = softmax(logits)
    perdida = -math.log(probabilidades[objetivo])
    gradientes = probabilidades[:]
    gradientes[objetivo] -= 1.0
    logits = [v - tasa * g for v, g in zip(logits, gradientes)]
    if paso in (1, 5, 10):
        print(
            f"Paso {paso:2d}: pérdida={perdida:.3f} "
            f"p(verde)={probabilidades[objetivo]:.3f}"
        )
""",
            caption=(
                "Un paso de descenso de gradiente sobre tres logits. Es la misma idea que "
                "backward + step, sin red neuronal ni PyTorch."
            ),
        ),
        p(
            "El ejemplo condensa el mecanismo: el gradiente de la entropía cruzada respecto "
            "a los logits es <code>p − onehot(objetivo)</code>. Restar ese gradiente, "
            "multiplicado por la tasa, sube la probabilidad del token correcto y baja la de "
            "los demás. En un transformer, la misma operación se repite para millones de "
            "parámetros, pero la lógica es idéntica. Lo que cambia es la escala y el coste de "
            "calcular las derivadas."
        ),
        h2("Qué mirar durante el entrenamiento"),
        p(
            "Una pérdida que baja no basta como diagnóstico. Hay que comparar la curva de "
            "entrenamiento con la de validación y leer alguna muestra. Si ambas bajan, el "
            "modelo está aprendiendo. Si la de entrenamiento baja y la de validación se "
            "estanca, aparece el sobreajuste. Si la pérdida se dispara o se queda en "
            "<code>NaN</code>, conviene revisar la tasa de aprendizaje, la inicialización y "
            "la estabilidad numérica. El registro periódico de métricas y muestras es parte "
            "del entrenamiento, no un adorno posterior."
        ),
        check(
            "¿Qué diferencia hay entre loss.backward() y optimizer.step()?",
            "backward() calcula los gradientes de la pérdida respecto a los parámetros y los "
            "guarda, pero no modifica los pesos. step() lee esos gradientes, aplica la regla "
            "del optimizador y actualiza los pesos. Primero se calcula la dirección; después "
            "se da el paso."
        ),
        keypoints(
            [
                "Cada lote sigue el orden zero_grad → forward → pérdida → backward → step.",
                "backward() calcula gradientes; step() actualiza los pesos.",
                "Una época es una pasada completa por el conjunto de entrenamiento.",
                "model.eval() y no_grad() se usan para evaluar sin dropout ni gradientes.",
                "En el libro, la pérdida de entrenamiento cae de 9,781 a 0,391 en diez épocas.",
                "La pérdida de validación se estanca en 6,452: señal de sobreajuste.",
                "El bucle debe registrar métricas y muestras, no solo ejecutar pasos.",
            ]
        ),
    ),
    key_points=(
        "El orden del paso de entrenamiento importa: zero_grad antes de backward.",
        "El forward produce logits; la entropía cruzada los convierte en pérdida.",
        "backward calcula gradientes y step actualiza los pesos.",
        "Una época recorre todos los lotes del conjunto de entrenamiento.",
        "Evaluar exige model.eval() y torch.no_grad().",
        "La brecha entre entrenamiento y validación revela sobreajuste.",
    ),
)
