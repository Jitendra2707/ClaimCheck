# ClaimCheck — LLM usage log (concise record)

**Purpose:** This file records representative prompts and the assistance used while developing the assignment. It is a concise summary, **not a complete export or verbatim transcript** of the ChatGPT conversation. If the submission form requires full chat logs, attach the platform's actual conversation export separately.

## Representative prompts from the applicant

1. **Domain research:** “Understand the problem of deceased-customer claims in Indian banks. Research the existing process, RBI guidelines, bank portals, and current digital solutions. Identify what problems still exist for bank employees and claimants.”
   - **AI assistance:** Summarised the claim process, regulatory framework and publicly documented bank portals; distinguished regulatory requirements from operational assumptions.

2. **Problem selection:** “Now identify the biggest problems faced by bank employees and families during deceased-customer claims. Separate verified problems from assumptions. Explain which problems are frequent, costly, or difficult to solve.”
   - **AI assistance:** Compared document verification, no-nominee complexity and claim tracking; highlighted the lack of public national data on frequency and processing cost.

3. **Solution design:** “Help me design a practical solution for the selected problem. Explain the workflow, main features, input data, AI tasks, outputs, and human review. Keep the solution realistic and focused. Discuss alternatives before choosing the final design.”
   - **AI assistance:** Proposed a hybrid OCR/LLM/rules/human-review design and compared rules-only, LLM-only and multi-agent alternatives.

4. **Technical architecture:** “Help me design the technical architecture. Compare LLM, RAG, OCR, deterministic rules, databases, and human review. Decide what should use AI and what must remain rule-based. Explain data flow, security, traceability, and failure handling.”
   - **AI assistance:** Separated probabilistic extraction from deterministic policy checks and human accountability; recommended avoiding unnecessary agents and vector infrastructure in the initial prototype.

5. **Risk review:** “Review the complete solution critically. Identify risks involving incorrect AI outputs, outdated policies, privacy, security, bias, and legal responsibility. Explain human safeguards and compare our design with alternatives we rejected.”
   - **AI assistance:** Identified design risks and reviewed the deterministic prototype for false-pass behaviour, invalid confidence values and unknown document types.

6. **Prototype planning and implementation:** “Help me plan the smallest useful prototype for this assignment. Choose the technology stack, define the core features, data structure, and implementation steps. Use synthetic data only. Do not start coding until we agree on the plan.”
   - **AI assistance:** Recommended a small Python rules-engine baseline and synthetic test fixtures before adding OCR/LLM components.

## What was actually implemented with assistance

- A Python deterministic verification engine and synthetic JSON policy configuration.
- Fourteen hand-authored synthetic claim cases.
- Pytest tests for expected statuses, mismatches, missing fields, unknown document types, invalid confidence metadata and date normalisation.
- A README, proposed architecture diagram and evaluation summary.

## Limitations of this log

- This is not a full transcript and does not reproduce every assistant response.
- No real customer data, bank employee interviews or internal bank systems were used.
- OCR, LLM extraction, RAG, database, authentication and employee UI are not implemented in the current prototype.
