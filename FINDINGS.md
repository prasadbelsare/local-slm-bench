# Benchmark Findings — Local SLM Project

I ran three models on my CPU-only laptop (16GB RAM, no GPU) using Ollama.
Here's what I actually found, including the stuff that surprised me.

---

## Setup

- Machine: CPU only, 16GB RAM, Windows
- Ollama: v0.18.0
- Models tested: tinyllama:1.1b, phi3:mini, mistral:7b-instruct-q4_0
- Test suite: 9 prompts across summarization, reasoning, and code generation

---

## Speed Results

| Model | Avg tokens/sec | Avg latency |
|---|---|---|
| tinyllama:1.1b | 14.87 tok/s | ~14s |
| phi3:mini | 4.91 tok/s | ~37s |
| mistral:7b-instruct-q4_0 | 2.43 tok/s | ~43s |

Tinyllama is roughly 3x faster than phi3 and 6x faster than mistral.
That gap sounds impressive until you look at what tinyllama actually says.

---

## Quality Results — Where It Gets Interesting

### Reasoning tasks

I gave all three models the same three reasoning prompts. Results were stark.

**Trick question:** "A farmer has 17 sheep. All but 9 die. How many left?"
- tinyllama: said "9 sheep left" then immediately said "18 (9+9)" in the
  same response. Contradicted itself.
- phi3: 9. Explained the "all but" phrasing correctly.
- mistral: 9. Clean, clear explanation.

**Math:** "Train travels 60km in 30 min, how far in 2 hours?"
- tinyllama: answered 5.2km. Completely wrong. Showed pages of broken working.
- phi3: 240km. Correct.
- mistral: 120km. Wrong — calculated the speed correctly (120km/h) but
  returned it as the distance instead of multiplying by 2. One step short.

Tinyllama failed every reasoning test. It wasn't close — it was confidently
wrong, which is worse than saying "I don't know."

### The French response

On one prompt, tinyllama responded entirely in French. The prompt was in
English. I didn't ask for French. It just did it.

That's 1 out of 9 prompts failing on something as basic as language
consistency. In a real product that would be a support ticket and a
confused user. I wouldn't have caught this without running a proper
test suite.

### Code generation

All three models wrote working Python for simple tasks. Mistral wrote
the cleanest code with the best comments. Phi3 was decent but had some
hallucinated variable names in one response. Tinyllama was verbose and
over-engineered simple functions.

---

## Structured Output (JSON Schema Enforcement)

I built an endpoint that forces models to return structured JSON instead
of free text. This is important for real applications where you need to
parse and use the model's output programmatically.

**What happened:**

tinyllama ignored the system prompt completely on the first attempt.
It just answered normally like there was no instruction. I had to embed
the JSON format directly inside the prompt itself to get any response
at all. Even then, it copied my example JSON template word for word
instead of filling in real content:
```json
{
  "summary": "Your summary here",
  "key_points": ["Point 1", "Point 2"],
  "word_count": 10
}
```

That's not a structured output — that's a copy-paste.

phi3 and mistral both returned valid, real JSON on the first attempt:
```json
{
  "summary": "Machine learning is a subset of AI that uses algorithms
               to enable computers to improve at tasks with experience.",
  "key_points": ["Involves algorithms", "Statistical models",
                 "Experience-based improvement"],
  "word_count": 42
}
```

**Retry mechanism:**
I built a retry that catches invalid JSON and reprompts with stronger
instructions at temperature 0. It worked — tinyllama's second attempt
always returned valid JSON structure. The content was still wrong but
the structure was valid. phi3 and mistral never needed the retry.

| Model | Valid JSON | Real content | Attempts |
|---|---|---|---|
| tinyllama | yes | no | 2 |
| phi3:mini | yes | yes | 1 |
| mistral:7b | yes | yes | 1 |

---

## Latency Reality Check

Mistral took 65 seconds to respond to one prompt. On a chat interface
that means a user stares at a spinner for over a minute. That's not
a slow app — that's an unusable app for real-time use.

The honest picture on CPU-only hardware:

- tinyllama: fast enough for real-time but too unreliable to trust
- phi3: 30-60 seconds — only viable for background/async tasks
- mistral: 37-65 seconds — same, background only

None of these are suitable for a real-time chat product on CPU.
The right use case for this stack is batch processing, overnight
document analysis, or internal tools where nobody is waiting on
a spinner.

---

## Privacy & Cost

### Privacy
Everything runs locally. No prompt, no response, no user data leaves
the machine. This is the whole point of the stack.

For a medical records tool, a legal document analyzer, or any system
handling sensitive business data — you simply cannot send that data
to OpenAI or Anthropic. This stack solves that problem, even if it
trades speed to do it.

### Cost
Cloud APIs charge per token. At scale that adds up fast:
- GPT-4o: ~$0.01-0.03 per 1K tokens
- Local inference: $0 per token after setup

For a high-volume internal tool processing thousands of documents
per day, local inference pays for itself quickly.

---

## What I'd Actually Use

| Situation | My pick | Why |
|---|---|---|
| Need speed, task is simple | tinyllama | Fastest, acceptable for drafts |
| Need structured JSON output | phi3:mini | Reliable, 2x faster than mistral |
| Need accuracy, batch job | mistral:7b | Best quality, latency doesn't matter |
| Privacy-sensitive data | any of them | Nothing leaves the machine |
| Real-time chat product | none on CPU | Need GPU or cloud API |

---

## What I'd Do Differently

If I ran this again I would:
1. Test on GPU hardware to separate model quality from hardware constraints
2. Expand the prompt suite to 30+ prompts
3. Measure actual RAM usage per model during inference
4. Test quantization levels — Q4 vs Q5 vs Q8 on the same model

The CPU constraint shaped every result here. The quality differences
between models are real but the latency numbers would look very
different on even a mid-range GPU.