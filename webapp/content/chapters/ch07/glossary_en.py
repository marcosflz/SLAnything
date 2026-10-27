"""Chapter 7 glossary (EN)."""

from webapp.content.schema import GlossaryTerm

GLOSSARY_EN: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="supervised instruction tuning",
        definition=(
            "Training that adapts a pretrained model with instruction-response pairs, keeping "
            "the next-token loss but changing the data and the mask. Also abbreviated as SFT."
        ),
        lesson="instrucciones-y-sft",
    ),
    GlossaryTerm(
        term="instruction-response pair",
        definition=(
            "The unit of SFT data: a request, an optional context, and a reference response. "
            "The quality and diversity of these pairs shape the learned behaviour."
        ),
        lesson="datos-de-instrucciones",
    ),
    GlossaryTerm(
        term="chat template",
        definition=(
            "A function that turns roles and messages into a text sequence with markers. It "
            "must be the same in training and inference so the input distribution does not "
            "change."
        ),
        lesson="plantillas-chat",
    ),
    GlossaryTerm(
        term="loss masking",
        definition=(
            "Replacing certain targets with a value the loss function ignores so they do not "
            "contribute to training. It is used for padding and, optionally, for instructions."
        ),
        lesson="mascara-de-perdida",
    ),
    GlossaryTerm(
        term="ignore_index",
        definition=(
            "A special value that cross_entropy discards when computing the loss. In PyTorch "
            "it defaults to -100, which is why it marks padding in targets."
        ),
        lesson="mascara-de-perdida",
    ),
    GlossaryTerm(
        term="collate function",
        definition=(
            "A function that receives a list of examples and builds a batch: it pads sequences, "
            "shifts targets, and applies the mask. In PyTorch it is passed to DataLoader as "
            "collate_fn."
        ),
        lesson="mascara-de-perdida",
    ),
    GlossaryTerm(
        term="LLM judge",
        definition=(
            "A language model used to score responses against a rubric, often with a reference "
            "answer. It scales well but approximates human judgement and may carry length, "
            "order, or model biases."
        ),
        lesson="evaluar-instrucciones",
    ),
    GlossaryTerm(
        term="preference pair",
        definition=(
            "Two responses to the same request, one preferred and one rejected. It is the signal "
            "used by RLHF and DPO to learn quality criteria that a single reference cannot "
            "capture."
        ),
        lesson="preferencias-y-seguridad",
    ),
    GlossaryTerm(
        term="DPO",
        definition=(
            "Direct preference optimisation: it tunes a model on preferred/rejected pairs "
            "without training a separate reward model. It keeps a reference model and a "
            "parameter limiting drift."
        ),
        lesson="preferencias-y-seguridad",
    ),
    GlossaryTerm(
        term="reward model",
        definition=(
            "A model that scores a response from human comparisons. RLHF uses it to guide policy "
            "optimisation; a badly calibrated reward model can be exploited."
        ),
        lesson="preferencias-y-seguridad",
    ),
)

__all__ = ["GLOSSARY_EN"]
