"""Lección 4 · AdamW y el learning rate."""

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
    slug="optimizador-y-lr",
    title="AdamW y el learning rate",
    summary=(
        "AdamW adapta el paso de cada peso y separa la regularización; la tasa de "
        "aprendizaje decide cuánto avanza el modelo en cada actualización."
    ),
    minutes=10,
    objectives=(
        "Explicar qué guardan los momentos de Adam.",
        "Distinguir el decaimiento de pesos de AdamW del de Adam clásico.",
        "Relacionar la tasa de aprendizaje con la estabilidad del entrenamiento.",
        "Describir para qué sirven el warmup y el decaimiento coseno.",
    ),
    blocks=(
        lead(
            "Elegir un optimizador no es buscar una fórmula mágica. Es decidir cómo repartir "
            "el paso de actualización entre parámetros con gradientes muy distintos. "
            "<strong>AdamW</strong> resuelve la parte adaptativa y la regularización; la "
            "<strong>tasa de aprendizaje</strong> decide la escala del movimiento. Juntos "
            "explican buena parte de que un entrenamiento converja o se descontrole."
        ),
        h2("Adam en dos momentos"),
        p(
            "Adam mantiene dos estimaciones por cada peso: el primer momento, una media "
            "móvil del gradiente, y el segundo, una media móvil del gradiente al cuadrado. La "
            "primera da dirección; la segunda mide la magnitud reciente y permite dividir el "
            "paso por una escala adaptada a cada parámetro. Los coeficientes habituales son "
            "0,9 para el primer momento y 0,999 para el segundo. Al principio las medias "
            "están sesgadas hacia cero, así que Adam aplica una corrección de sesgo antes de "
            "usarlas. El resultado es un paso que se comporta de forma parecida en "
            "parámetros con gradientes grandes y pequeños."
        ),
        p(
            "Esa adaptación acelera la convergencia, pero también puede amplificar el ruido "
            "cuando el segundo momento es muy pequeño. Por eso los frameworks añaden una "
            "pequeña constante de estabilidad, <code>eps</code>, en el denominador. En un "
            "transformer, los embeddings, las matrices de atención y las capas "
            "feed-forward reciben gradientes de magnitudes muy distintas; Adam equilibra "
            "parcialmente esas diferencias y evita que unos pesos se muevan mucho más que "
            "otros solo por la escala de su gradiente."
        ),
        h2("Por qué AdamW"),
        p(
            "El decaimiento de pesos es una regularización que empuja los pesos hacia cero "
            "para limitar su tamaño. En Adam clásico, ese término se suma al gradiente y "
            "acaba mezclado con los momentos adaptativos: el efecto de la regularización "
            "depende de la escala del gradiente. <strong>AdamW</strong> lo aplica de forma "
            "desacoplada, directamente sobre el peso, después del paso adaptativo. Así el "
            "decaimiento conserva su significado y no interfiere con la estimación de los "
            "momentos. Es la variante que usa el libro para preentrenar el GPT pequeño."
        ),
        table(
            ["Hiperparámetro", "Valor del libro", "Qué controla"],
            [
                ["Optimizador", "AdamW", "Pasos adaptativos con decaimiento desacoplado"],
                ["Tasa de aprendizaje", "0,0004", "Tamaño del paso inicial"],
                ["Weight decay", "0,1", "Presión hacia pesos pequeños"],
                ["Épocas", "10", "Pasadas completas por el corpus"],
                ["Evaluación", "cada 5 pasos", "Frecuencia de las métricas"],
            ],
            caption="Configuración del ejemplo de preentrenamiento del capítulo 5.",
            note=(
                "Son valores de un experimento didáctico, no una receta universal. El "
                "tamaño del lote, la arquitectura y el corpus cambian el óptimo."
            ),
        ),
        h2("Ajustar la tasa de aprendizaje"),
        p(
            "La tasa de aprendizaje multiplica el paso del optimizador. Si es demasiado "
            "alta, la pérdida oscila, se dispara o aparece <code>NaN</code>: el modelo salta "
            "fuera de la región donde la aproximación local del gradiente es válida. Si es "
            "demasiado baja, el entrenamiento avanza, pero necesita muchas más iteraciones "
            "y puede quedarse en una zona pobre. Una tasa de 0,0004 es razonable para el "
            "modelo de 124 M del libro con lotes pequeños; no se traslada sin más a un "
            "modelo grande ni a otro tamaño de lote."
        ),
        p(
            "Dos técnicas habituales mejoran la trayectoria. El <strong>warmup</strong> "
            "empieza con una tasa muy pequeña y la sube durante los primeros pasos, para que "
            "los momentos de Adam se estabilicen antes de dar pasos grandes. El "
            "<strong>decaimiento coseno</strong> reduce después la tasa siguiendo una curva "
            "suave hasta cerca de cero, de modo que el final del entrenamiento haga ajustes "
            "finos. A veces se añade <strong>gradient clipping</strong>: si la norma del "
            "gradiente supera un umbral, se reescala para evitar actualizaciones "
            "desproporcionadas. El libro presenta estas variantes en el apéndice D; el bucle "
            "básico del capítulo usa una tasa constante."
        ),
        callout(
            "tip",
            "Una tasa no es una constante eterna",
            "Si la pérdida se vuelve ruidosa, prueba a bajarla o a añadir warmup. Si baja "
            "muy despacio y el gradiente es estable, prueba a subirla con cuidado. Registra "
            "la norma del gradiente y la pérdida por paso: sin esas curvas, cambiar "
            "hiperparámetros es adivinar. Un buen punto de partida es reproducir primero la "
            "configuración del libro y modificar una variable cada vez."
        ),
        check(
            "¿Qué aporta el decaimiento de pesos desacoplado de AdamW frente a sumarlo al "
            "gradiente?",
            "Mantiene la regularización separada de los momentos adaptativos. El peso se "
            "encoge con un factor propio, independiente de la escala del gradiente, mientras "
            "el paso de Adam sigue usando los momentos. Eso hace que el efecto del weight "
            "decay sea más predecible y no se amplifique ni se diluya según el parámetro."
        ),
        keypoints(
            [
                "Adam estima media y varianza del gradiente para adaptar el paso por peso.",
                "La corrección de sesgo evita que los momentos iniciales sean demasiado pequeños.",
                "AdamW aplica el decaimiento de pesos de forma desacoplada del gradiente.",
                "El libro usa AdamW con lr 0,0004, weight decay 0,1 y diez épocas.",
                "Una tasa demasiado alta desestabiliza; una demasiado baja ralentiza.",
                "Warmup, decaimiento coseno y gradient clipping estabilizan el entrenamiento.",
            ]
        ),
    ),
    key_points=(
        "Adam adapta el paso con medias móviles del gradiente y de su cuadrado.",
        "AdamW separa el weight decay de la actualización adaptativa.",
        "La tasa de aprendizaje controla el tamaño del paso y la estabilidad.",
        "Warmup suaviza el arranque; el decaimiento coseno afina el final.",
        "El gradient clipping limita actualizaciones desproporcionadas.",
        "Los hiperparámetros del libro son un punto de partida, no una receta universal.",
    ),
)
