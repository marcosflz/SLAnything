"""Preguntas del capítulo 1.

Contrato: cada `Question.correct` es el índice de la opción correcta. El quiz se
corrige en servidor; el HTML nunca revela la respuesta antes de enviar.
"""

from webapp.content.schema import Question, Quiz

QUIZZES: dict[str, Quiz] = {
    "quiz-capitulo-1": Quiz(
        id="quiz-capitulo-1",
        title="Autoevaluación · Capítulo 1",
        description=(
            "Diez preguntas sobre los conceptos centrales. Necesitas un 80 % para "
            "considerar el capítulo superado; puedes repetirlo tantas veces como quieras."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt="¿Qué dos cosas miden el “large” de un large language model?",
                options=(
                    "Solo el número de parámetros.",
                    "El número de parámetros y el tamaño y la diversidad del corpus.",
                    "La longitud máxima del prompt.",
                    "El número de usuarios simultáneos.",
                ),
                correct=1,
                explanation=(
                    "“Grande” se refiere tanto a los parámetros —los pesos ajustables de la "
                    "red— como a la cantidad y diversidad de los datos de entrenamiento. "
                    "Ninguna de las dos dimensiones basta por separado."
                ),
            ),
            Question(
                id="q2",
                prompt="¿Cuál es la tarea central del pretraining de GPT?",
                options=(
                    "Clasificar correos como spam.",
                    "Traducir sin ejemplos.",
                    "Predecir el siguiente token.",
                    "Resumir documentos largos.",
                ),
                correct=2,
                explanation=(
                    "GPT se entrena para predecir el siguiente token en un corpus enorme. "
                    "Traducir, resumir o clasificar son capacidades que se aprovechan después, "
                    "no la tarea de pretraining."
                ),
            ),
            Question(
                id="q3",
                prompt="¿Por qué el pretraining es autosupervisado?",
                options=(
                    "Porque un humano etiqueta cada frase.",
                    "Porque usa refuerzo con recompensas.",
                    "Porque no necesita datos.",
                    "Porque la etiqueta es el propio texto: el siguiente token.",
                ),
                correct=3,
                explanation=(
                    "El texto proporciona entrada y objetivo a la vez. Si la frase es «El gato "
                    "duerme sobre el sofá», la entrada puede ser «El gato duerme sobre el» y la "
                    "etiqueta, «sofá». No hace falta anotación humana."
                ),
            ),
            Question(
                id="q4",
                prompt="¿Qué parte del transformer original usa GPT?",
                options=(
                    "El encoder.",
                    "El decoder.",
                    "Encoder y decoder.",
                    "Ninguna; GPT no usa transformer.",
                ),
                correct=1,
                explanation=(
                    "GPT es un modelo decoder-only: procesa de izquierda a derecha y genera "
                    "texto de forma autorregresiva. BERT, en cambio, se basa en el encoder."
                ),
            ),
            Question(
                id="q5",
                prompt="¿Para qué está especialmente diseñado BERT?",
                options=(
                    "Para generar texto de izquierda a derecha.",
                    "Para traducir sin datos.",
                    "Para predecir palabras enmascaradas y clasificar.",
                    "Para entrenar con RLHF.",
                ),
                correct=2,
                explanation=(
                    "BERT usa el encoder y se entrena rellenando palabras ocultas, mirando el "
                    "contexto en ambas direcciones. Por eso destaca en clasificación y "
                    "extracción de información más que en generación abierta."
                ),
            ),
            Question(
                id="q6",
                prompt="¿Qué permite el mecanismo de self-attention?",
                options=(
                    "Mirar solo la palabra anterior.",
                    "Ponderar la relevancia de otros tokens del contexto.",
                    "Reducir el vocabulario.",
                    "Evitar el entrenamiento.",
                ),
                correct=1,
                explanation=(
                    "Cada token calcula pesos sobre los demás para construir una representación "
                    "contextual. Eso permite conectar palabras distantes, como «gato» y "
                    "«cansado» en una frase larga."
                ),
            ),
            Question(
                id="q7",
                prompt="¿Qué es un prompt few-shot?",
                options=(
                    "Entrenar el modelo con pocos datos.",
                    "Usar un modelo con pocos parámetros.",
                    "Generar muy pocas palabras.",
                    "Incluir unos pocos ejemplos resueltos en el prompt.",
                ),
                correct=3,
                explanation=(
                    "Few-shot significa dar ejemplos dentro del contexto, no reentrenar. Los "
                    "pesos no cambian: el modelo aprende en contexto y el efecto dura lo que "
                    "dura la conversación."
                ),
            ),
            Question(
                id="q8",
                prompt="¿Qué cambia el finetuning a diferencia de few-shot?",
                options=(
                    "El prompt.",
                    "Los pesos del modelo.",
                    "El tokenizador.",
                    "El hardware.",
                ),
                correct=1,
                explanation=(
                    "El finetuning actualiza los pesos con datos etiquetados y el cambio "
                    "persiste. Few-shot solo condiciona la generación con ejemplos en el "
                    "contexto."
                ),
            ),
            Question(
                id="q9",
                prompt="¿Qué significa que GPT sea autorregresivo?",
                options=(
                    "Que usa su salida anterior como entrada del siguiente paso.",
                    "Que se entrena sin etiquetas.",
                    "Que genera todos los tokens en paralelo.",
                    "Que no necesita contexto.",
                ),
                correct=0,
                explanation=(
                    "Genera un token, lo añade a la secuencia y vuelve a predecir. Ese bucle "
                    "—predecir, añadir y repetir— es la generación autorregresiva."
                ),
            ),
            Question(
                id="q10",
                prompt=(
                    "¿Por qué GPT puede traducir aunque no se entrenó específicamente para "
                    "ello?"
                ),
                options=(
                    "Porque incluye un módulo de traducción.",
                    "Porque el prompt cambia los pesos.",
                    "Porque usa el encoder de BERT.",
                    "Por comportamiento emergente a partir de la escala y los datos multilingües.",
                ),
                correct=3,
                explanation=(
                    "La traducción emerge como una capacidad no entrenada explícitamente "
                    "cuando el modelo es grande y ha visto suficientes textos en varios "
                    "idiomas. Es un ejemplo de comportamiento emergente, no de magia."
                ),
            ),
        ),
    )
}
