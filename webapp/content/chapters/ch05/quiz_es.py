"""Quiz del capítulo 5 (ES)."""

from webapp.content.schema import Question, Quiz

QUIZZES_ES: dict[str, Quiz] = {
    "quiz-capitulo-5": Quiz(
        id="quiz-capitulo-5",
        title="Autoevaluación · Capítulo 5",
        description=(
            "Diez preguntas sobre pérdida, entrenamiento, datos, evaluación y coste. "
            "Necesitas un 80 % para superar la autoevaluación; puedes repetirla."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt="¿Qué mide la pérdida de entrenamiento de un GPT?",
                options=(
                    "El porcentaje de palabras generadas sin errores ortográficos.",
                    "La probabilidad asignada al token correcto, transformada con −log y promediada.",
                    "El número de parámetros que cambian en cada paso.",
                    "El tiempo que tarda una época en completarse.",
                ),
                correct=1,
                explanation=(
                    "La pérdida compara la distribución del modelo con el token que "
                    "realmente sigue en el texto. Se toma la probabilidad del token correcto, "
                    "se aplica −log y se promedian las posiciones del lote. Cuanto más alta "
                    "es esa probabilidad, menor es la pérdida."
                ),
            ),
            Question(
                id="q2",
                prompt=(
                    "Si el modelo asigna una probabilidad de 0,25 al token correcto, "
                    "¿cuál es la pérdida de ese token?"
                ),
                options=("0,25", "0,75", "1,386", "4,000"),
                correct=2,
                explanation=(
                    "La pérdida es −ln(0,25). Como ln(0,25) ≈ −1,386, el resultado es "
                    "≈ 1,386. Una probabilidad de 1 daría 0; una de 0,5, ≈ 0,693."
                ),
            ),
            Question(
                id="q3",
                prompt=(
                    "Un lote tiene dos tokens con pérdidas 0,5 y 1,5. ¿Cuál es la "
                    "perplejidad del lote?"
                ),
                options=("1,00", "1,65", "2,72", "4,48"),
                correct=2,
                explanation=(
                    "La pérdida media es (0,5 + 1,5) / 2 = 1,0. La perplejidad es "
                    "exp(1,0) ≈ 2,72. Se interpreta como el número efectivo de candidatos "
                    "entre los que el modelo duda."
                ),
            ),
            Question(
                id="q4",
                prompt="¿Cuál es el orden correcto de un paso de entrenamiento en PyTorch?",
                options=(
                    "backward → zero_grad → forward → step.",
                    "zero_grad → forward y pérdida → backward → step.",
                    "step → forward → backward → zero_grad.",
                    "forward → step → zero_grad → backward.",
                ),
                correct=1,
                explanation=(
                    "Primero se vacían los gradientes del paso anterior, después se calcula "
                    "la salida y la pérdida, se retropropaga para obtener gradientes y, por "
                    "último, el optimizador actualiza los pesos."
                ),
            ),
            Question(
                id="q5",
                prompt="¿Qué rasgo distingue a AdamW de Adam clásico?",
                options=(
                    "AdamW no usa momentos de primer y segundo orden.",
                    "AdamW aplica el decaimiento de pesos de forma desacoplada del gradiente.",
                    "AdamW solo funciona con modelos de menos de 1 000 millones de parámetros.",
                    "AdamW elimina la necesidad de una tasa de aprendizaje.",
                ),
                correct=1,
                explanation=(
                    "AdamW separa el decaimiento de pesos de la actualización adaptativa. "
                    "Eso evita que la regularización se mezcle con los momentos y suele "
                    "generalizar mejor. Sigue usando una tasa de aprendizaje."
                ),
            ),
            Question(
                id="q6",
                prompt=(
                    "En el data loader de entrenamiento del libro se usa drop_last=True. "
                    "¿Para qué?"
                ),
                options=(
                    "Para mezclar los ejemplos en cada época.",
                    "Para descartar el último lote si está incompleto y mantener formas estables.",
                    "Para usar el conjunto de validación como entrenamiento.",
                    "Para duplicar el último lote y equilibrar las clases.",
                ),
                correct=1,
                explanation=(
                    "Con drop_last=True, el cargador omite el lote final cuando no tiene el "
                    "tamaño completo. Así todos los lotes de entrenamiento comparten forma y "
                    "se evitan actualizaciones con muy pocos ejemplos. En validación se usa "
                    "False para no perder datos."
                ),
            ),
            Question(
                id="q7",
                prompt=(
                    "La pérdida de entrenamiento sigue bajando, pero la de validación se "
                    "estanca o sube. ¿Qué indica?"
                ),
                options=(
                    "Que el modelo ha dejado de aprender el idioma por completo.",
                    "Que el optimizador tiene una tasa de aprendizaje demasiado baja.",
                    "Que el modelo se está sobreajustando al conjunto de entrenamiento.",
                    "Que el tokenizador tiene un vocabulario demasiado grande.",
                ),
                correct=2,
                explanation=(
                    "Es el patrón clásico de sobreajuste: el modelo mejora en los datos que "
                    "ve, pero no generaliza a texto no visto. En el libro ocurre porque el "
                    "corpus es muy pequeño y se entrenan varias épocas; con más datos suele "
                    "bastar una sola pasada."
                ),
            ),
            Question(
                id="q8",
                prompt=(
                    "¿Qué configuración produce una generación más determinista, parecida "
                    "a elegir siempre el token más probable?"
                ),
                options=(
                    "Temperatura alta y top-k grande.",
                    "Temperatura 0 o selección con argmax.",
                    "Temperatura 1,5 y top-k 50.",
                    "Aumentar el número de épocas en inferencia.",
                ),
                correct=1,
                explanation=(
                    "Con temperatura 0 se desactiva el muestreo y se elige el argmax; también "
                    "puede hacerse directamente con argmax. Una temperatura alta aplana la "
                    "distribución y aumenta la variedad, no el determinismo."
                ),
            ),
            Question(
                id="q9",
                prompt=(
                    "Con la regla FLOPs ≈ 6 · N · D, ¿cuántos FLOPs requiere entrenar un "
                    "modelo de 124 M de parámetros con 1 000 M de tokens?"
                ),
                options=("7,44 × 10¹⁵", "7,44 × 10¹⁷", "7,44 × 10²⁰", "1,24 × 10¹⁷"),
                correct=1,
                explanation=(
                    "6 × 124 × 10⁶ × 1 × 10⁹ = 7,44 × 10¹⁷ FLOPs. Es una estimación de "
                    "orden de magnitud: no incluye ineficiencias, comunicación entre GPUs ni "
                    "el coste de la inferencia."
                ),
            ),
            Question(
                id="q10",
                prompt="¿Qué secuencia resume mejor el capítulo 5?",
                options=(
                    "Cargar GPT-2 → hacer finetuning → medir la pérdida → clasificar.",
                    "Tokenizar → construir atención → entrenar → borrar los pesos.",
                    "Medir la pérdida → entrenar → evaluar y muestrear → guardar o cargar pesos.",
                    "Cuantizar → destilar → alinear con RLHF → desplegar.",
                ),
                correct=2,
                explanation=(
                    "El capítulo recorre la evaluación numérica, el bucle de entrenamiento, "
                    "las estrategias de decodificación y el guardado o carga de pesos. La "
                    "carga de GPT-2 permite partir de un modelo ya entrenado. La alineación "
                    "con RLHF y la cuantización pertenecen a otras etapas."
                ),
            ),
        ),
    )
}
