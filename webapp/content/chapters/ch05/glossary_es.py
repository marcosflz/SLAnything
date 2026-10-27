"""Glosario del capítulo 5 (ES)."""

from webapp.content.schema import GlossaryTerm

GLOSSARY_ES: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="entropía cruzada",
        definition=(
            "Pérdida que compara la distribución predicha por el modelo con el token correcto: "
            "equivale a la media de −ln p en las posiciones del lote. Cuanto mayor es la "
            "probabilidad asignada al token correcto, menor es la entropía cruzada."
        ),
        lesson="entropia-cruzada",
    ),
    GlossaryTerm(
        term="perplejidad",
        definition=(
            "Exponencial de la entropía cruzada media, exp(L). Se interpreta como el número "
            "efectivo de candidatos entre los que el modelo duda en cada paso; cuanto más "
            "baja, mejor."
        ),
        lesson="entropia-cruzada",
    ),
    GlossaryTerm(
        term="log-probabilidad",
        definition=(
            "Logaritmo de la probabilidad que el modelo asigna a un token. Es negativo porque "
            "las probabilidades están entre 0 y 1; sumar o promediar log-probabilidades es más "
            "estable que multiplicar probabilidades muy pequeñas."
        ),
        lesson="entropia-cruzada",
    ),
    GlossaryTerm(
        term="retropropagación",
        definition=(
            "Algoritmo que calcula el gradiente de la pérdida respecto a cada peso aplicando "
            "la regla de la cadena hacia atrás. En PyTorch se invoca con loss.backward()."
        ),
        lesson="bucle-de-entrenamiento",
    ),
    GlossaryTerm(
        term="época",
        definition=(
            "Una pasada completa por el conjunto de entrenamiento. En corpus pequeños se "
            "suelen hacer varias épocas; en corpus masivos es habitual entrenar durante una "
            "sola pasada."
        ),
        lesson="bucle-de-entrenamiento",
    ),
    GlossaryTerm(
        term="tasa de aprendizaje",
        definition=(
            "Factor que escala el tamaño del paso que da el optimizador al actualizar los "
            "pesos. Demasiado alta desestabiliza el entrenamiento; demasiado baja lo hace "
            "lento."
        ),
        lesson="optimizador-y-lr",
    ),
    GlossaryTerm(
        term="AdamW",
        definition=(
            "Variante de Adam que aplica el decaimiento de pesos de forma desacoplada del "
            "gradiente. Es una elección habitual para preentrenar transformers porque "
            "regulariza sin interferir con los momentos adaptativos."
        ),
        lesson="optimizador-y-lr",
    ),
    GlossaryTerm(
        term="decaimiento de pesos",
        definition=(
            "Regularización que penaliza los pesos grandes para reducir la complejidad del "
            "modelo. En AdamW se aplica directamente sobre los pesos, no a través del "
            "gradiente de la pérdida."
        ),
        lesson="optimizador-y-lr",
    ),
    GlossaryTerm(
        term="cargador de datos",
        definition=(
            "Objeto que divide el corpus en lotes y los entrega al bucle de entrenamiento. "
            "Controla el tamaño de lote, el desplazamiento entre ventanas, el mezclado y si "
            "se descarta el último lote incompleto."
        ),
        lesson="carga-de-datos",
    ),
    GlossaryTerm(
        term="sobreajuste",
        definition=(
            "Situación en la que el modelo mejora en el conjunto de entrenamiento pero no en "
            "datos nuevos. La señal típica es que la pérdida de validación deja de bajar "
            "mientras la de entrenamiento sigue disminuyendo."
        ),
        lesson="evaluacion-y-generacion",
    ),
    GlossaryTerm(
        term="conjunto de validación",
        definition=(
            "Porción del corpus que no se usa para actualizar los pesos y sirve para estimar "
            "la generalización. En el libro se reserva un 10 % del texto para esta función."
        ),
        lesson="evaluacion-y-generacion",
    ),
    GlossaryTerm(
        term="FLOP",
        definition=(
            "Operación de coma flotante. Los FLOPs de entrenamiento se estiman con 6 · N · D, "
            "donde N es el número de parámetros y D el número de tokens procesados."
        ),
        lesson="escala-y-coste",
    ),
    GlossaryTerm(
        term="GPU-hora",
        definition=(
            "Unidad de coste equivalente a usar una GPU durante una hora. Se obtiene dividiendo "
            "los FLOPs totales entre el rendimiento efectivo y el tiempo, y sirve para comparar "
            "experimentos y presupuestos."
        ),
        lesson="escala-y-coste",
    ),
)
