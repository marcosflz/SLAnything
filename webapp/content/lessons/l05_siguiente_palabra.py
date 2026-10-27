"""Lección 5 · Predecir la siguiente palabra."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
)

LESSON = Lesson(
    number=5,
    slug="predecir-la-siguiente-palabra",
    title="Predecir la siguiente palabra",
    summary=(
        "GPT significa Generative Pretrained Transformer. Detrás de las siglas hay un "
        "bucle muy simple: predecir un token, añadirlo al contexto y repetir."
    ),
    minutes=15,
    objectives=(
        "Descomponer las siglas GPT y explicar qué aporta cada palabra.",
        "Describir la generación autorregresiva paso a paso.",
        "Usar un modelo de n-gramas como maqueta de la predicción del siguiente token.",
        "Relacionar temperatura y top-k con la variedad y la coherencia del texto generado.",
    ),
    blocks=(
        lead(
            "GPT son tres siglas y un bucle. <strong>G</strong>enerative, porque produce "
            "texto nuevo; <strong>P</strong>retrained, porque aprendió de un corpus enorme "
            "antes de que le pidieras nada; <strong>T</strong>ransformer, por la arquitectura "
            "que veremos en la lección 3. Lo que las une es una tarea diminuta: dado un "
            "contexto, predecir el siguiente token."
        ),
        p(
            "Ese bucle se llama <strong>generación autorregresiva</strong>. El modelo recibe "
            "un contexto inicial —una frase, una pregunta, un documento— y produce una "
            "distribución de probabilidad sobre todos los tokens de su vocabulario. Elige "
            "uno, lo añade al contexto y vuelve a empezar. No planifica el párrafo entero: "
            "toma una decisión local, la incorpora y recalcula. La coherencia global es el "
            "resultado de encadenar muchas decisiones locales. Si el contexto es «El cielo se "
            "tiñó de», el modelo no busca una regla en un diccionario: asigna más probabilidad "
            "a «naranja» o «rojo» que a «ventana», porque ha visto patrones parecidos. El "
            "contexto es su memoria de trabajo; todo lo que no cabe en él no existe para la "
            "predicción."
        ),
        figure(
            "img/ch01/fig_1_8_autoregressive.png",
            "Diagrama de un modelo autorregresivo: la salida de cada paso se convierte en parte de la entrada del siguiente.",
            "En cada iteración, el token generado se añade a la secuencia y el modelo vuelve "
            "a predecir. Ese circuito cerrado es la generación autorregresiva.",
            credit="Figura 1.8 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        p(
            "Para hacer tangible el mecanismo, la lección incluye una maqueta sin red "
            "neuronal: un <strong>modelo de n-gramas</strong>. Un unigrama mira solo la "
            "frecuencia de cada palabra; un bigrama condiciona la siguiente palabra a la "
            "anterior; un trigrama usa las dos anteriores. Nuestro modelo emplea hasta tres "
            "tokens de contexto —es decir, un 4-grama— y recurre a un <em>backoff</em>: si el "
            "contexto largo no aparece en el corpus, prueba con uno más corto y, en último "
            "término, con la frecuencia global. Ese retroceso es una forma primitiva de "
            "generalizar: cuando no hay evidencia suficiente para el contexto largo, se usa la "
            "que sí existe. El laboratorio lo entrena en el navegador con un fragmento de "
            "<em>El Quijote</em>, de dominio público, y permite cambiar el contexto, la "
            "longitud y la semilla para ver cómo cambia la generación."
        ),
        lab("ngram"),
        figure(
            "img/ch01/fig_1_7_next_word.png",
            "La frase se divide en tokens y el modelo predice cuál es el siguiente.",
            "La única tarea de pretraining: dividir el texto en tokens y aprender a rellenar "
            "el siguiente. No hay etiqueta humana; la etiqueta es el propio texto.",
            credit="Figura 1.7 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        h2("Temperatura y top-k"),
        p(
            "El modelo no elige siempre el token más probable. La <strong>temperatura</strong> "
            "modifica la forma de la distribución: por debajo de 1 la agudiza y favorece las "
            "opciones seguras; por encima de 1 la aplana y da espacio a candidatos menos "
            "probables. Una temperatura muy baja produce texto repetitivo y predecible; una "
            "muy alta, más variedad y también más incoherencias. El <strong>top-k</strong> "
            "recorta la cola: conserva solo los <em>k</em> candidatos más probables, "
            "renormaliza sus probabilidades y muestrea entre ellos. Así se evita que un token "
            "absurdo pero afortunado arruine la frase. Los dos controles se combinan: el top-k "
            "decide <em>entre qué</em> elegir y la temperatura decide <em>cuánto</em> arriesgar. "
            "En el límite, una temperatura de 0 equivale a elegir siempre el candidato más "
            "probable —generación voraz— y el top-k deja de importar."
        ),
        py(
            """
