# Question Classification & Perspective Routing

Classify the user's question to determine which perspectives are most relevant. The User Advocate 🫂 is **always first** unless explicitly excluded.

## Routing Table

| Category                         | Signal Words                                                                                                                  | Relevance Order (after Advocate)                                   |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| **Architecture / System Design** | structure, API, schema, microservice, monolith, database, layer, boundary, coupling, dependency, module, decompose            | Architect → Skeptic → Pragmatist → Temporal → Innovator            |
| **Visual / UI Design**           | UI, layout, typography, color, spacing, landing page, hero, brand, aesthetic, visual, design system, component, mockup, style | Craft Critic → Brand Guardian → Innovator → Pragmatist → Architect |
| **Strategy / Direction**         | roadmap, pivot, long-term, vision, differentiate, market, strategy, compete, bet, invest, direction, north star               | Architect → Innovator → Temporal → Skeptic → Pragmatist            |
| **User / Developer Experience**  | UX, DX, onboarding, friction, API ergonomics, developer experience, documentation, error message, discoverability, naming     | Skeptic → Pragmatist → Craft Critic → Innovator → Temporal         |
| **Risk Assessment**              | risk, vulnerability, worst case, failure, what could go wrong, security, incident, outage, postmortem, blast radius           | Skeptic → Temporal → Architect → Pragmatist → Innovator            |
| **Innovation / Ideation**        | what if, brainstorm, rethink, reimagine, alternative approach, new way, creative, unconventional, disrupt, invert             | Innovator → Craft Critic → Architect → Skeptic → Temporal          |
| **Planning / Execution**         | timeline, milestone, sprint, ship, sequence, implement, rollout, migration, phase, deploy, release, schedule                  | Temporal → Pragmatist → Architect → Skeptic → Innovator            |
| **General / Unknown**            | _(no clear signal match)_                                                                                                     | Architect → Skeptic → Pragmatist → Innovator → Temporal            |

## Classification Procedure

1. **Scan** the user's question for signal words from the table above
2. **Match** to the category with the most signal hits; on ties, prefer the category listed earlier
3. **Compose council** by taking the User Advocate first, then filling remaining seats from the relevance order for that category
4. **Adjust** for explicit `--include` / `--exclude` flags

## Council Size Selection

| Flag                    | Size | Composition                            |
| ----------------------- | ---- | -------------------------------------- |
| `--quick`               | 2    | User Advocate + top-1 from routing     |
| `--council` _(default)_ | 3    | User Advocate + top-2 from routing     |
| `--council N`           | N    | User Advocate + top-(N-1) from routing |
| `--full`                | 8    | All perspectives                       |

## Edge Cases

- **Multiple categories match equally:** Use General/Unknown ordering, which provides a balanced default
- **User explicitly provides a category:** Skip signal word matching, use the routing for that category directly
- **`--exclude advocate`:** Drop User Advocate; fill all seats from routing order starting at position 1
- **`--include` a perspective already selected:** No-op (already in council)
- **`--include` pushes size above 8:** Cap at 8, prioritize explicitly included over routing-derived
