# ClaimCheck — synthetic prototype, stage 1

A small deterministic baseline for checking synthetic deceased-customer deposit claim document sets.

## Important scope notice

All cases and policy rules in this repository are synthetic. The policy is illustrative software-test data, not an actual bank policy, legal checklist, or RBI-prescribed document list. The program does not authenticate documents, determine inheritance rights, approve claims, or authorise payments.

## What is implemented

- Two synthetic claim categories: `nominee` and `no_nominee_uncontested`.
- Required-document checks.
- Duplicate document-type warnings.
- Cross-document comparison of deceased name and date of death.
- Required-field checks for key extracted fields.
- Low OCR-confidence flags when confidence metadata is supplied.
- Three statuses: `CHECKS_PASSED`, `INCOMPLETE`, `REVIEW_REQUIRED`.
- Ten synthetic test cases and automated tests.

## Run

Python 3.10+ is recommended. The baseline uses only the Python standard library at runtime; install `pytest` to run the test suite.

```bash
pytest -q
```

## Next stages

1. Review and strengthen the deterministic rules and test cases.
2. Add OCR over synthetic sample documents.
3. Add structured LLM extraction with schema validation and source evidence.
4. Add a minimal employee review interface.

Do not use real customer data.
