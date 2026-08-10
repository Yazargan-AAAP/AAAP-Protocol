AAAP v2.0 Repository Migration Guide
This document records the repository changes required to align the AAAP reference validator, audit log, documentation, tests, and GitHub Actions.
Migration objective
The repository should provide one consistent verification path:
audit-log-2026-07-13.json
        ↓
validator.py
        ↓
PASS / FAIL
        ↓
GitHub Actions
        ↓
AAAP CI Pipeline
The validator verifies record integrity and structure. It does not determine the substantive truth of an allegation or legal claim.
Files to update
The following files form the reference implementation:
validator.py
audit-log-2026-07-13.json
README.md
MIGRATION.md
tests/test_validator.py
.github/workflows/main.yml
1. Replace validator.py
Replace the previous validator implementation with the AAAP v2.0 reference validator.
It provides:
command-line operation
--audit-log input
--input alias
AAAP document validation
event schema validation
UTC timestamp validation
chronology validation
duplicate event-ID detection
SHA-256 event-data verification
previous-hash chain verification
process exit code 0 for PASS and 1 for FAIL
Run locally:
python3 validator.py --audit-log audit-log-2026-07-13.json
Expected result:
PASS: AAAP v2.0 verified (1 event(s))
2. Replace the reference audit log
Use the AAAP v2.0 structure in:
audit-log-2026-07-13.json
The document contains protocol metadata and an events array.
The first event uses a zero SHA-256 hash as its previous_hash. Its data_hash is calculated from the canonical JSON representation of its data object.
3. Replace README.md
The README should describe the same command, data model, evidence discipline, tests, and GitHub Actions workflow used by the implementation.
Avoid documenting commands or file paths that are not present in the repository.
4. Add regression tests
The test suite is:
tests/test_validator.py
Run it locally:
python3 -m unittest discover -s tests -v
The tests verify that:
the reference audit log passes;
tampering with event data causes validation to fail.
5. Add the GitHub Actions workflow
GitHub Actions requires the workflow to be under:
.github/workflows/main.yml
The workflow should:
check out the repository;
install Python 3.12;
run the AAAP validator;
run the regression tests.
The previous root-level workflows directory is not the canonical GitHub Actions location and should not be relied upon.
6. Post-migration verification
After committing the files, verify the repository tree:
AAAP-Protocol/
├── .github/
│   └── workflows/
│       └── main.yml
├── tests/
│   └── test_validator.py
├── audit-log-2026-07-13.json
├── validator.py
├── README.md
├── MIGRATION.md
└── LICENSE
Then open:
GitHub → Actions → AAAP CI Pipeline
A successful run should show all workflow steps as green.
Important integrity note
Migration changes the implementation and verification structure. It should not be interpreted as proof that the underlying factual, legal, regulatory, or forensic assertions in an audit record are true.
AAAP's role is to make the supplied record:
structured
reproducible
chronologically traceable
hash-verifiable
explicit about evidence versus analysis
Substantive conclusions remain subject to independent review.
Rollback
If a migration causes unexpected behavior, restore the previous commit rather than manually mixing old and new validator, audit-log, and workflow formats.
The validator, audit log, README, tests, and workflow should be treated as one coherent reference implementation.
