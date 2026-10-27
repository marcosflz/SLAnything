"""Lección 3 · Transformer y atención."""

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
    table,
)

LESSON = Lesson(
    number=3,
    slug="transformer-y-atencion",
    title="Transformer y atención",
    summary=(
        "Encoder, decoder y self-attention: la arquitectura que cambió el procesamiento "
        "del lenguaje y las dos familias que la adaptaron."
    ),
    minutes=12,
    objectives=(
        "Describir los dos módulos del transformer original y la asimetría entre ellos.",
        "Explicar por qué GPT conserva solo el decoder.",
        "Entender la self-attention como una ponderación contextual, no como una bolsa de palabras.",
        "Comparar BERT y GPT por arquitectura, objetivo y uso típico.",
    ),
    blocks=(
        lead(
            "En 2017, el artículo «Attention Is All You Need» presentó una arquitectura que "
            "prescindía de la recurrencia y organizaba todo alrededor de la atención. GPT, BERT "
            "y la mayoría de los modelos que usamos hoy descienden de aquel diseño."
        ),
        h2("Del encoder al decoder"),
        p(
            "La novedad no fue inventar la atención —ya existía—, sino construir toda la "
            "arquitectura alrededor de ella, sin recurrencia; eso permite procesar los tokens "
            "en paralelo durante el entrenamiento. El transformer original se construyó para "
            "traducir y tenía dos módulos. El "
            "<strong>encoder</strong> leía la frase de entrada completa y construía una "
            "representación contextual de cada token. El <strong>decoder</strong> generaba la "
            "traducción token a token, mirando la representación del encoder y su propia salida "
            "parcial. Esa asimetría es clave: el encoder ve toda la entrada; el decoder solo ve "
            "el pasado de lo que está generando, por eso la generación es autorregresiva. El "
            "artículo apilaba seis bloques de encoder y seis de decoder. GPT conserva solo el "
            "decoder porque su tarea es exactamente esa: continuar una secuencia hacia delante. "
            "GPT-3 llevó la misma familia a 96 capas y 175 000 millones de parámetros. No todo "
            "transformer es un LLM: también se usa en visión y audio. El laboratorio "
            "«Transformer» te permite recorrer las etapas de la figura."
        ),
        figure(
            "img/ch01/fig_1_4_transformer.png",
            "Diagrama del transformer original: el encoder procesa la frase de entrada y el decoder genera la traducción paso a paso.",
            "El encoder procesa la frase completa; el decoder genera la traducción palabra a "
            "palabra y reutiliza su propia salida.",
            credit="Figura 1.4 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        lab("transformer"),
        h2("La self-attention"),
        p(
            "La <strong>self-attention</strong> es el mecanismo que permite a cada token "
            "ponderar la relevancia de los demás. Para representar «cansado» en «El gato no "
            "cruzó la calle porque estaba cansado», el modelo puede dar mucho peso a «gato» y "
            "poco a «calle»: la conexión supera la distancia y el orden superficial. No es una "
            "bolsa de palabras: los tokens se comparan entre sí y la posición también cuenta, "
            "de modo que «el perro muerde al gato» no se representa igual que «el gato muerde "
            "al perro». Por dentro, cada token se proyecta en tres vectores: una "
            "<em>consulta</em> (qué busca), una <em>clave</em> (qué ofrece) y un "
            "<em>valor</em> (qué contenido aporta). La comparación entre consultas y claves "
            "produce los pesos; los valores se combinan con ellos. Esa representación cambia "
            "según el contexto: la misma palabra no pesa igual en dos frases distintas. En cada "
            "capa, varias cabezas de atención (<em>multi-head</em>) observan "
            "relaciones distintas en paralelo; las conexiones residuales y la normalización "
            "ayudan a que la información fluya y el entrenamiento sea estable. No hace falta "
            "memorizar las fórmulas: quédate con que la atención construye representaciones "
            "contextuales, no diccionarios de palabras aisladas. El laboratorio «Atención» te "
            "deja elegir una palabra y ver a cuáles da más peso."
        ),
        lab("attention"),
        py(
            """
import matplotlib.pyplot as plt

FRASE = ["El", "gato", "no", "cruzó", "la", "calle", "porque", "estaba", "cansado"]
PESOS = [0.02, 0.42, 0.02, 0.05, 0.01, 0.02, 0.03, 0.13, 0.30]

total = sum(PESOS)
pesos = [peso / total for peso in PESOS]
orden = sorted(range(len(pesos)), key=lambda i: pesos[i])
etiquetas = [FRASE[i] for i in orden]
valores = [pesos[i] for i in orden]
colores = ["#C77800" if etiqueta == "cansado" else "#9DB7F5" for etiqueta in etiquetas]

fig, ax = plt.subplots(figsize=(8, 3.4))
barras = ax.barh(etiquetas, valores, color=colores)
ax.set_xlabel("peso de atención")
ax.set_title("¿A qué atiende «cansado»?")
for barra, valor in zip(barras, valores):
    ax.text(valor + 0.005, barra.get_y() + barra.get_height() / 2, f"{valor:.0%}", va="center")
plt.tight_layout()
plt.show()

maxima = FRASE[pesos.index(max(pesos))]
print(f"«cansado» dedica más atención a «{maxima}».")
""",
            caption=(
                "Pesos de atención ilustrativos, normalizados para que sumen 1. "
                "Cambia los pesos y observa cómo se mueve el gráfico."
            ),
        ),
        table(
            ["Aspecto", "BERT", "GPT"],
            [
                [
                    "Arquitectura",
                    "Encoder-only: ve la frase completa en ambas direcciones.",
                    "Decoder-only: mira solo el pasado y genera de izquierda a derecha.",
                ],
                [
                    "Objetivo",
                    "Rellenar palabras enmascaradas (<em>masked language modeling</em>).",
                    "Predecir el siguiente token (<em>causal language modeling</em>).",
                ],
                [
                    "Uso típico",
                    "Clasificación, extracción de información y análisis de sentimiento.",
                    "Generación de texto, diálogo, código y asistentes.",
                ],
            ],
            caption=(
                "BERT y GPT: dos formas de usar el transformer. BERT entiende un texto "
                "cerrado; GPT lo continúa."
            ),
            note="La figura 1.5 resume los dos objetivos.",
        ),
        figure(
            "img/ch01/fig_1_5_bert_vs_gpt.png",
            "Comparación entre BERT, que rellena palabras enmascaradas, y GPT, que predice el siguiente token.",
            "BERT rellena huecos y mira en ambas direcciones; GPT completa texto de izquierda "
            "a derecha usando solo el pasado.",
            credit="Figura 1.5 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        callout(
            "warning",
            "No todo transformer es un LLM",
            "La arquitectura transformer también se usa en visión, audio y modelos "
            "multimodales. Un LLM es un transformer <strong>generativo</strong> entrenado a "
            "escala para procesar y producir lenguaje. La arquitectura es la misma familia; "
            "el objetivo y los datos cambian.",
        ),
        check(
            "¿Por qué GPT usa solo el decoder y no necesita un encoder?",
            "Porque se entrena para continuar texto: dado un prefijo, predice el siguiente "
            "token y va añadiendo su propia salida. El decoder, con atención causal, ya puede "
            "mirar todo el pasado; un encoder separado que leyera la frase completa no encaja "
            "con una tarea que debe avanzar sin ver el futuro.",
        ),
        keypoints(
            [
                "El transformer original combina un encoder que lee toda la entrada y un decoder que genera token a token.",
                "GPT es decoder-only porque su tarea es continuar texto de izquierda a derecha.",
                "La self-attention pondera la relevancia de otros tokens y conecta información distante.",
                "No es una bolsa de palabras: las relaciones y las posiciones importan.",
                "BERT y GPT adaptan el transformer a objetivos distintos: rellenar huecos frente a predecir el siguiente token.",
            ]
        ),
    ),
    key_points=(
        "El transformer original tiene encoder y decoder; GPT conserva solo el decoder.",
        "El decoder genera de forma autorregresiva y solo mira el pasado.",
        "La self-attention construye representaciones contextuales y conecta tokens distantes.",
        "Multi-head, conexiones residuales y normalización hacen la arquitectura más expresiva y estable.",
        "BERT usa el encoder para entender; GPT usa el decoder para generar.",
    ),
)
