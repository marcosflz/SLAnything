"""Autoevaluación del capítulo 2 (ES)."""

from webapp.content.schema import Question, Quiz

QUIZZES: dict[str, Quiz] = {
    "quiz-capitulo-2": Quiz(
        id="quiz-capitulo-2",
        title="Autoevaluación · Capítulo 2",
        description=(
            "Diez preguntas sobre tokens, BPE, ventanas, pares y embeddings. Necesitas un 80 % "
            "para considerar el capítulo superado; puedes repetirlo sin penalización."
        ),
        pass_score=80,
        questions=(
            Question(
                id="q1",
                prompt="¿Cuál es la diferencia entre un token y un token ID?",
                options=(
                    "El token es la pieza de texto; el ID es su clave numérica en el vocabulario.",
                    "El token es un número y el ID es una palabra.",
                    "Son sinónimos: ambos designan la misma cadena.",
                    "El ID es el vector denso y el token es su posición.",
                ),
                correct=0,
                explanation=(
                    "El token es la unidad de texto que produce el tokenizador. El ID es el "
                    "entero con el que el vocabulario representa esa unidad. El vector llega "
                    "después, con la capa de embeddings."
                ),
            ),
            Question(
                id="q2",
                prompt="¿Qué ventaja principal ofrece la tokenización por subpalabras frente a la tokenización por palabras?",
                options=(
                    "Elimina por completo la necesidad de vocabulario.",
                    "Representa palabras nuevas combinando fragmentos conocidos.",
                    "Garantiza que cada token tenga un significado único.",
                    "Reduce el texto a un solo carácter por palabra.",
                ),
                correct=1,
                explanation=(
                    "Un vocabulario de subpalabras puede descomponer términos no vistos en piezas "
                    "que sí conoce. Por eso BPE casi elimina el problema OOV sin necesidad de un "
                    "token <|unk|> en cada palabra nueva."
                ),
            ),
            Question(
                id="q3",
                prompt="¿Para qué se añade el token <|unk|> a un vocabulario cerrado?",
                options=(
                    "Para marcar el final de cada documento.",
                    "Para rellenar lotes de distinta longitud.",
                    "Para representar piezas que no estaban en el corpus de entrenamiento.",
                    "Para aumentar la dimensión de los embeddings.",
                ),
                correct=2,
                explanation=(
                    "Sin <|unk|>, una palabra desconocida provoca un error de consulta en el "
                    "vocabulario. El token desconocido ofrece una representación de emergencia, "
                    "aunque la palabra original ya no se pueda recuperar al decodificar."
                ),
            ),
            Question(
                id="q4",
                prompt="¿Qué función cumple <|endoftext|> en el tokenizador de GPT-2?",
                options=(
                    "Indica que el modelo debe traducir la frase.",
                    "Separa documentos y ocupa el ID 50 256 de un vocabulario de 50 257 tokens.",
                    "Sustituye a todas las palabras poco frecuentes.",
                    "Añade información de posición a cada token.",
                ),
                correct=1,
                explanation=(
                    "GPT-2 usa un único token especial para delimitar el final de un texto o "
                    "separar fuentes. Su vocabulario BPE tiene 50 257 entradas y <|endoftext|> es "
                    "la última, con ID 50 256."
                ),
            ),
            Question(
                id="q5",
                prompt="En BPE, ¿qué se hace en cada iteración del entrenamiento?",
                options=(
                    "Se elimina el token menos frecuente del corpus.",
                    "Se fusiona el par de símbolos adyacentes más frecuente.",
                    "Se asigna un vector aleatorio a cada palabra.",
                    "Se divide cada palabra en sus letras y se detiene el proceso.",
                ),
                correct=1,
                explanation=(
                    "BPE cuenta los pares adyacentes ponderados por la frecuencia de cada palabra "
                    "y fusiona el más frecuente. Cada fusión añade un token nuevo al vocabulario "
                    "y el proceso se repite."
                ),
            ),
            Question(
                id="q6",
                prompt="Un vocabulario tiene 10 000 tokens y la dimensión de embedding es 128. ¿Cuántos parámetros tiene la matriz de tokens?",
                options=(
                    "128 000",
                    "1 280 000",
                    "10 128",
                    "12 800 000",
                ),
                correct=1,
                explanation=(
                    "La matriz tiene una fila por token y una columna por dimensión: "
                    "10 000 × 128 = 1 280 000 parámetros. Los sesgos y los embeddings "
                    "posicionales, si existen, se cuentan aparte."
                ),
            ),
            Question(
                id="q7",
                prompt="Una secuencia tiene 1 000 tokens, el contexto es 100 y el stride es 50. ¿Cuántas ventanas con objetivo completo se obtienen?",
                options=(
                    "10",
                    "18",
                    "19",
                    "20",
                ),
                correct=1,
                explanation=(
                    "Aplicando floor((N − L − 1) / S) + 1: floor((1000 − 100 − 1) / 50) + 1 = "
                    "17 + 1 = 18 ventanas con objetivo completo. Cada una comparte 50 tokens con "
                    "la siguiente."
                ),
            ),
            Question(
                id="q8",
                prompt="Si la entrada de una ventana es x = [10, 20, 30, 40], ¿cuál es el objetivo y para predecir el siguiente token?",
                options=(
                    "[10, 20, 30, 40]",
                    "[20, 30, 40, 50]",
                    "[9, 19, 29, 39]",
                    "[40, 30, 20, 10]",
                ),
                correct=1,
                explanation=(
                    "El objetivo es la entrada desplazada una posición: y[i] = x[i + 1]. La última "
                    "posición debe predecir el token que sigue a 40 en la secuencia original, que "
                    "en el ejemplo se representa como 50."
                ),
            ),
            Question(
                id="q9",
                prompt="Dos embeddings tienen una similitud coseno de 0,95. ¿Qué significa exactamente?",
                options=(
                    "Que sus vectores apuntan en direcciones muy parecidas.",
                    "Que uno de los vectores es mucho más largo que el otro.",
                    "Que los tokens son sinónimos en todos los contextos.",
                    "Que la distancia euclídea entre ellos es de 0,95.",
                ),
                correct=0,
                explanation=(
                    "El coseno mide el ángulo entre vectores y normaliza por sus normas. Un valor "
                    "alto indica direcciones parecidas, no longitudes ni sinonimia garantizada."
                ),
            ),
            Question(
                id="q10",
                prompt="¿Cuál es el orden correcto del pipeline de preparación de texto del capítulo?",
                options=(
                    "Texto → IDs → tokens → ventanas → embeddings → pares.",
                    "Texto → tokens → IDs → ventanas → pares → embeddings.",
                    "Tokens → texto → embeddings → IDs → ventanas → pares.",
                    "Texto → embeddings → tokens → pares → IDs → ventanas.",
                ),
                correct=1,
                explanation=(
                    "Primero se tokeniza el texto, después se codifican los tokens como IDs, se "
                    "recortan ventanas, se construyen los pares x/y y finalmente se convierten "
                    "los IDs en vectores de embedding."
                ),
            ),
        ),
    ),
}
