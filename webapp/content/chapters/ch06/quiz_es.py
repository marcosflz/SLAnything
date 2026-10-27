"""Autoevaluación del capítulo 6 en español."""

from webapp.content.schema import Question, Quiz

QUIZZES_ES: dict[str, Quiz] = {
    "quiz-capitulo-6": Quiz(
        id="quiz-capitulo-6",
        title="Autoevaluación · Capítulo 6",
        description=(
            "Diez preguntas sobre el finetuning de clasificación: datos, cabeza, pérdida, "
            "entrenamiento, métricas y umbrales. Necesitas un 80 % para superar el capítulo."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt=(
                    "¿Qué distingue al finetuning de clasificación del finetuning de "
                    "instrucciones?"
                ),
                options=(
                    "El de clasificación solo puede predecir las clases vistas y suele "
                    "necesitar menos datos.",
                    "El de clasificación no modifica los pesos del modelo.",
                    "El de instrucciones exige cambiar el tokenizador.",
                    "El de instrucciones solo sirve para tareas binarias.",
                ),
                correct=0,
                explanation=(
                    "El clasificador sustituye la salida por una capa con las etiquetas del "
                    "problema y se limita a esas clases. El finetuning de instrucciones es más "
                    "flexible, pero requiere más datos y cómputo. Ambos modifican pesos."
                ),
            ),
            Question(
                id="q2",
                prompt=(
                    "Duplicas mensajes y los repartes al azar entre entrenamiento y prueba. "
                    "¿Qué problema introduces?"
                ),
                options=(
                    "El test se queda demasiado pequeño.",
                    "Fuga de datos: el test contiene ejemplos vistos en entrenamiento.",
                    "El tokenizador cambia de tamaño.",
                    "El modelo pierde la cabeza de clasificación.",
                ),
                correct=1,
                explanation=(
                    "Si un mensaje o una variante casi idéntica aparece en ambos splits, el "
                    "modelo puede memorizarlo y la evaluación deja de medir generalización. "
                    "Hay que eliminar duplicados antes de dividir."
                ),
            ),
            Question(
                id="q3",
                prompt=(
                    "¿Por qué se usa el último token para clasificar una secuencia con GPT?"
                ),
                options=(
                    "Porque es el token más corto de la secuencia.",
                    "Porque recibe una tasa de aprendizaje mayor.",
                    "Porque la atención causal le permite ver todos los tokens anteriores.",
                    "Porque evita tener que aplicar softmax.",
                ),
                correct=2,
                explanation=(
                    "Con máscara causal, cada token solo atiende a los anteriores. El último "
                    "es el único que ha podido acumular información de toda la secuencia, así "
                    "que su representación resume mejor el mensaje."
                ),
            ),
            Question(
                id="q4",
                prompt=(
                    "El modelo asigna una probabilidad de 0,1 a la clase correcta. ¿Cuál es "
                    "aproximadamente la entropía cruzada?"
                ),
                options=("0,105", "0,693", "2,303", "10,0"),
                correct=2,
                explanation=(
                    "La entropía cruzada binaria es -ln(p). Para p = 0,1, -ln(0,1) ≈ 2,303. "
                    "El valor 0,105 corresponde a p = 0,9 y 0,693 a p = 0,5."
                ),
            ),
            Question(
                id="q5",
                prompt=(
                    "Un conjunto tiene 95 mensajes ham y 5 spam. Un modelo que siempre predice "
                    "ham obtiene un 95 % de accuracy. ¿Qué conclusiones son correctas?"
                ),
                options=(
                    "El modelo ha aprendido a detectar spam.",
                    "La accuracy oculta que el recall de spam es cero.",
                    "El umbral está demasiado bajo.",
                    "La entropía cruzada será negativa.",
                ),
                correct=1,
                explanation=(
                    "El modelo acierta la clase mayoritaria y falla todos los positivos. La "
                    "accuracy global no revela ese fallo; hay que mirar la matriz de confusión "
                    "y el recall de la clase spam."
                ),
            ),
            Question(
                id="q6",
                prompt=(
                    "¿Por qué el finetuning usa una tasa de aprendizaje baja y congela la "
                    "mayor parte del modelo?"
                ),
                options=(
                    "Para aumentar el vocabulario durante el entrenamiento.",
                    "Para preservar el conocimiento previo y reducir el riesgo de olvido.",
                    "Para evitar tener que calcular la pérdida.",
                    "Para que el test sea más grande que el entrenamiento.",
                ),
                correct=1,
                explanation=(
                    "Los pesos preentrenados ya contienen lenguaje útil. Moverlos poco y "
                    "ajustar solo las últimas capas reduce el coste y limita el olvido "
                    "catastrófico, sin impedir que la cabeza aprenda la tarea."
                ),
            ),
            Question(
                id="q7",
                prompt=(
                    "Con TP=40, FP=10, FN=20 y TN=130, ¿cuál es el recall de la clase spam?"
                ),
                options=("0,80", "0,667", "0,85", "0,727"),
                correct=1,
                explanation=(
                    "Recall = TP / (TP + FN) = 40 / (40 + 20) = 0,667. El 0,80 es la "
                    "precisión, 0,85 la accuracy y 0,727 el F1."
                ),
            ),
            Question(
                id="q8",
                prompt="¿Qué mide la precisión en un clasificador binario?",
                options=(
                    "De todos los positivos reales, cuántos se detectaron.",
                    "De todas las predicciones positivas, cuántas eran realmente positivas.",
                    "El porcentaje total de predicciones correctas.",
                    "La media armónica de accuracy y recall.",
                ),
                correct=1,
                explanation=(
                    "Precisión = TP / (TP + FP). Responde a cuánto de lo que el modelo marcó "
                    "como spam era spam de verdad. El recall mira los positivos reales y la "
                    "accuracy mezcla todas las casillas."
                ),
            ),
            Question(
                id="q9",
                prompt=(
                    "Si bajas el umbral de decisión de 0,5 a 0,3, ¿qué efecto es más probable?"
                ),
                options=(
                    "Sube el recall y suele bajar la precisión.",
                    "Suben el recall y la precisión a la vez.",
                    "Bajan el recall y la precisión.",
                    "No cambia ninguna métrica porque el modelo es el mismo.",
                ),
                correct=0,
                explanation=(
                    "Un umbral más bajo marca más mensajes como spam: se detectan más "
                    "positivos reales (sube el recall), pero también entran más falsos "
                    "positivos (suele bajar la precisión). Es un intercambio, no una mejora "
                    "gratuita."
                ),
            ),
            Question(
                id="q10",
                prompt=(
                    "¿Cuál es el orden correcto del flujo de trabajo de clasificación del "
                    "capítulo?"
                ),
                options=(
                    "Sustituir la cabeza → preparar datos → elegir umbral → cargar pesos.",
                    "Preparar y dividir datos → cargar el modelo preentrenado → sustituir la "
                    "cabeza → entrenar → evaluar y elegir el umbral en validación.",
                    "Entrenar desde cero → tokenizar → dividir → aplicar softmax.",
                    "Elegir el umbral en test → entrenar → dividir los datos → guardar.",
                ),
                correct=1,
                explanation=(
                    "Primero se preparan y separan los datos; después se reutiliza el modelo "
                    "preentrenado, se cambia la salida por la cabeza de clases y se ajustan "
                    "las capas elegidas. La evaluación y el umbral se deciden con validación, "
                    "y el test se reserva para el final."
                ),
            ),
        ),
    )
}

# Alias compatible con el registro global del curso.
QUIZZES = QUIZZES_ES