import collections
import random
import re

try:
    CORPUS = leer_recurso("quijote_fragmento.txt")
except NameError:
    CORPUS = '''En un lugar de la Mancha, de cuyo nombre no quiero acordarme, no ha mucho
tiempo que vivía un hidalgo de los de lanza en astillero. Tenía en su casa
una ama que pasaba de los cuarenta y una sobrina que no llegaba a los veinte.
Con estas razones perdía el pobre caballero el juicio, y desvelábase por
entenderlas. En resolución, él se enfrascó tanto en su lectura, que se le
pasaban las noches leyendo de claro en claro y los días de turbio en turbio.'''

TOKEN_RE = re.compile(r"\\w+|[^\\w\\s]", re.UNICODE)

def tokenizar(texto):
    return TOKEN_RE.findall(texto.lower())

TOKENS = tokenizar(CORPUS)
MAX_ORDEN = 4
COUNTS = {n: collections.defaultdict(collections.Counter) for n in range(1, MAX_ORDEN + 1)}
for i, token in enumerate(TOKENS):
    for n in range(1, MAX_ORDEN + 1):
        if i >= n - 1:
            COUNTS[n][tuple(TOKENS[i - n + 1:i])][token] += 1

def distribucion(contexto):
    for n in range(min(MAX_ORDEN - 1, len(contexto)), 0, -1):
        clave = tuple(contexto[-n:])
        if clave in COUNTS[n + 1]:
            return COUNTS[n + 1][clave]
    return COUNTS[1][()]

def generar(prompt, pasos=24, semilla=7):
    random.seed(semilla)
    contexto = tokenizar(prompt)
    for _ in range(pasos):
        dist = distribucion(contexto)
        candidatos = dist.most_common(5)
        palabras = [palabra for palabra, _ in candidatos]
        pesos = [cuenta for _, cuenta in candidatos]
        elegida = random.choices(palabras, weights=pesos, k=1)[0]
        contexto.append(elegida)
        if elegida in ".!?":
            break
    return " ".join(contexto)

print(f"Tokens del corpus: {len(TOKENS):,}")
print(generar("El caballero", 24))
""",
            caption=(
                "Un bucle autorregresivo mínimo sobre un corpus de El Quijote. "
                "Cambia el prompt, la longitud o la semilla. En un GPT real, los "
                "conteos se sustituyen por los logits de la red."
            ),
        ),
        callout(
            "warning",
            "Lo que la maqueta no hace",
            "El n-grama solo mira tres tokens: no entiende el significado, no generaliza a "
            "contextos nuevos y memoriza fragmentos del corpus. Si le pides una tarea, no la "
            "cumplirá. Un LLM reemplaza los conteos por <strong>pesos aprendidos</strong> y "
            "usa atención para integrar contextos mucho más largos. La tarea es la misma; "
            "cambian la arquitectura y la escala.",
        ),
        check(
            "¿Qué dos operaciones se repiten en cada paso de la generación autorregresiva?",
            "Predecir una distribución sobre el siguiente token y añadir el token elegido al "
            "contexto. La salida de un paso se convierte en la entrada del siguiente.",
        ),
        keypoints(
            [
                "GPT significa Generative Pretrained Transformer y genera token a token.",
                "La generación autorregresiva encadena predicción, anexión y repetición.",
                "Un modelo de n-gramas reproduce el bucle con conteos y backoff, sin red neuronal.",
                "La temperatura regula la variedad; el top-k recorta los candidatos improbables.",
                "La maqueta imita la tarea, no la comprensión: un LLM aprende representaciones, no tablas.",
            ]
        ),
    ),
    key_points=(
        "GPT es un transformer generativo preentrenado que predice el siguiente token.",
        "Generar es un bucle: predecir, añadir al contexto y repetir.",
        "Los n-gramas sirven de maqueta didáctica, no de sustituto de un LLM.",
        "Temperatura y top-k controlan el equilibrio entre coherencia y variedad.",
    ),
)
