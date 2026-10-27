"""Glossary for chapter 1 (English)."""

from webapp.content.schema import GlossaryTerm

GLOSSARY: tuple[GlossaryTerm, ...] = (
    GlossaryTerm(
        term="hallucination",
        definition=(
            "A fluent, plausible answer that is not supported by the facts or by the "
            "provided context. It does not mean the model is lying: it optimizes "
            "likelihood, not truth."
        ),
        lesson="repaso",
    ),
    GlossaryTerm(
        term="autoregressive",
        definition=(
            "A model that generates a sequence one token at a time and reuses its own "
            "output as part of the next step's input."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="self-supervised",
        definition=(
            "Training in which the label comes from the data itself, without human "
            "annotation. In an LLM, the input is the text and the target is the next token."
        ),
        lesson="pretraining-y-finetuning",
    ),
    GlossaryTerm(
        term="benchmark",
        definition=(
            "A standardized set of tasks and metrics for comparing models. A good "
            "benchmark score does not guarantee good performance in another domain."
        ),
        lesson="repaso",
    ),
    GlossaryTerm(
        term="BERT",
        definition=(
            "A model based on the transformer encoder that is trained by predicting masked "
            "words while looking at context in both directions. It excels at classification "
            "and information extraction."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="layer",
        definition=(
            "A set of operations that transforms representations and is stacked on previous "
            "ones. In a transformer, each layer combines attention and a feed-forward network "
            "with residual connections."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="emergent behaviour",
        definition=(
            "A capability that was not explicitly trained and appears as scale and data "
            "diversity increase, such as translating or summarizing. Detecting it depends on "
            "how it is evaluated."
        ),
        lesson="zero-shot-y-few-shot",
    ),
    GlossaryTerm(
        term="context",
        definition=(
            "The text available to the model to condition the next prediction: instructions, "
            "examples, and previous turns. It is not permanent memory."
        ),
        lesson="zero-shot-y-few-shot",
    ),
    GlossaryTerm(
        term="corpus",
        definition=(
            "A collection of texts used to train or evaluate a model. Its size, diversity, "
            "and filtering shape what the model learns."
        ),
        lesson="escala-de-datos",
    ),
    GlossaryTerm(
        term="quantization",
        definition=(
            "Reducing the numerical precision of weights, for example from 16 to 8 or 4 bits, "
            "to use less memory and speed up inference at the cost of some quality loss."
        ),
        lesson="que-es-un-llm",
    ),
    GlossaryTerm(
        term="decoder",
        definition=(
            "The transformer module that generates the output token by token while looking "
            "only at what has already been produced. GPT is a decoder-only model."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="distillation",
        definition=(
            "A technique for training a small model by imitating the outputs or distributions "
            "of a large one. It aims to retain part of the capability with fewer parameters "
            "and lower cost."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="embedding",
        definition=(
            "A learned vector representation of a token, a position, or another element. "
            "Nearby vectors tend to encode similar meanings or uses."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="encoder",
        definition=(
            "The transformer module that processes the whole input and builds bidirectional "
            "contextual representations. BERT uses the encoder."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="scaling",
        definition=(
            "A coordinated increase in parameters, data, and compute. Scaling laws describe "
            "how loss changes as these factors grow."
        ),
        lesson="escala-de-datos",
    ),
    GlossaryTerm(
        term="few-shot",
        definition=(
            "A prompt that includes a few solved examples before the task. The model adapts "
            "in context without updating its weights."
        ),
        lesson="zero-shot-y-few-shot",
    ),
    GlossaryTerm(
        term="finetuning",
        definition=(
            "A second training stage, with labeled data and less volume, that specializes a "
            "base model for a task or domain. It does modify the weights."
        ),
        lesson="pretraining-y-finetuning",
    ),
    GlossaryTerm(
        term="GPT",
        definition=(
            "A family of generative models based on the transformer decoder, pretrained to "
            "predict the next token. GPT stands for Generative Pretrained Transformer."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="GPU",
        definition=(
            "A massively parallel processor used to train and run neural networks. Its memory "
            "limits model and batch size."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="inference",
        definition=(
            "Using an already trained model to produce a response. It does not update the "
            "weights; its cost depends on the parameters, the context, and the generated tokens."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="LLM",
        definition=(
            "Large language model: a deep neural network trained on large corpora to process "
            "and generate language. Its base task is predicting the next token."
        ),
        lesson="que-es-un-llm",
    ),
    GlossaryTerm(
        term="logit",
        definition=(
            "An unnormalized score that the network assigns to each token before turning it "
            "into a probability. Softmax transforms logits into a distribution that sums to 1."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="multi-head",
        definition=(
            "A variant of attention that runs several heads in parallel over different "
            "projections. Each head can specialize in a type of relationship."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="normalization",
        definition=(
            "An operation that rescales activations to stabilize and speed up training. In "
            "transformers it is applied, for example, as LayerNorm before or after each "
            "sublayer."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="parameter",
        definition=(
            "An adjustable weight of the network that training modifies to reduce error. The "
            "number of parameters measures the model's capacity, not its quality on its own."
        ),
        lesson="que-es-un-llm",
    ),
    GlossaryTerm(
        term="position",
        definition=(
            "A signal that indicates where each token sits in the sequence. Attention has no "
            "implicit order, so the transformer adds this information to the embeddings."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="pretraining",
        definition=(
            "The first training stage, using unlabeled text and the task of predicting the "
            "next token. It produces a base model with general knowledge of the language."
        ),
        lesson="pretraining-y-finetuning",
    ),
    GlossaryTerm(
        term="probability",
        definition=(
            "A value between 0 and 1 that expresses how strongly the model believes a token "
            "is the next one. The probabilities of all candidates sum to 1 after softmax."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="prompt",
        definition=(
            "The input given to the model to condition its response: instruction, context, "
            "and, if desired, examples. It does not change the weights."
        ),
        lesson="zero-shot-y-few-shot",
    ),
    GlossaryTerm(
        term="residual",
        definition=(
            "A connection that adds a sublayer's input to its output. It helps gradients flow "
            "and makes it possible to stack many layers."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="RLHF",
        definition=(
            "Reinforcement Learning from Human Feedback: adjusting the model with a reward "
            "model trained from human preferences. It is used to align responses with what "
            "users value."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="self-attention",
        definition=(
            "A mechanism that computes, for each token, how much it should focus on the other "
            "tokens in the sequence. It combines that weighting to build contextual "
            "representations."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="temperature",
        definition=(
            "A sampling parameter that flattens or sharpens the probability distribution. A "
            "low temperature makes output more conservative; a high one makes it more varied "
            "and risky."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="token",
        definition=(
            "A unit of text that the model reads and generates: a word, a word fragment, or a "
            "punctuation mark. Text is split into tokens before entering the network."
        ),
        lesson="escala-de-datos",
    ),
    GlossaryTerm(
        term="tokenization",
        definition=(
            "The process of splitting text into tokens and assigning them numerical "
            "identifiers. The vocabulary and tokenizer rules must match between training and "
            "inference."
        ),
        lesson="como-se-construye",
    ),
    GlossaryTerm(
        term="top-k",
        definition=(
            "A sampling filter that keeps only the k most probable tokens and redistributes "
            "probability among them. It prevents absurd candidates from the tail."
        ),
        lesson="predecir-la-siguiente-palabra",
    ),
    GlossaryTerm(
        term="transformer",
        definition=(
            "A neural network architecture introduced in 2017 based on attention, with "
            "encoder and decoder modules. It is the basis of BERT, GPT, and most current LLMs."
        ),
        lesson="transformer-y-atencion",
    ),
    GlossaryTerm(
        term="context window",
        definition=(
            "The maximum number of tokens the model can process at once. Anything outside it "
            "is no longer available for prediction."
        ),
        lesson="zero-shot-y-few-shot",
    ),
    GlossaryTerm(
        term="zero-shot",
        definition=(
            "Solving a task with only an instruction, without solved examples in the prompt. "
            "The model uses what it learned during pretraining."
        ),
        lesson="zero-shot-y-few-shot",
    ),
)
