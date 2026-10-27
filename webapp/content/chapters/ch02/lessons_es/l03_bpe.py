"""Lección 3 · BPE paso a paso."""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
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
    slug="byte-pair-encoding",
    title="BPE paso a paso",
    summary=(
        "Byte pair encoding construye un vocabulario de subpalabras fusionando los pares de "
        "símbolos más frecuentes. Es el método que usan GPT-2, GPT-3 y buena parte de los "
        "modelos actuales."
    ),
    minutes=12,
    objectives=(
        "Describir el bucle de entrenamiento de BPE.",
        "Explicar por qué las fusiones dependen de las frecuencias del corpus.",
        "Tokenizar una palabra nueva con las fusiones aprendidas.",
        "Relacionar BPE con el vocabulario de 50 257 tokens de GPT-2.",
    ),
    blocks=(
        lead(
            "La tokenización por palabras se rompe con una palabra nueva. La tokenización por "
            "caracteres cubre cualquier texto, pero alarga las secuencias. BPE resuelve el "
            "dilema con una idea sencilla: empezar por caracteres y fusionar los pares que más "
            "se repiten, hasta construir piezas del tamaño adecuado."
        ),
        p(
            "El algoritmo se entrena en dos fases. Primero, cada palabra del corpus se "
            "descompone en caracteres y se marca su final; en el ejemplo de código omitimos esa "
            "marca para simplificar la salida. Segundo, se cuentan todos los pares de símbolos "
            "adyacentes; el par más frecuente se fusiona en un símbolo nuevo y se repite el "
            "proceso. Cada iteración añade una entrada al vocabulario. Al cabo de muchas "
            "iteraciones, los símbolos frecuentes representan morfemas o palabras completas, "
            "mientras que los infrecuentes siguen siendo fragmentos."
        ),
        table(
            ["Iteración", "Par más frecuente", "Fusión", "Efecto"],
            [
                ["0", "—", "—", "Vocabulario de caracteres"],
                ["1", "a + s", "as", "Aparece en «bajas», «casas», «paso»"],
                ["2", "c + as", "cas", "Agrupa «casa», «casas», «casero»"],
                ["3", "b + a", "ba", "Aparece en «bajo», «baja», «bajas»"],
                ["4", "ba + j", "baj", "El fragmento agrupa la raíz"],
            ],
            caption=(
                "Ejemplo didáctico con un corpus pequeño. Las fusiones reales dependen del "
                "corpus y del número de operaciones configurado."
            ),
            note=(
                "La tabla es una ilustración, no una salida del tokenizador de GPT-2. El orden "
                "exacto cambia con el corpus y con los criterios de desempate."
            ),
        ),
        h2("El bucle, con precisión"),
        p(
            "Entrenar BPE es repetir tres pasos hasta alcanzar el tamaño de vocabulario "
            "deseado. <strong>Uno:</strong> representar cada palabra como una secuencia de "
            "símbolos. <strong>Dos:</strong> contar los pares adyacentes ponderando por la "
            "frecuencia de la palabra. <strong>Tres:</strong> fusionar el par más frecuente en "
            "todas sus apariciones y registrar la regla. Si dos pares empatan, hace falta un "
            "criterio estable —por ejemplo, el orden lexicográfico— para que el resultado sea "
            "reproducible."
        ),
        p(
            "El número de fusiones es un hiperparámetro. Más fusiones producen tokens más "
            "largos, secuencias más cortas y un vocabulario mayor. Menos fusiones producen "
            "fragmentos pequeños y secuencias largas. GPT-2 fija el vocabulario en "
            "<strong>50 257 tokens</strong>; <code>&lt;|endoftext|&gt;</code> ocupa el último "
            "ID, el 50 256. Ese tamaño no es una ley natural: es el resultado de un compromiso "
            "entre cobertura, coste computacional y calidad observada."
        ),
        h2("Un BPE en miniatura"),
        p(
            "El siguiente ejemplo entrena un BPE sobre ocho palabras inventadas. No pretende "
            "reproducir el tokenizador de GPT: muestra el mecanismo completo en pocas líneas. "
            "Observa el orden de las fusiones y prueba a cambiar el número de operaciones o a "
            "añadir palabras al corpus. Después tokeniza una palabra que no estaba en el "
            "entrenamiento."
        ),
        py(
            """
from collections import Counter

# BPE simplificado: sin marca de final para que la salida sea más legible.
CORPUS = ["bajo", "bajo", "baja", "bajas", "casa", "casas", "casero", "paso"]


def contar_pares(tokens):
    return Counter(zip(tokens, tokens[1:]))


def fusionar(tokens, par):
    a, b = par
    salida = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens) and tokens[i] == a and tokens[i + 1] == b:
            salida.append(a + b)
            i += 2
        else:
            salida.append(tokens[i])
            i += 1
    return salida


def entrenar(palabras, operaciones):
    vocabulario = {tuple(palabra) for palabra in palabras}
    reglas = []
    for _ in range(operaciones):
        conteo = Counter()
        for tokens in vocabulario:
            conteo.update(contar_pares(tokens))
        if not conteo:
            break
        par, frecuencia = conteo.most_common(1)[0]
        if frecuencia < 2:
            break
        vocabulario = {tuple(fusionar(list(tokens), par)) for tokens in vocabulario}
        reglas.append((par, frecuencia, "".join(par)))
    return reglas


def tokenizar(palabra, reglas):
    tokens = list(palabra)
    for par, _, _ in reglas:
        tokens = fusionar(tokens, par)
    return tokens


reglas = entrenar(CORPUS, operaciones=6)
print("Fusiones aprendidas:")
for numero, ((a, b), frecuencia, resultado) in enumerate(reglas, start=1):
    print(f"  {numero}. {a} + {b} -> {resultado}  (frecuencia {frecuencia})")

for palabra in ("bajito", "casero", "pasillo"):
    piezas = tokenizar(palabra, reglas)
    print(f"{palabra:10} -> {piezas}  ({len(piezas)} tokens)")
""",
            caption=(
                "BPE didáctico: cuenta pares, fusiona el más frecuente y aplica las reglas a "
                "palabras nuevas. Cambia el corpus o el número de operaciones."
            ),
        ),
        p(
            "Hay un detalle que suele sorprender: la palabra «bajito» puede compartir la raíz "
            "«baj» con palabras vistas y dejar «ito» como fragmento. El tokenizador no sabe "
            "que «-ito» es un sufijo; solo aplica reglas de frecuencia. Esa ceguera es también "
            "su virtud: funciona con lenguas, nombres propios y código sin necesidad de un "
            "analizador morfológico."
        ),
        p(
            "El resultado también depende de la frecuencia mínima exigida. Si se permiten "
            "fusiones de pares que aparecen una sola vez, el vocabulario se llena de "
            "combinaciones accidentales y deja de comprimir. Por eso muchos entrenamientos "
            "exigen que el par supere un umbral antes de fusionarlo; es otra decisión que "
            "cambia el tokenizador final."
        ),
        lab("tokenizer"),
        callout(
            "info",
            "Por qué BPE casi elimina el OOV",
            "Si una palabra no aparece en el vocabulario, BPE la descompone en piezas que sí "
            "están. En el límite, todo texto puede representarse como bytes o caracteres. El "
            "libro lo comprueba con «someunknownPlace»: el tokenizador de GPT-2 la divide en "
            "varias subpalabras y la decodificación devuelve la palabra exacta.",
        ),
        check(
            "Dos corpus distintos producen fusiones distintas. ¿Significa eso que uno de los dos tokenizadores es incorrecto?",
            "No. BPE es un procedimiento guiado por frecuencias: el resultado depende de los "
            "datos. Dos tokenizadores pueden ser válidos y repartir el mismo texto de forma "
            "diferente. Lo importante es que cada modelo use el tokenizador con el que fue "
            "entrenado y que el vocabulario cubra bien su dominio.",
        ),
        h2("Lo que BPE no resuelve"),
        p(
            "BPE no entiende de significado. Una fusión frecuente puede unir fragmentos que "
            "pertenecen a morfemas distintos, y una palabra rara puede quedar partida en piezas "
            "poco intuitivas. Tampoco elimina los sesgos del corpus: si un término aparece poco, "
            "su representación será más fragmentada y recibirá menos entrenamiento. Es una "
            "herramienta de compresión y cobertura, no una teoría lingüística."
        ),
        p(
            "Con esto ya tenemos texto convertido en IDs de forma robusta. El siguiente paso "
            "es dar a cada ID una representación vectorial. Antes veremos cuántas dimensiones "
            "tiene esa representación y de dónde salen sus parámetros."
        ),
        keypoints(
            [
                "BPE empieza con caracteres y fusiona pares frecuentes de forma iterativa.",
                "Cada fusión añade un token nuevo al vocabulario.",
                "El número de fusiones controla el equilibrio entre cobertura y longitud.",
                "GPT-2 usa un vocabulario BPE de 50 257 tokens.",
                "Las palabras nuevas se tokenizan aplicando las fusiones aprendidas.",
                "BPE no garantiza tokens interpretables: garantiza cobertura.",
            ]
        ),
    ),
    key_points=(
        "BPE aprende fusiones a partir de la frecuencia de pares adyacentes.",
        "El vocabulario crece una entrada por fusión.",
        "GPT-2 usa 50 257 tokens BPE; <|endoftext|> es el 50 256.",
        "Las palabras desconocidas se descomponen en subpalabras.",
        "BPE depende del corpus y no codifica significado.",
    ),
    quiz_id=None,
)
