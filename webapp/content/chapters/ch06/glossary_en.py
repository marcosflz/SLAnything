"""Chapter 6 glossary in English."""

from webapp.content.schema import GlossaryTerm

GLOSSARY_EN: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="classification head",
        definition=(
            "A linear layer that replaces the vocabulary projection and produces one score "
            "per class. In small GPT-2 it turns 768 dimensions into 2 logits."
        ),
        lesson="cabeza-clasificacion",
    ),
    GlossaryTerm(
        term="classification",
        definition=(
            "The task of assigning an input to one of several predefined labels. The model "
            "can only predict the classes it was trained on."
        ),
        lesson="finetuning-clasificacion",
    ),
    GlossaryTerm(
        term="test set",
        definition=(
            "The part of a dataset reserved for the final evaluation. It must not be used to "
            "tune hyperparameters or thresholds, or it stops being an independent estimate."
        ),
        lesson="datos-etiquetados",
    ),
    GlossaryTerm(
        term="class imbalance",
        definition=(
            "A situation in which one class appears much more often than another. It can make "
            "accuracy look high even when the model ignores the minority class."
        ),
        lesson="perdida-clasificacion",
    ),
    GlossaryTerm(
        term="F1",
        definition=(
            "The harmonic mean of precision and recall: 2PR/(P+R). It summarises the balance "
            "between both metrics and penalises a very low value in either."
        ),
        lesson="metricas",
    ),
    GlossaryTerm(
        term="data leakage",
        definition=(
            "Contamination of the test set with training information, for example by randomly "
            "splitting duplicates. It inflates metrics and hides generalisation failures."
        ),
        lesson="datos-etiquetados",
    ),
    GlossaryTerm(
        term="confusion matrix",
        definition=(
            "A 2×2 table counting true positives, false positives, false negatives, and true "
            "negatives. It is the basis for precision, recall, and F1."
        ),
        lesson="metricas",
    ),
    GlossaryTerm(
        term="early stopping",
        definition=(
            "A technique that stops training when a validation metric stops improving. It is "
            "often combined with restoring the best checkpoint."
        ),
        lesson="entrenamiento-clasificador",
    ),
    GlossaryTerm(
        term="precision",
        definition=(
            "The proportion of positive predictions that are correct: TP/(TP+FP). It is not "
            "the same as accuracy, which counts all correct predictions."
        ),
        lesson="metricas",
    ),
    GlossaryTerm(
        term="recall",
        definition=(
            "The proportion of real positives that the model detects: TP/(TP+FN). Also called "
            "sensitivity or true positive rate."
        ),
        lesson="metricas",
    ),
    GlossaryTerm(
        term="threshold",
        definition=(
            "The value above which a probability becomes a positive decision. Moving it "
            "changes the balance between false positives and false negatives."
        ),
        lesson="inferencia-clasificador",
    ),
)

# Alias compatible with the global course registry.
GLOSSARY = GLOSSARY_EN
