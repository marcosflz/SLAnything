"""Quiz del capítulo 3 (ES)."""

from webapp.content.schema import Question, Quiz

QUIZZES: dict[str, Quiz] = {
    "quiz-capitulo-3": Quiz(
        id="quiz-capitulo-3",
        title="Autoevaluación · Capítulo 3",
        description=(
            "Diez preguntas sobre atención, Q/K/V, escalado, máscara causal, multi-head y "
            "coste. Necesitas un 80 % para considerar el capítulo superado; puedes repetirlo "
            "tantas veces como quieras."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt=(
                    "¿Qué limitación de los encoder-decoder recurrentes motivó la aparición de "
                    "los mecanismos de atención?"
                ),
                options=(
                    "Que solo podían traducir entre dos idiomas.",
                    "Que el decoder dependía de un único estado oculto con toda la entrada comprimida.",
                    "Que no usaban representaciones vectoriales.",
                    "Que no se podían entrenar con retropropagación.",
                ),
                correct=1,
                explanation=(
                    "El encoder comprimía toda la frase en un estado oculto de tamaño fijo y el "
                    "decoder solo veía ese resumen. La atención permitió consultar directamente "
                    "las posiciones de la entrada y repartir el peso entre ellas."
                ),
            ),
            Question(
                id="q2",
                prompt=(
                    "En la self-attention simplificada, ¿cuál es el orden correcto de las "
                    "operaciones?"
                ),
                options=(
                    "Softmax, producto escalar y suma ponderada.",
                    "Producto escalar, softmax y suma ponderada de los vectores de entrada.",
                    "Suma ponderada, producto escalar y softmax.",
                    "Producto escalar, suma ponderada y softmax.",
                ),
                correct=1,
                explanation=(
                    "Primero se calculan las puntuaciones con productos escalares, después se "
                    "normalizan por filas con softmax y finalmente se mezclan los vectores de "
                    "entrada con esos pesos."
                ),
            ),
            Question(
                id="q3",
                prompt="¿Qué representa la clave (key) de un token en la atención?",
                options=(
                    "Lo que ese token busca en los demás.",
                    "El contenido que aporta cuando se le presta atención.",
                    "Lo que ese token ofrece para que otras consultas lo comparen.",
                    "Su posición absoluta en la secuencia.",
                ),
                correct=2,
                explanation=(
                    "La consulta expresa qué busca el token actual; la clave, qué ofrece cada "
                    "candidato; el valor, qué contenido se mezcla. Las tres salen de "
                    "proyecciones distintas del mismo embedding."
                ),
            ),
            Question(
                id="q4",
                prompt=(
                    "Una puntuación de atención sin escalar vale 16 y la dimensión de las claves "
                    "es d_k = 64. ¿Cuál es la puntuación escalada?"
                ),
                options=("0,25", "2", "4", "8"),
                correct=1,
                explanation=(
                    "Se divide por √d_k = √64 = 8. Por tanto, 16 / 8 = 2. Dividir por d_k daría "
                    "0,25, que sería un escalado demasiado agresivo."
                ),
            ),
            Question(
                id="q5",
                prompt=(
                    "En atención causal, ¿por qué se sustituyen las posiciones futuras por −∞ "
                    "antes de softmax en lugar de poner un cero?"
                ),
                options=(
                    "Porque exp(−∞) es cero, mientras que exp(0) = 1 y seguiría contribuyendo.",
                    "Porque un cero haría que la matriz no fuera triangular.",
                    "Porque −∞ elimina el token del tensor y ahorra memoria.",
                    "Porque softmax no acepta valores positivos.",
                ),
                correct=0,
                explanation=(
                    "Softmax exponencia cada puntuación. Un cero se convertiría en 1 y daría peso "
                    "a la posición futura; −∞ se convierte en 0 y la elimina por completo. "
                    "Después, la fila se normaliza solo con las posiciones permitidas."
                ),
            ),
            Question(
                id="q6",
                prompt=(
                    "En una matriz de atención causal para 4 tokens, ¿cuántos pesos no nulos hay "
                    "en total?"
                ),
                options=("4", "6", "10", "16"),
                correct=2,
                explanation=(
                    "La máscara deja visibles la diagonal y la parte inferior. La fila 1 tiene 1 "
                    "peso, la 2 tiene 2, la 3 tiene 3 y la 4 tiene 4: 1 + 2 + 3 + 4 = 10. Los "
                    "otros 6 pesos son cero."
                ),
            ),
            Question(
                id="q7",
                prompt=(
                    "Un modelo tiene d_modelo = 768 y 12 cabezas de atención. ¿Cuántas "
                    "dimensiones tiene cada cabeza?"
                ),
                options=("32", "48", "64", "96"),
                correct=2,
                explanation=(
                    "La dimensión por cabeza es d_modelo / h = 768 / 12 = 64. GPT-2 pequeño usa "
                    "exactamente ese reparto: 12 cabezas de 64 dimensiones."
                ),
            ),
            Question(
                id="q8",
                prompt=(
                    "¿Qué papel cumple la proyección de salida W_O después de concatenar las "
                    "cabezas de multi-head attention?"
                ),
                options=(
                    "Aplica la máscara causal a cada cabeza.",
                    "Combina la información de las cabezas en un vector de d_modelo.",
                    "Normaliza los pesos para que sumen uno.",
                    "Reduce el vocabulario al número de tokens.",
                ),
                correct=1,
                explanation=(
                    "Las cabezas producen tramos distintos que se concatenan. W_O mezcla esos "
                    "tramos y devuelve una representación del tamaño del modelo. La máscara y "
                    "softmax ya se aplicaron dentro de cada cabeza."
                ),
            ),
            Question(
                id="q9",
                prompt=(
                    "Una capa con 12 cabezas procesa 1024 tokens. ¿Cuántas puntuaciones de "
                    "atención genera, aproximadamente?"
                ),
                options=("12 288", "1,05 millones", "12,6 millones", "150 millones"),
                correct=2,
                explanation=(
                    "Cada cabeza construye una matriz de 1024 × 1024 = 1 048 576 puntuaciones. "
                    "Multiplicando por 12 cabezas: 12 582 912, es decir, unos 12,6 millones por "
                    "capa."
                ),
            ),
            Question(
                id="q10",
                prompt=(
                    "¿Cuál es el orden correcto de los pasos en una atención causal con pesos "
                    "entrenables?"
                ),
                options=(
                    "Proyectar Q, K y V; calcular QKᵀ; escalar; enmascarar; softmax; multiplicar "
                    "por V.",
                    "Proyectar Q, K y V; softmax; calcular QKᵀ; enmascarar; multiplicar por V.",
                    "Calcular QKᵀ; proyectar Q, K y V; enmascarar; softmax; multiplicar por V.",
                    "Enmascarar; proyectar Q, K y V; softmax; calcular QKᵀ; multiplicar por V.",
                ),
                correct=0,
                explanation=(
                    "Primero se proyectan las consultas, claves y valores. Después se puntúa con "
                    "QKᵀ, se escala por √d_k, se enmascara el futuro con −∞, se aplica softmax y "
                    "se mezclan los valores. Alterar ese orden cambia el resultado."
                ),
            ),
        ),
    )
}
