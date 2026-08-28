# Context-Aware Cyberbullying Dialogues — Dataset, Taxonomy, and Review App

Research artifacts for **"Generating Context-Aware Cyberbullying Dialogues: A Structured LLM-Based
Dataset."** This repository contains the synthetic multi-turn cyberbullying dialogue corpus, the subtype
taxonomy that conditioned its generation, and the Streamlit application used for human review.

> **Paper:** M. S. Islam, S. Sutton, and R. I. Rafiq, "Generating Context-Aware Cyberbullying Dialogues: A
> Structured LLM-Based Dataset," *2025 IEEE 12th International Conference on Cyber Security and Cloud
> Computing (CSCloud)*, New York, NY, USA, 2025, pp. 1–6, doi:
> [10.1109/CSCloud66326.2025.00035](https://doi.org/10.1109/CSCloud66326.2025.00035).

---

## Why this dataset exists

Most cyberbullying corpora label isolated messages from public platforms. That framing misses what makes
cyberbullying harmful in private channels: it unfolds across turns, it has stable roles (bully, victim,
bystander), and the harm accumulates rather than appearing in any single message.

This dataset supplies that missing shape — multi-turn, role-consistent, narratively grounded private
conversations, each conditioned on a specific documented subtype of abuse. It is **synthetic by design**,
which is both the point and the principal limitation. See [Limitations](#limitations).

---

## Contents

| File | What it is |
|---|---|
| `cyberbullying_conversations_generated.json` | The dataset — conversations with full metadata and dialogue turns |
| `conversations_id_only.json` | Identifier-only projection of the same conversations, used for blind human review |
| `appendix-subtype-taxonomy.md` | The 98-subtype taxonomy, with operational definitions and supporting literature |
| `app.py` | Streamlit review application (AI-vs-human judgement collection, writes to Google Sheets) |
| `analysis/comparison_with_other_datasets.md` | Comparison against existing public corpora |
| `examples/` | Illustrative excerpts from the public datasets evaluated and rejected during design |
| `requirements.txt` | Python dependencies |

### Record schema

Each entry in `cyberbullying_conversations_generated.json`:

| Field | Description |
|---|---|
| `id` | Conversation identifier |
| `group` | One of five broad behavioural groups |
| `type` | Thematic type (e.g. Harassment, Catfishing) |
| `subtype` | Fine-grained subtype |
| `story` | The narrative mini-story used to ground generation |
| `platform` | Simulated platform context (WhatsApp, Discord, Instagram DM, …) |
| `conversation` | The multi-turn dialogue |

### Dataset statistics

| Measure | Value |
|---|---|
| Conversations | 99 |
| Behavioural groups | 5 |
| Total dialogue turns | 940 |
| Turns per conversation | 7 min / 15 max |

Group distribution: Direct Aggression 30 · Deceptive and Covert Abuse 23 · Social Manipulation and
Exclusion 19 · Visual and Multimodal Abuse 17 · Psychological Coercion & Threat 10.

Generation used **Claude 3.7 Sonnet**, conditioned on a mini-story and an assigned subtype. All
conversations were manually reviewed and filtered for coherence, ethical safety, and fidelity to the
assigned subtype before inclusion.

**Note on the evaluation benchmark.** The learnability experiment in the paper used 174 conversations: the
99 synthetic dialogues here plus 75 safe conversations from a public Kaggle corpus. That third-party
material is not redistributed in this repository.

---

## Running the review application

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app presents conversations for blind AI-vs-human judgement and writes responses to a Google Sheet. It
expects two Streamlit secrets, which are **not** included in this repository:

```toml
# .streamlit/secrets.toml
GCP_SERVICE_ACCOUNT = '{ ...service account JSON... }'
GOOGLE_SHEET_ID = "your-sheet-id"
```

Without these the app reports a connection error and collects no responses. The dataset files can be used
independently of the app.

---

## Limitations

The dialogues are synthetic — LLM-generated and human-filtered, not observed — so they do not capture the
slang density and emotional rawness of real abuse, and may carry artifacts of the generating model. All
dialogues come from a single model. At 99 conversations the corpus is small for training robust
classifiers.

Treat this as a controlled environment for studying escalation, subtype-specific patterns, and
intervention, **not** as a benchmark for classifier quality. The paper reports and discusses this directly.

---

## Ethical use

This repository contains simulated abusive language depicting harassment, coercion, and threats. It is
released for **research on detecting and mitigating online harm**.

- No real individuals, real conversations, or personal data are included. All names and scenarios are
  invented.
- Do not use these artifacts to generate, target, or refine abusive content against any person.
- Content is distressing in places. Consider this before use in classroom or crowdsourced settings.
- Validate anything built on this data against real-world data before deployment affecting real users.
  Nothing here is validated for deployment.

---

## Citation

```bibtex
@inproceedings{islam2025cyberbullying,
  author    = {Islam, Mohammad Shafiqul and Sutton, Sara and Rafiq, Rahat Ibn},
  title     = {Generating Context-Aware Cyberbullying Dialogues: A Structured {LLM}-Based Dataset},
  booktitle = {2025 IEEE 12th International Conference on Cyber Security and Cloud Computing (CSCloud)},
  year      = {2025},
  pages     = {1--6},
  address   = {New York, NY, USA},
  publisher = {IEEE},
  doi       = {10.1109/CSCloud66326.2025.00035}
}
```

## Contact

Mohammad Shafiqul Islam — [Google Scholar](https://scholar.google.com/citations?user=GBlNBacAAAAJ) ·
[GitHub](https://github.com/anikgvsu)
