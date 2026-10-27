"""Glosario del capítulo 1."""

from webapp.content.schema import GlossaryTerm

GLOSSARY: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="alucinación",
        definition=(
            "Respuesta fluida y plausible que no está respaldada por los hechos ni por el "
            "contexto aportado. No implica que el modelo mienta: optimiza verosimilitud, no "
            "verdad."
        ),
        lesson="repaso",
    ),
    GlossaryTerm(
        term="autorregresivo",
        definition=(
            "Modelo que genera una secuencia un token cada vez y reutiliza su propia salida "
            "como parte de la entrada del paso siguiente."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="autosupervisado",
        definition=(
            "Entrenamiento en el que la etiqueta se obtiene del propio dato, sin anotación "
            "humana. En un LLM, la entrada es el texto y el objetivo es el siguiente token."
        ),
        lesson="pretraining-y-finetuning",
    ),
    GlossaryTerm(
        term="benchmark",
        definition=(
            "Conjunto estandarizado de tareas y métricas para comparar modelos. Un buen "
            "resultado en un benchmark no garantiza buen rendimiento en otro dominio."
        ),
        lesson="repaso",
    ),
    GlossaryTerm(
        term="BERT",
        definition=(
            "Modelo basado en el encoder del transformer que se entrena prediciendo palabras "
            "enmascaradas y mirando el contexto en ambas direcciones. Destaca en clasificación "
            "y extracción de información."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="capa",
        definition=(
            "Conjunto de operaciones que transforma las representaciones y se apila sobre las "
            "anteriores. En un transformer, cada capa combina atención y una red feed-forward "
            "con conexiones residuales."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="comportamiento emergente",
        definition=(
            "Capacidad que no se entrenó de forma explícita y aparece al aumentar la escala y "
            "la diversidad de datos, como traducir o resumir. Su detección depende de cómo se "
            "evalúe."
        ),
        lesson="zero-shot-y-few-shot",
    ),
    GlossaryTerm(
        term="contexto",
        definition=(
            "Texto que el modelo tiene disponible para condicionar la siguiente predicción: "
            "instrucciones, ejemplos y turnos anteriores. No es memoria permanente."
        ),
        lesson="zero-shot-y-few-shot",
    ),
    GlossaryTerm(
        term="corpus",
        definition=(
            "Conjunto de textos usado para entrenar o evaluar un modelo. Su tamaño, diversidad "
            "y filtrado condicionan lo que el modelo aprende."
        ),
        lesson="escala-de-datos",
    ),
    GlossaryTerm(
        term="cuantización",
        definition=(
            "Reducción de la precisión numérica de los pesos, por ejemplo de 16 a 8 o 4 bits, "
            "para ocupar menos memoria y acelerar la inferencia a cambio de cierta pérdida de "
            "calidad."
        ),
        lesson="que-es-un-llm",
    ),
    GlossaryTerm(
        term="decoder",
        definition=(
            "Módulo del transformer que genera la salida token a token mirando solo lo ya "
            "producido. GPT es un modelo decoder-only."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="destilación",
        definition=(
            "Técnica para entrenar un modelo pequeño imitando las salidas o distribuciones de "
            "uno grande. Busca conservar parte de la capacidad con menos parámetros y coste."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="embedding",
        definition=(
            "Representación vectorial aprendida de un token, una posición u otro elemento. "
            "Vectores cercanos tienden a codificar significados o usos parecidos."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="encoder",
        definition=(
            "Módulo del transformer que procesa la entrada completa y construye "
            "representaciones contextuales bidireccionales. BERT usa el encoder."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="escalado",
        definition=(
            "Aumento coordinado de parámetros, datos y cómputo. Las leyes de escalado "
            "describen cómo cambia la pérdida al crecer estos factores."
        ),
        lesson="escala-de-datos",
    ),
    GlossaryTerm(
        term="few-shot",
        definition=(
            "Prompt que incluye unos pocos ejemplos resueltos antes de la tarea. El modelo se "
            "adapta en el contexto sin actualizar sus pesos."
        ),
        lesson="zero-shot-y-few-shot",
    ),
    GlossaryTerm(
        term="finetuning",
        definition=(
            "Segunda fase de entrenamiento, con datos etiquetados y menos volumen, que "
            "especializa un modelo base en una tarea o dominio. Sí modifica los pesos."
        ),
        lesson="pretraining-y-finetuning",
    ),
    GlossaryTerm(
        term="GPT",
        definition=(
            "Familia de modelos generativos basados en el decoder del transformer, "
            "preentrenados para predecir el siguiente token. GPT significa Generative "
            "Pretrained Transformer."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="GPU",
        definition=(
            "Procesador paralelo masivo usado para entrenar y ejecutar redes neuronales. Su "
            "memoria limita el tamaño del modelo y del lote."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="inferencia",
        definition=(
            "Uso de un modelo ya entrenado para producir una respuesta. No actualiza los "
            "pesos; su coste depende de los parámetros, del contexto y de los tokens generados."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="LLM",
        definition=(
            "Large language model: red neuronal profunda entrenada con grandes corpus para "
            "procesar y generar lenguaje. Su tarea base es predecir el siguiente token."
        ),
        lesson="que-es-un-llm",
    ),
    GlossaryTerm(
        term="logit",
        definition=(
            "Puntuación sin normalizar que la red asigna a cada token antes de convertirla en "
            "probabilidad. El softmax transforma los logits en una distribución que suma 1."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="multi-head",
        definition=(
            "Variante de la atención que ejecuta varias cabezas en paralelo sobre "
            "proyecciones distintas. Cada cabeza puede especializarse en un tipo de relación."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="normalización",
        definition=(
            "Operación que reescala las activaciones para estabilizar y acelerar el "
            "entrenamiento. En transformers se aplica, por ejemplo, LayerNorm antes o después "
            "de cada subcapa."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="parámetro",
        definition=(
            "Peso ajustable de la red que el entrenamiento modifica para reducir el error. El "
            "número de parámetros mide la capacidad del modelo, no su calidad por sí solo."
        ),
        lesson="que-es-un-llm",
    ),
    GlossaryTerm(
        term="posición",
        definition=(
            "Señal que indica el lugar de cada token en la secuencia. La atención no tiene "
            "orden implícito, así que el transformer añade esta información a los embeddings."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="pretraining",
        definition=(
            "Primera fase de entrenamiento con texto sin etiquetar y la tarea de predecir el "
            "siguiente token. Produce un modelo base con conocimiento general del lenguaje."
        ),
        lesson="pretraining-y-finetuning",
    ),
    GlossaryTerm(
        term="probabilidad",
        definition=(
            "Valor entre 0 y 1 que expresa cuánto cree el modelo que un token es el siguiente. "
            "Las probabilidades de todos los candidatos suman 1 tras el softmax."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="prompt",
        definition=(
            "Entrada que se da al modelo para condicionar su respuesta: instrucción, contexto "
            "y, si se quiere, ejemplos. No cambia los pesos."
        ),
        lesson="zero-shot-y-few-shot",
    ),
    GlossaryTerm(
        term="residual",
        definition=(
            "Conexión que suma la entrada de una subcapa a su salida. Facilita el flujo del "
            "gradiente y permite apilar muchas capas."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="RLHF",
        definition=(
            "Reinforcement Learning from Human Feedback: ajuste del modelo con un modelo de "
            "recompensa entrenado a partir de preferencias humanas. Se usa para alinear las "
            "respuestas con lo que los usuarios valoran."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="self-attention",
        definition=(
            "Mecanismo que calcula, para cada token, cuánto debe fijarse en los demás tokens "
            "de la secuencia. Combina esa ponderación para construir representaciones "
            "contextuales."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="temperatura",
        definition=(
            "Parámetro de muestreo que aplana o agudiza la distribución de probabilidad. Una "
            "temperatura baja hace la salida más conservadora; una alta, más variada y "
            "arriesgada."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="token",
        definition=(
            "Unidad de texto que el modelo lee y genera: una palabra, un fragmento de palabra "
            "o un signo. El texto se divide en tokens antes de entrar en la red."
        ),
        lesson="escala-de-datos",
    ),
    GlossaryTerm(
        term="tokenización",
        definition=(
            "Proceso de dividir el texto en tokens y asignarles identificadores numéricos. El "
            "vocabulario y las reglas del tokenizador deben coincidir entre entrenamiento e "
            "inferencia."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="top-k",
        definition=(
            "Filtro de muestreo que conserva solo los k tokens más probables y reparte la "
            "probabilidad entre ellos. Evita elegir candidatos absurdos de la cola."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="transformer",
        definition=(
            "Arquitectura de red neuronal presentada en 2017 basada en atención, con módulos "
            "encoder y decoder. Es la base de BERT, GPT y la mayoría de los LLM actuales."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="ventana de contexto",
        definition=(
            "Número máximo de tokens que el modelo puede procesar a la vez. Todo lo que queda "
            "fuera deja de estar disponible para la predicción."
        ),
        lesson="zero-shot-y-few-shot",
    ),
    GlossaryTerm(
        term="zero-shot",
        definition=(
            "Resolver una tarea solo con una instrucción, sin ejemplos resueltos en el prompt. "
            "El modelo usa lo aprendido durante el pretraining."
        ),
        lesson="zero-shot-y-few-shot",
    ),
)
