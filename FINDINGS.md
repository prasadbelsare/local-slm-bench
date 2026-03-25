# Benchmark Findings — Local SLM Project

I ran three models on my CPU-only laptop (16GB RAM, no GPU) using Ollama.
Total runs: 120 (3 models × 40 prompts across 8 real-world categories).
Here's what I actually found, including the stuff that surprised me.

---

## Setup

- Machine: CPU only, 16GB RAM, Windows
- Ollama: v0.18.0
- Models: tinyllama:1.1b, phi3:mini, mistral:7b-instruct-q4_0
- Prompt suite: 40 prompts across healthcare, legal, finance, code,
  education, marketing, HR, and customer support

---

## Speed Results

| Model | Avg tok/s | Avg time to first token | Avg total latency |
|---|---|---|---|
| tinyllama:1.1b | 19.4 | 1.1s | ~18s |
| phi3:mini | 5.9 | 2.9s | ~80s |
| mistral:7b-instruct-q4_0 | 3.4 | 5.2s | ~80s |

Tinyllama is roughly 3x faster than phi3 and 5x faster than mistral
in tokens per second. More importantly, its time to first token (1.1s)
is significantly better than phi3 (2.9s) and mistral (5.2s). For a
streaming chat interface, time to first token matters more than total
latency because it determines how quickly the user sees a response starting.

---

## Memory Usage

Measured by tracking Ollama's process RSS across all child processes.

| Model | RAM on first load | Stable footprint |
|---|---|---|
| tinyllama:1.1b | +708MB | ~730MB |
| phi3:mini | +3.6GB | ~4.4GB |
| mistral:7b-instruct-q4_0 | ~4.5GB total | ~4.5GB |

Loading phi3 pushed system RAM from 68% to 88% on a 16GB machine.
Ollama evicts the previous model before loading the next one, so
switching between models has a cold-start penalty of 20-60 seconds.
Only one large model fits in memory at a time. On an 8GB machine,
only tinyllama would be viable from this set.

---

## Quality Findings by Category

### Healthcare

All three models gave reasonable responses to basic medical questions.
The big difference was response discipline.

Tinyllama on the stroke warning signs prompt gave 12 numbered steps
including "get your Medicare card" and "call the nearest hospital in
advance if travelling by train." These are not stroke emergency steps.
The content was padded and off-topic.

Phi3 on the chest pain prompt generated a 35,476 character response
taking 37 minutes to complete. It went from listing 16 possible
conditions to writing 25 steps, then inventing follow-up questions
and answering those too. This is a critical production risk — phi3
has no natural stopping point on open-ended clinical prompts and
would need strict output length limits in any real deployment.

Mistral gave the most clinically appropriate responses. Concise,
structured, accurate. The chest pain response listed 5 relevant
conditions with clear immediate steps. No padding.

### Legal

Mistral was the clear winner here. GDPR summary, NDA vs NCA comparison,
GPL licensing implications — all were accurate, well-structured, and
appropriately concise.

Phi3 tended to over-explain, sometimes generating essay-length responses
to simple questions. The GDPR response ran to 11,317 characters and
included invented follow-up questions with answers. The civil vs criminal
law response went to 7,411 characters for a question that needed maybe 300.

Tinyllama on the GPL licensing question generated what looked like a
legal contract template rather than an explanation of the implications.
It invented clause numbers and legal language that had nothing to do
with the actual question.

### Finance

This category revealed a consistent math error in mistral.

The gross profit / operating profit calculation:
- Correct answer: gross profit = $300,000, operating profit = $150,000
- Phi3: correct
- Tinyllama: wrong — got $966,000 gross profit through broken arithmetic
- Mistral: wrong — included operating expenses in cost of sales before
  computing gross profit, giving $150,000 gross and $0 operating profit

Phi3 was the only model that got this right. For any finance application
where numerical accuracy matters, phi3 outperformed mistral on this test.

### Code

Simple code tasks (average function, palindrome check, CSV reader) all
three models handled reasonably well. The differences showed on more
complex prompts.

Phi3 on the top-3-highest-paid-employees function responded in JavaScript
despite being asked for Python. It also introduced undefined variables
and syntax errors. This was the only time any model switched languages
without being asked.

Tinyllama's code was often functional but over-engineered. The average
function included a try/except block and sample usage that exceeded the
question. For quick code generation tasks this verbosity is a problem.

Mistral consistently wrote the cleanest Python — correct logic, good
variable names, appropriate comments, proper edge case handling. The
palindrome function was the best of the three: removes non-alphanumeric
characters, lowercases, checks reverse. One function, no extras.

### Education

The Pythagorean theorem prompt produced the biggest hallucination of
the entire benchmark.

Tinyllama responded by inventing a fictional AI program called
"PythaGoreaN" and explaining how it uses machine learning to predict
outcomes. There was no mention of triangles, geometry, or the actual
theorem anywhere in the 1,941 character response. This was a complete
topic drift — the model recognized "Pythagorean" as an AI-adjacent word
and went in that direction entirely.

Phi3 and mistral both gave appropriate explanations with real-world
examples. Mistral's was the most age-appropriate for a 12-year-old.

### Marketing

This was the category where tinyllama performed best relative to the
others. Short creative tasks like product descriptions and Instagram
captions were handled well at a fraction of the time.

