# Comparison with Other Datasets

**Table: Comparison of our narrative-grounded synthetic cyberbullying dataset with existing real-world corpora**

| Attribute | Narrative-Grounded (Ours) | Stormfront | Wikipedia Talk | Twitter Classification |
|-----------|---------------------------|------------|----------------|----------------------|
| **Source Type** | LLM-generated, mini-story based | Extremist forum data | Wikipedia comment threads | Public tweets |
| **Interaction Type** | Two-person multi-turn chat | Multi-user threaded posts | Threaded discussions | Single-turn posts |
| **Narrative Context** | Explicit mini-stories | Minimal or absent | Minimal | Absent |
| **Avg. Turns per Conversation** | 6–9 | 2–6 | 1–3 | 1 |
| **Subtype Labels** | 98 labeled subtypes | None | None | 5 categories + control |
| **Escalation Trajectory** | Structured escalation | Partial (ideological shifts) | Rare | Not modeled |
| **Victim-Perpetrator Roles** | Explicit, defined in prompt | Often absent | Weak or unclear | Implicit |
| **Language Register** | Informal, varied tone | Formal/ideological | Polite or vandalistic | Colloquial, sarcastic |
| **Content Moderation** | Curated for safety | Unfiltered | Moderated | Partially filtered |
| **Common Use Cases** | Detection, response generation | Hate speech detection | Toxicity analysis | Classification |