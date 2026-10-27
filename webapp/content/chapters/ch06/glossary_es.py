"""Glosario del capítulo 6 en español."""

from webapp.content.schema import GlossaryTerm

GLOSSARY_ES: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="cabeza de clasificación",
        definition=(
            "Capa lineal que sustituye la proyección al vocabulario y produce una puntuación "
            "por clase. En GPT-2 pequeño transforma 768 dimensiones en 2 logits."
        ),
        lesson="cabeza-clasificacion",
    ),
    GlossaryTerm(
        term="clasificación",
        definition=(
            "Tarea de asignar una entrada a una de varias etiquetas prefijadas. El modelo "
            "solo puede predecir las clases con las que se entrenó."
        ),
        lesson="finetuning-clasificacion",
    ),
    GlossaryTerm(
        term="conjunto de prueba",
        definition=(
            "Parte del dataset reservada para la evaluación final. No debe usarse para "
            "ajustar hiperparámetros ni umbrales, o dejará de ser una estimación independiente."
        ),
        lesson="datos-etiquetados",
    ),
    GlossaryTerm(
        term="desbalance de clases",
        definition=(
            "Situación en la que una clase aparece mucho más que otra. Puede hacer que la "
            "accuracy sea alta aunque el modelo ignore la clase minoritaria."
        ),
        lesson="perdida-clasificacion",
    ),
    GlossaryTerm(
        term="F1",
        definition=(
            "Media armónica de precisión y recall: 2PR/(P+R). Resume el equilibrio entre "
            "ambas métricas y penaliza que una de ellas sea muy baja."
        ),
        lesson="metricas",
    ),
    GlossaryTerm(
        term="fuga de datos",
        definition=(
            "Contaminación del conjunto de prueba con información del entrenamiento, por "
            "ejemplo al dividir duplicados al azar. Infla las métricas y oculta fallos de "
            "generalización."
        ),
        lesson="datos-etiquetados",
    ),
    GlossaryTerm(
        term="matriz de confusión",
        definition=(
            "Tabla 2×2 que cuenta verdaderos positivos, falsos positivos, falsos negativos y "
            "verdaderos negativos. Es la base para calcular precisión, recall y F1."
        ),
        lesson="metricas",
    ),
    GlossaryTerm(
        term="parada temprana",
        definition=(
            "Técnica que detiene el entrenamiento cuando una métrica de validación deja de "
            "mejorar. Suele combinarse con restaurar el mejor checkpoint."
        ),
        lesson="entrenamiento-clasificador",
    ),
    GlossaryTerm(
        term="precisión",
        definition=(
            "Proporción de predicciones positivas que son correctas: TP/(TP+FP). No es lo "
            "mismo que la exactitud o accuracy, que cuenta todos los aciertos."
        ),
        lesson="metricas",
    ),
    GlossaryTerm(
        term="recall",
        definition=(
            "Proporción de positivos reales que el modelo detecta: TP/(TP+FN). También se "
            "llama exhaustividad o sensibilidad."
        ),
        lesson="metricas",
    ),
    GlossaryTerm(
        term="umbral",
        definition=(
            "Valor a partir del cual una probabilidad se convierte en una decisión positiva. "
            "Moverlo cambia el equilibrio entre falsos positivos y falsos negativos."
        ),
        lesson="inferencia-clasificador",
    ),
)

# Alias compatible con el registro global del curso.
GLOSSARY = GLOSSARY_ES
