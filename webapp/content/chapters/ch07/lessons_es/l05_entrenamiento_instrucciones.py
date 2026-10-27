"""Lección 5 · Entrenar con instrucciones."""

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
    number=5,
    slug="entrenamiento-instrucciones",
    title="Entrenar instrucciones",
    summary=(
        "El ajuste reutiliza el bucle del pretraining con lotes, una tasa de aprendizaje "
        "baja y pocas épocas. La pérdida guía, pero las respuestas generadas deciden."
    ),
    minutes=11,
    objectives=(
        "Describir la configuración del experimento del libro.",
        "Interpretar las curvas de pérdida de entrenamiento y validación.",
        "Detectar señales de sobreajuste y decidir cuándo detener.",
        "Relacionar tamaño del modelo, lote y hardware con el coste.",
    ),
    blocks=(
        lead(
            "Con el dataset formateado y los lotes enmascarados, el entrenamiento se parece "
            "mucho al del pretraining: un bucle, un optimizador y una pérdida de siguiente "
            "token. Lo que cambia es la escala y la prudencia. Un ajuste de instrucciones "
            "suele necesitar pocas épocas, una tasa de aprendizaje baja y una mirada atenta "
            "a las respuestas, no solo al número de pérdida."
        ),
        p(
            "El libro parte de GPT-2 mediano, con 355 millones de parámetros, y lo ajusta "
            "durante <strong>dos épocas</strong> con AdamW, una tasa de aprendizaje de "
            "<strong>5 × 10⁻⁵</strong> y un decaimiento de pesos de 0,1. El lote es de "
            "8 ejemplos y la longitud máxima se limita a 1024 tokens. La evaluación se hace "
            "cada cinco pasos sobre cinco lotes, y además se genera una respuesta de "
            "validación para inspeccionarla. Estos valores son del experimento del libro; "
            "no son una receta universal, pero sí un punto de partida razonable para un "
            "modelo de este tamaño."
        ),
        h2("Qué observar durante el entrenamiento"),
        p(
            "Antes de entrenar, el libro mide la pérdida inicial: aproximadamente 3,83 en "
            "entrenamiento y 3,76 en validación. Al cabo de dos épocas, la pérdida de "
            "entrenamiento baja a 0,300 y la de validación a 0,657. La caída rápida inicial "
            "indica que el modelo capta el formato y la tarea; la separación posterior entre "
            "ambas curvas es la señal que hay que vigilar. Una pérdida de entrenamiento muy "
            "baja con una de validación que deja de mejorar sugiere que el modelo está "
            "memorizando ejemplos en lugar de generalizar."
        ),
        table(
            ["Modelo", "Equipo", "Tiempo para 2 épocas"],
            [
                ["GPT-2 mediano (355 M)", "CPU Apple M3", "15,78 min"],
                ["GPT-2 mediano (355 M)", "GPU NVIDIA L4", "1,83 min"],
                ["GPT-2 mediano (355 M)", "GPU NVIDIA A100", "0,86 min"],
                ["GPT-2 pequeño (124 M)", "CPU Apple M3", "5,74 min"],
                ["GPT-2 pequeño (124 M)", "GPU NVIDIA L4", "0,69 min"],
                ["GPT-2 pequeño (124 M)", "GPU NVIDIA A100", "0,39 min"],
            ],
            caption="Tiempos de referencia del libro para el ajuste de instrucciones.",
            note="Son medidas de un entorno concreto; el tiempo real depende del equipo, la longitud de las secuencias y la versión del software.",
        ),
        p(
            "La pérdida es una guía, no el veredicto. Durante el entrenamiento conviene "
            "generar respuestas para la misma instrucción de validación y leerlas. En el "
            "libro, al final de la primera época el modelo ya produce una pasiva correcta; "
            "al final de la segunda, la respuesta es más limpia y termina con el token de "
            "fin. Esa inspección cualitativa detecta problemas que la media de pérdida "
            "esconde: respuestas truncadas, repeticiones, formato incompleto o cambios de "
            "idioma. Si solo se mira el número, se puede celebrar un modelo que ha aprendido "
            "a copiar el estilo del dataset sin resolver la tarea."
        ),
        h2("Sobreajuste, épocas y hardware"),
        p(
            "El libro se queda en dos épocas porque una tercera no aporta una mejora clara y "
            "puede aumentar el sobreajuste. En general, un dataset pequeño y un modelo "
            "relativamente grande son una combinación propensa a memorizar. La defensa es "
            "doble: reservar validación y prueba, y detener el entrenamiento cuando la "
            "validación deja de mejorar. También ayuda revisar la diversidad del conjunto: "
            "si todas las respuestas son largas, el modelo aprenderá a ser largo; si todas "
            "empiezan con la misma fórmula, repetirá la fórmula."
        ),
        p(
            "La tasa de aprendizaje tiene un efecto visible. Demasiado alta puede hacer que "
            "la pérdida oscile o diverga; demasiado baja alarga el entrenamiento y puede "
            "dejar al modelo a medio camino. El tamaño del lote cambia la memoria y la "
            "estabilidad: si no cabe, se reduce el lote o la longitud máxima, y se compensa "
            "con acumulación de gradientes. El modelo pequeño de 124 millones es una "
            "alternativa si el equipo no puede con el mediano, pero el libro advierte que su "
            "capacidad es más limitada. La elección es un compromiso entre calidad, tiempo y "
            "recursos, no una cuestión de orgullo."
        ),
        callout(
            "warning",
            "Una pérdida baja no es una respuesta buena",
            "La pérdida mide la probabilidad asignada a los tokens de referencia, no la "
            "utilidad de la respuesta. Un modelo puede obtener una pérdida excelente y "
            "producir respuestas repetitivas o incorrectas. Combina siempre la curva con "
            "generación, evaluación automática y revisión humana de una muestra.",
        ),
        check(
            "La pérdida de entrenamiento sigue bajando, pero la de validación se estanca. ¿Qué harías?",
            "Detener el entrenamiento o reducir las épocas, revisar una muestra de respuestas "
            "generadas y comprobar si el conjunto de validación representa las peticiones "
            "reales. Seguir bajando la pérdida de entrenamiento no mejora la generalización.",
        ),
        keypoints(
            [
                "El libro ajusta GPT-2 mediano durante dos épocas con lr 5e-5 y lote 8.",
                "La pérdida inicial ronda 3,8; al final, 0,300 en train y 0,657 en validación.",
                "La brecha entre curvas es una señal de sobreajuste, no una medida de calidad.",
                "Leer respuestas generadas detecta fallos que la pérdida no muestra.",
                "Menos épocas y validación temprana protegen un dataset pequeño.",
                "El hardware cambia el tiempo, no el planteamiento del experimento.",
            ]
        ),
    ),
    key_points=(
        "El ajuste reutiliza el bucle del pretraining con una tasa de aprendizaje baja.",
        "Dos épocas bastan en el experimento del libro; más puede sobreajustar.",
        "La pérdida de validación y las respuestas generadas se interpretan juntas.",
        "El tamaño del lote y la longitud máxima determinan el coste de memoria.",
    ),
)
