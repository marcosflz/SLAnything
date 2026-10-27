"""Chapter 5 glossary (EN)."""

from webapp.content.schema import GlossaryTerm

GLOSSARY_EN: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="cross-entropy",
        definition=(
            "A loss that compares the model's predicted distribution with the correct token; "
            "it equals the mean of −ln p over the batch positions. The higher the probability "
            "given to the correct token, the lower the cross-entropy."
        ),
        lesson="entropia-cruzada",
    ),
    GlossaryTerm(
        term="perplexity",
        definition=(
            "The exponential of mean cross-entropy, exp(L). It reads as the effective number "
            "of candidates among which the model is uncertain at each step; lower is better."
        ),
        lesson="entropia-cruzada",
    ),
    GlossaryTerm(
        term="log-probability",
        definition=(
            "The logarithm of the probability the model assigns to a token. It is negative "
            "because probabilities lie between 0 and 1; summing or averaging log-probabilities "
            "is more stable than multiplying tiny probabilities."
        ),
        lesson="entropia-cruzada",
    ),
    GlossaryTerm(
        term="backpropagation",
        definition=(
            "The algorithm that computes the gradient of the loss with respect to every weight "
            "by applying the chain rule backwards. In PyTorch it is invoked with loss.backward()."
        ),
        lesson="bucle-de-entrenamiento",
    ),
    GlossaryTerm(
        term="epoch",
        definition=(
            "One complete pass through the training set. Small corpora often need several "
            "epochs; large corpora are usually trained for a single pass."
        ),
        lesson="bucle-de-entrenamiento",
    ),
    GlossaryTerm(
        term="learning rate",
        definition=(
            "The factor that scales the step the optimizer takes when updating weights. Too "
            "high and training becomes unstable; too low and it crawls."
        ),
        lesson="optimizador-y-lr",
    ),
    GlossaryTerm(
        term="AdamW",
        definition=(
            "An Adam variant that applies weight decay decoupled from the gradient. It is a "
            "common choice for pretraining transformers because it regularises without "
            "interfering with the adaptive moments."
        ),
        lesson="optimizador-y-lr",
    ),
    GlossaryTerm(
        term="weight decay",
        definition=(
            "Regularisation that penalises large weights to reduce model complexity. In AdamW "
            "it is applied directly to the weights rather than through the loss gradient."
        ),
        lesson="optimizador-y-lr",
    ),
    GlossaryTerm(
        term="data loader",
        definition=(
            "An object that splits the corpus into batches and feeds them to the training loop. "
            "It controls batch size, stride between windows, shuffling, and whether to drop an "
            "incomplete final batch."
        ),
        lesson="carga-de-datos",
    ),
    GlossaryTerm(
        term="overfitting",
        definition=(
            "When a model improves on the training set but not on new data. The usual signal is "
            "validation loss that stops falling while training loss keeps decreasing."
        ),
        lesson="evaluacion-y-generacion",
    ),
    GlossaryTerm(
        term="validation set",
        definition=(
            "The portion of the corpus that is not used to update weights and estimates "
            "generalisation. The book reserves 10 % of the text for this purpose."
        ),
        lesson="evaluacion-y-generacion",
    ),
    GlossaryTerm(
        term="FLOP",
        definition=(
            "Floating-point operation. Training FLOPs are estimated as 6 · N · D, where N is "
            "the number of parameters and D the number of tokens processed."
        ),
        lesson="escala-y-coste",
    ),
    GlossaryTerm(
        term="GPU-hour",
        definition=(
            "A cost unit equal to using one GPU for one hour. It is obtained by dividing total "
            "FLOPs by effective throughput and time, and it lets you compare experiments and "
            "budgets."
        ),
        lesson="escala-y-coste",
    ),
)
