Algorithmic Accountability and Audit Protocol (AAAP) v2.0
AAAP is an open, dependency-free protocol for documenting, preserving, and verifying observable algorithmic platform behavior.
Observe → Capture → Timestamp → Classify → Preserve → Notify → Verify
Quick verification
The reference validator can be run directly from the repository root:
python3 validator.py --audit-log audit-log-2026-07-13.json
The --input option is also accepted as an alias:
python3 validator.py --input audit-log-2026-07-13.json
Expected result:
PASS: AAAP v2.0 verified (1 event(s))
A successful validation returns process exit code 0. A failed validation returns exit code 1.
What the validator verifies
The reference validator checks:
required AAAP document and event fields
AAAP protocol metadata
UTC ISO-8601 timestamps
strict event chronology
unique event IDs
SHA-256 hashes of canonical event data
previous-hash chain integrity
The validator verifies the integrity and structure of the supplied record. It does not determine whether an allegation, observation, or legal claim is substantively true.
Audit-log structure
An AAAP v2.0 audit log contains protocol metadata and an events array.
Each event contains, at minimum:
{
  "timestamp": "2026-07-13T06:00:00Z",
  "event_id": "AAAP-2026-07-13-0001",
  "trigger_type": "publication",
  "previous_hash": "<64-character SHA-256>",
  "data": {},
  "data_hash": "<64-character SHA-256>"
}
The first event begins with a zero hash. Each subsequent event must reference the hash of the preceding event's canonical data object.
Evidence discipline
AAAP separates recorded material from interpretation.
A practical evidence matrix is:
Level
Meaning
A
Primary record — official document, decision, or direct record
B
Notice record — submission, notification, delivery, or institutional acknowledgement
C
Independent corroboration — external or independently verifiable development
D
Analysis — hypothesis, commentary, or analytic inference
Level D analysis should not be represented as an A-level primary record.
Repository layout
AAAP-Protocol/
├── .github/
│   └── workflows/
│       └── main.yml
├── tests/
│   └── test_validator.py
├── audit-log-2026-07-13.json
├── validator.py
├── SPECIFICATION-v2.0.md
├── README.md
└── LICENSE
GitHub Actions
The CI workflow is located at:
.github/workflows/main.yml
It runs on pushes and pull requests targeting main and performs:
Python environment setup
AAAP audit-log validation
validator regression tests
The repository should report a green AAAP CI Pipeline check when all validation steps pass.
Local tests
Run the regression test suite with:
python3 -m unittest discover -s tests -v
Design principle
AAAP is intended to make an audit record:
reproducible
inspectable
independently verifiable
chronologically traceable
explicit about the distinction between evidence and analysis
The protocol does not replace legal, regulatory, scientific, or journalistic review. It provides a structured technical record that those processes can independently examine.
License
Apache-2.0
