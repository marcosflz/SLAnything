"""Lesson 1 · What is an LLM?"""

from webapp.content.schema import (
    Lesson,
    callout,
    check,
    figure,
    h2,
    keypoints,
    lab,
    lead,
    p,
    py,
    quote,
    table,
)

LESSON = Lesson(
    number=1,
    slug="que-es-un-llm",
    title="What is an LLM?",
    summary=(
        "A language model is a neural network trained to predict the next token. "
        "Here we unpack what “large” means and where this technology comes from."
    ),
    minutes=10,
    objectives=(
        "Define what a large language model is without resorting to magic.",
        "Explain the two dimensions of “large”: parameters and data.",
        "Place LLMs inside the hierarchy of artificial intelligence.",
        "Estimate the memory a model takes according to its precision.",
    ),
    blocks=(
        lead(
            "Before defining anything, let's do what a language model does. Read this "
            "sentence and complete the ending in your head: <em>“The sun was setting "
            "behind the mountains and the sky turned…”</em>."
        ),
        p(
            "You probably thought of <strong>orange</strong>, <strong>red</strong>, or "
            "<strong>purple</strong>. You did not apply an explicit rule: your experience "
            "with language produced a distribution of plausible endings. That is, in "
            "essence, the engine of an LLM."
        ),
        callout(
            "info",
            "The central idea of the chapter",
            "An LLM is an enormous neural network trained to <strong>predict the next "
            "token</strong>. Translation, summarization, programming, and conversation "
            "emerge from that task and from scale.",
        ),
        h2("A useful definition"),
        p(
            "A <strong>large language model</strong> is a deep neural network trained on "
            "massive amounts of text to <strong>understand, generate, and respond to</strong> "
            "human language. When we say it “understands”, we mean it processes and generates "
            "text coherently and in context; not that it has consciousness or human "
            "comprehension."
        ),
        p(
            "The word “large” refers to two things at once: the <strong>parameters</strong> "
            "—the adjustable weights of the network— and the <strong>data</strong> used to "
            "train it. A model with many parameters but little data does not learn well; "
            "one with lots of data but little capacity does not either."
        ),
        table(
            ["Dimension", "What it means", "Example"],
            [
                ["<strong>Parameters</strong>", "Adjustable weights of the network", "GPT-3: 175 billion"],
                ["<strong>Data</strong>", "Training corpus", "GPT-3: ~300 billion tokens"],
            ],
            caption="The two dimensions of “large”.",
        ),
        h2("The AI hierarchy"),
        p(
            "LLMs are not a separate field: they are a concrete application of deep "
            "learning. Figure 1.1 of the book places AI, machine learning, deep learning, "
            "generative AI, and LLMs in successive layers."
        ),
        figure(
            "img/ch01/fig_1_1_jerarquia_ia.png",
            "Hierarchy diagram: artificial intelligence, machine learning, deep learning, generative AI, and LLMs.",
            "AI is the umbrella; machine learning is algorithms that learn from data; "
            "deep learning uses multi-layer networks; GenAI creates new content; LLMs "
            "are a particular case focused on text.",
            credit="Figure 1.1 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
            wide=True,
        ),
        p(
            "The practical difference between traditional machine learning and deep "
            "learning lies in the features. In traditional ML, a person designs the "
            "relevant variables by hand: frequency of “free”, number of exclamation marks, "
            "capital letters. In deep learning, the network learns those representations "
            "from the data."
        ),
        h2("Language as an interface"),
        p(
            "The reason LLMs spread so quickly is that <strong>language is the interface "
            "of almost everything</strong>. If a task can be phrased as “read text and "
            "produce text”, a model can attempt it without changing its architecture. "
            "Figure 1.2 shows the conversational interface: the user writes an instruction "
            "and the model produces a response."
        ),
        figure(
            "img/ch01/fig_1_2_chatgpt.png",
            "ChatGPT conversational interface: the user writes an instruction and the model responds.",
            "The interface is simple; the responsibility lies in the model and in how its "
            "response is used. Fluent output is not the same as true output.",
            credit="Figure 1.2 · Raschka, Build a Large Language Model (From Scratch), Manning, 2024.",
        ),
        table(
            ["Task", "Input", "Output", "Example"],
            [
                ["Translation", "Text in one language", "Text in another", "“Good morning” → “Buenos días”"],
                ["Summarization", "Long document", "Short version", "Summary of a contract"],
                ["Sentiment", "Review", "Label", "Positive / negative / neutral"],
                ["Generation", "Instruction or start", "New text", "Article, story, code"],
                ["Question answering", "Question + context", "Answer", "Technical support"],
                ["Assistants", "Conversation", "Response", "ChatGPT, Gemini, Copilot"],
            ],
            caption="Typical applications. The same architecture, different instructions.",
        ),
        callout(
            "tip",
            "The idea to take away",
            "The same base model can translate, summarize, or classify <strong>without "
            "retraining</strong>: just change the prompt. That works because pretraining "
            "taught it general language patterns, not a single task.",
        ),
        check(
            "Why can the same model translate and summarize without retraining?",
            "Because pretraining gave it general language patterns and the task is "
            "expressed as input text → output text. The instruction in the prompt selects "
            "the behaviour; the weights do not need to change.",
        ),
        h2("Scale has a price"),
        p(
            "Every parameter takes memory. In 16-bit inference, a model needs approximately "
            "<strong>2 bytes per parameter</strong> just for the weights. GPT-3, with 175 "
            "billion parameters, takes about <strong>350 GB</strong> before counting "
            "activations and cache. Training is even more expensive: gradients and optimizer "
            "states must also be stored."
        ),
        table(
            ["Model", "Parameters", "16-bit weights", "8-bit weights", "4-bit weights", "Approx. training"],
            [
                ["GPT-2 small (the book's model)", "124 M", "0.25 GB", "0.12 GB", "0.06 GB", "2 GB"],
                ["GPT-2 XL", "1.5 B", "3 GB", "1.5 GB", "0.75 GB", "24 GB"],
                ["Llama 3.1 8B", "8 B", "16 GB", "8 GB", "4 GB", "128 GB"],
                ["Llama 3.1 70B", "70 B", "140 GB", "70 GB", "35 GB", "1.1 TB"],
                ["GPT-3", "175 B", "350 GB", "175 GB", "87.5 GB", "2.8 TB"],
            ],
            caption="Orders of magnitude, not exact measurements.",
            note=(
                "2 bytes per parameter at 16 bits, 1 at 8 bits, and 0.5 at 4 bits. "
                "Training is estimated at about 16 bytes per parameter (fp32 weights, "
                "gradients, and Adam states). Activations and cache add more memory."
            ),
        ),
        lab("memory"),
        py(
            """
MODELS = {
    "GPT-2 small (124 M)": 124e6,
    "GPT-2 XL (1.5 B)": 1.5e9,
    "Llama 3.1 8B": 8e9,
    "GPT-3 (175 B)": 175e9,
}

def memory_gb(parameters, bytes_per_parameter):
    return parameters * bytes_per_parameter / 1e9

print(f"{'Model':24} {'16-bit':>9} {'8-bit':>9} {'4-bit':>9}")
print("-" * 56)
for name, parameters in MODELS.items():
    print(
        f"{name:24} "
        f"{memory_gb(parameters, 2):>7.1f} GB "
        f"{memory_gb(parameters, 1):>7.1f} GB "
        f"{memory_gb(parameters, 0.5):>7.1f} GB"
    )
""",
            caption=(
                "Compute the memory used by the weights at each precision. Change "
                "the models or add your own and run it again."
            ),
        ),
        callout(
            "tip",
            "Before moving on · 30 seconds",
            "Why do you think predicting the next word can teach grammar or reasoning? "
            "Keep your hypothesis; we will revisit it at the end of the chapter.",
        ),
        check(
            "What two things does the “large” in large language model measure?",
            "The number of parameters (the network's capacity) and the amount and "
            "diversity of training data. Neither is enough on its own.",
        ),
        quote(
            "An LLM does not return a single word: it returns a probability for every "
            "possible token and picks one.",
            "An idea we develop in lesson 5",
        ),
        keypoints(
            [
                "An LLM is a neural network trained to predict the next token.",
                "“Large” means many parameters and lots of data, not just one thing.",
                "LLMs are deep learning applied to language, not a separate field.",
                "Scale has a direct cost in memory and compute.",
            ]
        ),
    ),
    key_points=(
        "An LLM is a neural network trained to predict the next token.",
        "“Large” means many parameters and lots of data.",
        "LLMs are an application of deep learning, not a separate field.",
        "Scale is paid for in memory and compute.",
    ),
)
