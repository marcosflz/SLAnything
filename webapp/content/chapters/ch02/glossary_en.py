"""Chapter 2 glossary (EN)."""

from webapp.content.schema import GlossaryTerm

GLOSSARY: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="BPE",
        definition=(
            "Byte pair encoding: an algorithm that builds a subword vocabulary by iteratively "
            "merging the most frequent pairs of symbols in a corpus."
        ),
        lesson="byte-pair-encoding",
    ),
    GlossaryTerm(
        term="merge",
        definition=(
            "A BPE operation that turns an adjacent pair of symbols into a single new symbol. "
            "Every merge adds one entry to the vocabulary."
        ),
        lesson="byte-pair-encoding",
    ),
    GlossaryTerm(
        term="subword",
        definition=(
            "A fragment of a word that the tokenizer treats as a unit. It lets the model "
            "represent new terms by combining known pieces."
        ),
        lesson="tokens-y-vocabulario",
    ),
    GlossaryTerm(
        term="vocabulary",
        definition=(
            "The finite, ordered set of tokens a model can represent, together with the mapping "
            "between each token and its identifier."
        ),
        lesson="tokens-y-vocabulario",
    ),
    GlossaryTerm(
        term="token ID",
        definition=(
            "The integer that identifies a token within the vocabulary. It is a lookup key, not "
            "a semantic representation."
        ),
        lesson="tokens-y-vocabulario",
    ),
    GlossaryTerm(
        term="special token",
        definition=(
            "A token that does not represent an ordinary word and serves a structural purpose, "
            "such as marking a document, a sequence end, or batch padding."
        ),
        lesson="tokens-especiales",
    ),
    GlossaryTerm(
        term="out-of-vocabulary",
        definition=(
            "The situation of a text piece with no entry in the tokenizer's vocabulary. Without "
            "subwords or an unknown token, it causes an encoding error."
        ),
        lesson="tokens-especiales",
    ),
    GlossaryTerm(
        term="decoding",
        definition=(
            "The reverse of encoding: turning a sequence of IDs into tokens and joining those "
            "tokens to reconstruct text."
        ),
        lesson="tokens-especiales",
    ),
    GlossaryTerm(
        term="sliding window",
        definition=(
            "A technique that cuts a long sequence into fixed-length fragments and advances by "
            "a step between fragments to generate training examples."
        ),
        lesson="ventana-deslizante",
    ),
    GlossaryTerm(
        term="stride",
        definition=(
            "The number of tokens the window advances between one example and the next. A "
            "smaller stride produces more overlap and more examples."
        ),
        lesson="ventana-deslizante",
    ),
    GlossaryTerm(
        term="input-target pair",
        definition=(
            "A pair formed by an input sequence and the same sequence shifted by one token, "
            "used as the target for next-token prediction."
        ),
        lesson="pares-entrada-objetivo",
    ),
    GlossaryTerm(
        term="cosine similarity",
        definition=(
            "A measure of the direction shared by two vectors: the dot product divided by the "
            "product of their norms. It ranges from −1 to 1 and ignores length."
        ),
        lesson="embeddings-y-significado",
    ),
    GlossaryTerm(
        term="embedding matrix",
        definition=(
            "A vocabulary × dimension table whose rows are the learned token vectors. The "
            "embedding layer selects one row per ID."
        ),
        lesson="vocabulario-y-embeddings",
    ),
    GlossaryTerm(
        term="positional embedding",
        definition=(
            "A vector added to a token embedding to indicate its position in the sequence. "
            "Without it, attention cannot distinguish word order."
        ),
        lesson="repaso-texto",
    ),
)
