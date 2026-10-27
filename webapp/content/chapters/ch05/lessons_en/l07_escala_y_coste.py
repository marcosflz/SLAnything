"""Lesson 7 · Scale, FLOPs, and cost."""

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
)

LESSON = Lesson(
    number=7,
    slug="escala-y-coste",
    title="Scale, FLOPs, and cost",
    summary=(
        "The 6 · N · D rule estimates pretraining compute; with effective throughput it "
        "becomes GPU-hours, money, and memory requirements."
    ),
    minutes=9,
    objectives=(
        "Apply FLOPs ≈ 6 · N · D to a small model.",
        "Convert FLOPs into GPU-hours using effective throughput.",
        "Estimate memory for weights, gradients, and optimizer states.",
        "Distinguish an order-of-magnitude estimate from a real budget.",
    ),
    blocks=(
        lead(
            "Before launching a training run it is worth knowing whether it fits. You do not "
            "need to wait for the first invoice: parameter count, token count, and hardware "
            "throughput give our own order-of-magnitude estimate. That account avoids two extremes: "
            "underestimating the cost and giving up, or believing a laptop will reproduce GPT-3 "
            "in an afternoon."
        ),
        h2("Six operations per parameter and token"),
        p(
            "The rule <strong>FLOPs ≈ 6 · N · D</strong> summarises the compute of transformer "
            "training. <code>N</code> is the number of parameters and <code>D</code> the number "
            "of tokens processed. The factor 6 approximates the operations per pair: in the "
            "forward pass, one multiply and one add per weight and activation; in the backward "
            "pass, roughly twice that to compute gradients with respect to activations and "
            "weights. It is an approximation, not a measurement: it ignores embeddings, "
            "normalisations, quadratic attention, and memory operations."
        ),
        figure(
            "img/ch05/escala-coste.svg",
            "Diagram with the 6 · N · D formula, the 124-million-parameter example, and a GPU-hour comparison across models.",
            "The same account compares a didactic model with GPT-3. The scale changes by "
            "orders of magnitude, not by a small factor.",
            credit="Diagrama propio de Aula LLM.",
            wide=True,
        ),
        p(
            "For the book's model, with 124 million parameters and 1 billion tokens, the rule "
            "gives 6 × 124 × 10⁶ × 10⁹ = 7.44 × 10¹⁷ FLOPs. If the hardware sustains 40 "
            "effective TFLOPS —40 × 10¹² operations per second— the pure compute time is about "
            "5.2 GPU-hours. That is small compared with large models, and it explains why the "
            "example can run on a laptop in minutes or hours, depending on hardware and "
            "implementation."
        ),
        h2("From FLOPs to GPU-hours and euros"),
        p(
            "A GPU does not deliver its theoretical peak. Effective utilisation depends on "
            "batch size, memory, interconnect, and kernel efficiency. That is why we use "
            "sustained throughput, not the number on the box. The conversion is "
            "<code>GPU-h = FLOPs / (TFLOPS · 10¹² · 3600)</code>. Multiplying by the price per "
            "GPU-hour gives the rental cost; energy, storage, networking, and engineering time "
            "are extra."
        ),
        p(
            "The book cites Llama 2 with 7 billion parameters: 2 trillion tokens and 184,320 "
            "GPU-hours on A100s. At 30 dollars per hour for an 8×A100 server, the rough account "
            "is 184,320 / 8 × 30 ≈ 690,000 dollars. For GPT-3, with 175 billion parameters and "
            "300 billion tokens, the rule gives 3.15 × 10²³ FLOPs, about 2.2 million GPU-hours "
            "at 40 effective TFLOPS. These are orders of magnitude: the real number depends on "
            "infrastructure and timing."
        ),
        h2("Memory: where it goes"),
        p(
            "Compute is not the only limit. In 32-bit training, each parameter needs 4 bytes "
            "for the weight, 4 for its gradient, and 8 for AdamW's two moments: 16 bytes per "
            "parameter. The 124 M model occupies about 1.98 GB in those states alone. Add "
            "activations, batches, buffers, and fragmentation; real memory is larger. Mixed "
            "precision reduces some of these magnitudes, but they do not disappear."
        ),
        p(
            "Activations also count. A single snapshot of one activation per layer, with batch "
            "2, length 256, dimension 768, and 12 layers in fp32, occupies 2 × 256 × 768 × 12 × "
            "4 bytes ≈ 18.9 MB. That sounds small, but the model stores many intermediate "
            "activations for backward, and attention grows with the square of sequence length. "
            "<em>Gradient checkpointing</em> trades memory for compute: it does not store every "
            "activation and recomputes them during backward."
        ),
        callout(
            "warning",
            "An estimate is not a budget",
            "The 6 · N · D rule and 16 bytes per parameter help compare scenarios and rule out "
            "infeasible ideas. They do not predict the final invoice: real utilisation, energy "
            "prices, interruptions, and interconnect change the result. Before reserving "
            "hardware, measure effective throughput with a short run and scale from there."
        ),
        py(
            """
N = 124e6
D = 1e9
flops = 6 * N * D
gpu_hours = flops / (40e12 * 3600)

print(f"Book model FLOPs: {flops:.2e}")
print(f"GPU-hours at 40 TFLOPS: {gpu_hours:.2f}")

N_gpt3 = 175e9
D_gpt3 = 300e9
flops_gpt3 = 6 * N_gpt3 * D_gpt3
gpu_hours_gpt3 = flops_gpt3 / (40e12 * 3600)
print(f"GPT-3 FLOPs: {flops_gpt3:.2e}")
print(f"GPT-3 GPU-hours: {gpu_hours_gpt3:,.0f}")

weight_memory = N * 16 / 1e9
activations = 2 * 256 * 768 * 12 * 4 / 1e6
print(f"Training states: {weight_memory:.2f} GB")
print(f"One activation per layer: {activations:.1f} MB")
""",
            caption=(
                "Compute, GPU-hour, and memory estimates for the book model and GPT-3. "
                "Change N, D, or TFLOPS to explore other scenarios."
            ),
        ),
        lab("cost"),
        p(
            "The training calculator lets you move model, tokens, number of GPUs, price, and "
            "effective throughput. Notice that doubling parameters or tokens doubles FLOPs, "
            "while adding GPUs distributes work but does not reduce total cost if the hourly "
            "price stays the same. The training memory shown by the calculator covers weights, "
            "gradients, and optimizer states; activations are added on top."
        ),
        check(
            "A 1-billion-parameter model is trained on 20 billion tokens. How many FLOPs does "
            "the 6 · N · D rule estimate?",
            "6 × 10⁹ × 2 × 10¹⁰ = 1.2 × 10²⁰ FLOPs. At 40 effective TFLOPS that is "
            "1.2 × 10²⁰ / (40 × 10¹² × 3600) ≈ 833 GPU-hours of pure compute. It is an "
            "order-of-magnitude estimate, before efficiency and overheads."
        ),
        keypoints(
            [
                "FLOPs ≈ 6 · N · D estimates training compute.",
                "The book model needs ≈ 7.44 × 10¹⁷ FLOPs with 1,000 M tokens.",
                "GPU-hours = FLOPs / (effective TFLOPS · 10¹² · 3600).",
                "Llama 2 7B is cited at 184,320 GPU-hours and about 690,000 dollars.",
                "Training with AdamW in fp32 uses about 16 bytes per parameter.",
                "Activations and attention add memory beyond the weights.",
                "Every estimate should be validated with a short, measured run.",
            ]
        ),
    ),
    key_points=(
        "The 6 · N · D rule gives a compute estimate, not a measurement.",
        "Effective throughput converts FLOPs into GPU-hours.",
        "Real cost includes hardware, energy, networking, and engineering time.",
        "AdamW in fp32 needs about 16 bytes per parameter.",
        "Activations and attention constrain batch memory.",
        "Gradient checkpointing trades memory for extra compute.",
    ),
)
