"""Autoevaluación del capítulo 4 (español)."""

from webapp.content.schema import Question, Quiz

QUIZZES_ES: dict[str, Quiz] = {
    "quiz-capitulo-4": Quiz(
        id="quiz-capitulo-4",
        title="Autoevaluación · Capítulo 4",
        description=(
            "Diez preguntas sobre la configuración de GPT-2 small, LayerNorm, GELU, "
            "la red feed-forward, el bloque transformer, las conexiones residuales y "
            "la cabeza de salida. Necesitas un 80 % para superar el capítulo."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt="En GPT_CONFIG_124M, ¿qué controla context_length = 1024?",
                options=(
                    "El número de capas transformer.",
                    "El máximo de tokens que el modelo puede procesar a la vez.",
                    "El tamaño del vocabulario.",
                    "La dimensión de cada cabeza de atención.",
                ),
                correct=1,
                explanation=(
                    "context_length fija la ventana de contexto: 1 024 posiciones. "
                    "n_layers controla las capas, vocab_size el vocabulario y emb_dim la "
                    "dimensión de los vectores. La dimensión por cabeza sale de dividir "
                    "emb_dim entre n_heads."
                ),
            ),
            Question(
                id="q2",
                prompt=(
                    "¿Cuántos parámetros tiene la tabla de embeddings de tokens de GPT-2 "
                    "small (50 257 × 768)?"
                ),
                options=(
                    "786 432",
                    "4 722 432",
                    "38 597 376",
                    "124 412 160",
                ),
                correct=2,
                explanation=(
                    "50 257 × 768 = 38 597 376. Es la tabla más grande del modelo si no "
                    "contamos la cabeza de salida, que tiene exactamente la misma forma. "
                    "786 432 corresponde a los embeddings posicionales (1 024 × 768)."
                ),
            ),
            Question(
                id="q3",
                prompt="¿A lo largo de qué dimensión normaliza LayerNorm cada token?",
                options=(
                    "La dimensión de embedding, con media 0 y varianza 1.",
                    "La dimensión del lote.",
                    "La dimensión temporal entre tokens.",
                    "El vocabulario completo.",
                ),
                correct=0,
                explanation=(
                    "LayerNorm calcula media y varianza sobre las 768 componentes de cada "
                    "token y normaliza dentro de ese vector. BatchNorm, en cambio, "
                    "normaliza a través del lote para cada característica."
                ),
            ),
            Question(
                id="q4",
                prompt="¿Dónde coloca LayerNorm un bloque Pre-LN?",
                options=(
                    "Solo después de la cabeza de salida.",
                    "Después de la atención y de la FFN.",
                    "Únicamente en el embedding posicional.",
                    "Antes de la atención y antes de la FFN.",
                ),
                correct=3,
                explanation=(
                    "En Pre-LN la normalización va antes de cada subcapa, y después se "
                    "suma la conexión residual. El transformer original usaba Post-LN, "
                    "con la normalización después de las subcapas."
                ),
            ),
            Question(
                id="q5",
                prompt="¿Qué rasgo distingue a GELU de ReLU?",
                options=(
                    "Elimina todos los valores negativos.",
                    "Es suave y conserva una salida pequeña para entradas negativas.",
                    "No necesita ningún parámetro ni cálculo.",
                    "Solo funciona con lotes de tamaño 1.",
                ),
                correct=1,
                explanation=(
                    "ReLU tiene un codo en cero y anula todo lo negativo. GELU es una "
                    "curva suave que se aproxima a ReLU, pero deja un valor pequeño no "
                    "nulo —y un gradiente— en la zona negativa."
                ),
            ),
            Question(
                id="q6",
                prompt=(
                    "La FFN de GPT-2 small expande 768 → 3072 → 768. ¿Cuántos parámetros "
                    "aproximados tiene, contando pesos y sesgos?"
                ),
                options=(
                    "2,36 M",
                    "38,6 M",
                    "4,72 M",
                    "7,09 M",
                ),
                correct=2,
                explanation=(
                    "La primera proyección aporta 768 × 3 072 pesos y 3 072 sesgos; la "
                    "segunda, 3 072 × 768 pesos y 768 sesgos. El total es 4 722 432, "
                    "aproximadamente 4,72 M. Los 7,09 M incluyen también la atención y "
                    "las dos LayerNorm del bloque."
                ),
            ),
            Question(
                id="q7",
                prompt="¿Cuál es el orden correcto dentro de un bloque transformer Pre-LN?",
                options=(
                    "LN → atención → residual → LN → FFN → residual",
                    "atención → LN → FFN → residual → LN",
                    "LN → FFN → atención → residual",
                    "residual → LN → atención → FFN",
                ),
                correct=0,
                explanation=(
                    "Primero se normaliza la entrada, se aplica atención multi-head y se "
                    "suma el residual. Después se normaliza otra vez, se aplica la red "
                    "feed-forward y se suma un segundo residual. La forma se conserva."
                ),
            ),
            Question(
                id="q8",
                prompt="¿Qué problema ayuda a mitigar una conexión residual?",
                options=(
                    "El tamaño excesivo del vocabulario.",
                    "La falta de tokenizador.",
                    "El exceso de softmax.",
                    "La desaparición del gradiente en redes profundas.",
                ),
                correct=3,
                explanation=(
                    "La suma x + f(x) crea un camino de identidad por el que el gradiente "
                    "puede retroceder sin multiplicarse por todas las derivadas "
                    "intermedias. Eso hace viable apilar muchos bloques."
                ),
            ),
            Question(
                id="q9",
                prompt="¿Qué produce la cabeza de salida para cada posición de la secuencia?",
                options=(
                    "Directamente el token elegido.",
                    "Un vector de logits de tamaño 50 257, antes del softmax.",
                    "Una probabilidad que ya suma 1 sin softmax.",
                    "Un embedding de 768 dimensiones.",
                ),
                correct=1,
                explanation=(
                    "La capa lineal final proyecta cada vector de 768 dimensiones al "
                    "vocabulario y devuelve 50 257 logits sin normalizar. El softmax "
                    "los convierte después en una distribución de probabilidad."
                ),
            ),
            Question(
                id="q10",
                prompt=(
                    "Ya has definido GPTModel e inicializado sus pesos al azar. ¿Qué falta "
                    "para que genere texto coherente?"
                ),
                options=(
                    "Añadir más capas sin entrenar.",
                    "Quitar la cabeza de salida.",
                    "Entrenarlo con datos; la arquitectura sola no aprende.",
                    "Cambiar el tokenizador por otro.",
                ),
                correct=2,
                explanation=(
                    "La arquitectura define la forma del cálculo, pero los pesos aleatorios "
                    "no contienen conocimiento del lenguaje. El libro muestra que el modelo "
                    "sin entrenar produce texto incoherente; el pretraining es el capítulo "
                    "siguiente."
                ),
            ),
        ),
    )
}
