"""Lección 4 · La escala de los datos."""

from webapp.content.schema import (
    Lesson,
    bullets,
    callout,
    check,
    h2,
    keypoints,
    lead,
    p,
    py,
    table,
)

LESSON = Lesson(
    number=4,
    slug="escala-de-datos",
    title="La escala de los datos",
    summary=(
        "Qué corpus entrenaron a GPT-3, cómo se mezclan las fuentes y por qué la calidad "
        "importa tanto como la cantidad."
    ),
    minutes=8,
    objectives=(
        "Identificar las cinco fuentes del corpus de GPT-3 y su peso en la mezcla.",
        "Leer críticamente una tabla de cifras y detectar una suma que no cuadra.",
        "Explicar por qué filtrar, deduplicar y elegir la mezcla forma parte del diseño.",
        "Relacionar los sesgos del corpus con los sesgos del modelo.",
    ),
    blocks=(
        lead(
            "Un LLM no aprende de un libro: aprende de una biblioteca. Pero esa biblioteca "
            "no es neutral ni está ordenada. Antes de entrenar hay que decidir qué entra, qué "
            "se descarta y con qué peso se mezcla cada fuente."
        ),
        h2("El corpus de GPT-3"),
        p(
            "La tabla 1.1 del libro desglosa el corpus de GPT-3. Hay cinco fuentes: "
            "CommonCrawl filtrado, WebText2, Books1, Books2 y Wikipedia. Juntas suman cientos "
            "de miles de millones de tokens disponibles, con una mezcla muy desigual: la web "
            "domina y Wikipedia aporta una fracción pequeña pero de alta calidad. Un "
            "<strong>token</strong> es una unidad de texto que el modelo lee y genera; puede ser "
            "una palabra, un fragmento de palabra o un signo. En inglés se suele estimar que un "
            "token equivale a unas 0,75 palabras; en español, a algo menos."
        ),
        table(
            ["Fuente", "Tipo", "Tokens disponibles", "Peso en la mezcla"],
            [
                ["CommonCrawl (filtrado)", "Rastreo web", "410 000 millones", "60 %"],
                ["WebText2", "Rastreo web", "19 000 millones", "22 %"],
                ["Books1", "Corpus de libros", "12 000 millones", "8 %"],
                ["Books2", "Corpus de libros", "55 000 millones", "8 %"],
                ["Wikipedia", "Texto de alta calidad", "3 000 millones", "3 %"],
            ],
            caption=(
                "Tabla 1.1 · Raschka, Build a Large Language Model (From Scratch), Manning, "
                "2024. Tokens disponibles y peso de cada fuente en la mezcla."
            ),
            note=(
                "El peso indica la proporción con la que se muestrea cada fuente durante el "
                "entrenamiento, no el porcentaje del total de tokens disponibles; los "
                "porcentajes son aproximados."
            ),
        ),
        callout(
            "warning",
            "Una suma que no cuadra",
            "Suma las filas: 410 + 19 + 12 + 55 + 3 = <strong>499 mil millones</strong>. El "
            "texto del libro habla de <strong>509 mil millones</strong>. Hay, por tanto, 10 mil "
            "millones de diferencia. El libro no ofrece una explicación en ese punto y no "
            "conviene inventarla. La lección metodológica es la importante: <strong>las tablas "
            "también se auditan</strong>. Y conviene no confundir dos cifras: GPT-3 se entrenó "
            "con unos 300 000 millones de tokens, no con todos los disponibles."
        ),
        h2("Calidad, no solo cantidad"),
        p(
            "La cantidad impresiona, pero el filtrado decide buena parte del resultado. "
            "CommonCrawl es un rastreo de la web abierta: contiene spam, texto automático, "
            "duplicados, plantillas, errores de codificación y contenido tóxico. Entrenar sin "
            "depurar enseña al modelo a reproducir ese ruido. Por eso los equipos aplican "
            "filtros de calidad, eliminan duplicados y ajustan la mezcla. La deduplicación "
            "importa especialmente: si una frase aparece mil veces, el modelo la memoriza y "
            "gasta capacidad en repetirla en lugar de aprender patrones generales."
        ),
        bullets(
            [
                "<strong>Filtrado</strong>: descartar páginas vacías, spam, código roto o texto generado automáticamente.",
                "<strong>Deduplicación</strong>: evitar que una misma página o frase aparezca muchas veces.",
                "<strong>Mezcla</strong>: decidir cuánto peso tiene la web, el libro o la enciclopedia.",
                "<strong>Evaluación</strong>: medir qué sesgos y qué lagunas quedan después de filtrar.",
            ]
        ),
        p(
            "Ningún corpus es neutro. La web sobrerrepresenta idiomas, países y puntos de vista "
            "con más presencia digital; los libros arrastran los sesgos de sus autores y de su "
            "época; Wikipedia, pese a su vocación enciclopédica, también tiene huecos. Un modelo "
            "entrenado con esa mezcla hereda y amplifica esos desequilibrios. La decisión de qué "
            "datos entran es, por tanto, una decisión técnica y también editorial. Más datos no "
            "arreglan un corpus mal elegido: a veces solo hacen el sesgo más difícil de detectar."
        ),
        p(
            "La columna de peso no mide la calidad ni el tamaño: indica con qué probabilidad se "
            "muestrea cada fuente al construir los lotes de entrenamiento. Por eso WebText2, con "
            "solo 19 000 millones de tokens, pesa más que Books2, que tiene casi el triple. La "
            "mezcla es una decisión de diseño: cambiar esos porcentajes cambia lo que el modelo "
            "ve y lo que aprende."
        ),
        py(
            """
DATOS = [
    ("CommonCrawl (filtrado)", 410, 60),
    ("WebText2", 19, 22),
    ("Books1", 12, 8),
    ("Books2", 55, 8),
    ("Wikipedia", 3, 3),
]

print(f"{'Fuente':24} {'Tokens':>8} {'Peso':>6}")
print("-" * 42)
for fuente, tokens, peso in DATOS:
    print(f"{fuente:24} {tokens:>6} B {peso:>5} %")

total = sum(tokens for _, tokens, _ in DATOS)
print(f"\\nSuma de tokens disponibles: {total:,} mil millones")
print("GPT-3 se entrenó con unos 300 000 millones, no con todo el corpus.")
""",
            caption=(
                "La tabla en código: cambia un peso y comprueba que la suma de "
                "tokens disponibles no cambia, pero la mezcla sí."
            ),
        ),
        check(
            "La tabla suma 499 000 millones de tokens y el texto dice 509 000 millones. ¿Qué conclusión sacas?",
            "Que hay una discrepancia de 10 000 millones que el libro no explica en ese punto. "
            "No conviene inventar una causa. La conclusión útil es metodológica: comprobar las "
            "cifras y no confundir el corpus disponible con los 300 000 millones de tokens con "
            "los que se entrenó GPT-3.",
        ),
        keypoints(
            [
                "GPT-3 mezcló cinco fuentes: CommonCrawl, WebText2, Books1, Books2 y Wikipedia.",
                "La web domina la mezcla; los libros y Wikipedia aportan diversidad y calidad.",
                "La tabla suma 499 000 millones, pero el texto dice 509 000 millones: hay una discrepancia sin explicar.",
                "GPT-3 se entrenó con unos 300 000 millones de tokens, no con todo el corpus disponible.",
                "Filtrar, deduplicar y elegir la mezcla importa tanto como acumular datos.",
                "Todo corpus tiene sesgos; el modelo los hereda.",
            ]
        ),
    ),
    key_points=(
        "El corpus de GPT-3 combina web, libros y Wikipedia en proporciones muy desiguales.",
        "La tabla 1.1 suma 499 000 millones de tokens, pero el texto habla de 509 000 millones.",
        "El corpus disponible no es lo mismo que los 300 000 millones de tokens vistos.",
        "La calidad, la deduplicación y la mezcla son decisiones de diseño, no detalles.",
        "Un corpus sesgado produce un modelo sesgado.",
    ),
)