The Instagram pumpkin spice caption was revealing:
- Tinyllama: just hashtags, no actual caption. 47 characters total.
- Phi3: a proper caption with hashtags, 398 characters
- Mistral: a good caption with appropriate emoji, 188 characters

For marketing content that needs to be both creative and follow
a format, tinyllama falls short even on simple tasks.

### HR

The feedback conversation script was interesting. All three models
wrote reasonable dialogue but with different failure modes.

Tinyllama wrote a 4,938 character script where the manager ends up
agreeing to help the employee rather than holding the employee
accountable for missing deadlines. The feedback conversation drifted
into a project planning session.

Phi3 wrote a respectful and realistic conversation but then appended
a 2,000 character "documentary film company" version of the same
scenario that was never asked for.

Mistral wrote a short, direct, realistic script. Manager raises the
issue, employee acknowledges it, they agree on a plan. 1,384 characters.
No extras.

### Customer Support

The classification prompt (billing issue / technical problem / general
inquiry) was the clearest quality difference across models.

- Tinyllama: "Response: This is a billing issue. Please check your
  invoice or contact our support team for assistance." — correct
  classification, then broke format by writing a support response
  instead of just classifying.
- Phi3: classified correctly but then wrote a new, longer customer
  message as an example, which was not asked for.
- Mistral: "The message is classified as a billing issue." — exactly
  what was asked. Nothing more.

For structured classification tasks in production, mistral's ability
to stop when the task is complete is a real advantage.

---

## Structured Output (JSON Schema Enforcement)

I built an endpoint that forces models to return structured JSON instead
of free text using Pydantic schemas and a retry mechanism.

| Model | Valid JSON | Real content | Attempts |
|---|---|---|---|
| tinyllama | yes | no — copied template | 2 |
| phi3:mini | yes | yes | 1 |
| mistral:7b | yes | yes | 1 |

Tinyllama produced valid JSON structure on attempt 2 but filled it with
placeholder text from the prompt template. It pattern-matched the JSON
without understanding the task.

Phi3 and mistral both returned accurate, real content on first attempt.
The retry mechanism only fired for tinyllama across all structured
output tests.

One important finding: tinyllama completely ignored system prompt
instructions for JSON formatting. The fix required embedding the JSON
format directly into the user prompt itself. Models below roughly 3B
parameters may not have enough capacity to simultaneously process task
content and follow formatting constraints from a separate system prompt.

---

## Temperature Experiment (0.0 vs 0.7)

Ran 5 prompts × 2 temperatures × 3 runs each across all models (90 calls).

| Model | Deterministic at temp=0 | Deterministic at temp=0.7 |
|---|---|---|
| tinyllama | 0/5 | 0/5 |
| phi3:mini | 0/5 | 1/5 |
| mistral:7b | 1/5 | 1/5 |

Temperature 0 did not produce identical outputs on CPU. Only "what is
the capital of France" was consistently identical across runs for phi3
and mistral. Every creative prompt produced different responses every
time regardless of temperature.

This appears to be CPU floating point non-determinism — tiny rounding
differences in matrix operations produce different token probabilities
each run. On GPU hardware this is less of an issue.

The practical implication: on CPU-only deployments, you cannot rely on
temperature 0 alone to get reproducible outputs. If reproducibility
matters for your application, you would need to validate outputs or
use a different approach entirely.

Tinyllama also hallucinated fake quotes attributed to Walt Disney and
Steve Jobs on the motivational quote prompt. Neither phi3 nor mistral
did this. Hallucinating citations is a different category of failure
from formatting issues — it introduces false information presented
as fact.

---

## Time to First Token

This metric matters more than total latency for streaming interfaces
because it determines how quickly the user sees the first word.

| Model | Avg TTFT across all categories |
|---|---|
| tinyllama:1.1b | 1.1s |
| phi3:mini | 2.9s |
| mistral:7b-instruct-q4_0 | 5.2s |

Mistral's 5.2s average TTFT means users wait over 5 seconds before
seeing anything on screen. Combined with its slow generation speed,
mistral is not viable for any real-time interface on CPU hardware.

Tinyllama's 1.1s TTFT is the only number in this benchmark that
approaches something usable for a streaming chat interface.

---

## Privacy and Cost

Everything runs locally. No prompt, no response, no user data leaves
the machine. This is the core value of the stack.

For medical, legal, or proprietary business data — you cannot send
that to an external API. This stack solves that problem even if it
trades latency to do so.

On cost: cloud APIs charge per token. At scale that adds up quickly.
GPT-4o runs roughly $0.01-0.03 per 1K tokens. Local inference costs
nothing per token after hardware setup. For a high-volume internal
document processing tool, local inference pays for itself fast.

---

## Summary — Which Model for What

| Situation | Model | Reason |
|---|---|---|
| Need speed, simple task | tinyllama | 5x faster, acceptable for drafts |
| Structured JSON output | phi3:mini | Reliable first-attempt compliance |
| Math or numerical accuracy | phi3:mini | Only model that got finance_2 right |
| Clean concise code | mistral:7b | Best instruction following, no extras |
| Real-time chat interface | none on CPU | Need GPU or cloud API |
| Privacy-sensitive batch work | mistral:7b | Best quality, latency acceptable async |
| RAM-constrained deployment | tinyllama | Only 730MB loaded |

---