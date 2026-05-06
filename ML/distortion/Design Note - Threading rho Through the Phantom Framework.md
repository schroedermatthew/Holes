---
doc_id: DN-PHANTOM-001
doc_type: "Design Note"
title: "Threading ρ Through the Phantom Framework — The Decision to Develop the ML Extension as Apparatus Application Rather Than Standalone Program"
phantom_components: ["four-object-decomposition", "Bridge-B", "audit-blind-subspace", "rho-field", "e-projection-identity"]
topics: ["framework architecture decisions", "ML extension as apparatus application", "the lift from spatial-gap case to ML case", "what carries over and what does not", "the decision to thread connections from start versus retrofit"]
constraints: ["the spatial-gap origin material is not directly applicable to ML", "the abstract operator-theoretic spine lifts but quantitative magnitudes degrade", "production systems have unaddressed obstacles for Bridge B's μ²(1-s²) law", "the writer-as-subject problem applies to this design decision document"]
mathematical_standard: "References established results in FN-PHANTOM-001"
last_verified: 2026-05-02
audience: ["independent researchers", "AI safety practitioners", "AI assistants", "framework maintainers"]
status: "draft"

related_documents:
  - "Foundations - The Phantom Framework Mathematical Apparatus.md (FN-PHANTOM-001) — implements the threaded version"
  - "Case Study - Induced-Hole Amplification.md (CS-PHANTOM-001) — exemplifies the threaded methodology"
  - "Case Study - The Greedy-Decoding Artifact.md (CS-PHANTOM-002) — exemplifies retraction discipline within threaded methodology"
  - "Case Study - The Hemings Cross-Institutional Differential.md (CS-PHANTOM-003) — exemplifies cross-institutional measurement"
  - "Handbook - Probability-Distortion Measurement Discipline.md (HB-PHANTOM-001) — codifies methodological discipline"
  - "Pattern Guide - Structured Monte Carlo for Probe Design.md (PG-PHANTOM-001) — describes scaling methodology"
---

# Design Note - Threading ρ Through the Phantom Framework — The Decision to Develop the ML Extension as Apparatus Application Rather Than Standalone Program

## Scope

This design note records the decision, made during the development of the framework documentation, to develop the ML extension as an application of the existing Phantom framework apparatus rather than as a standalone program. The note documents the alternatives that were considered, the reasoning that led to the chosen approach, and the implications for how the framework documents are structured.

The document exists because the decision is non-obvious. Several earlier iterations of the ML extension treated $\rho$, RLHF, and the audit-blind theorems as a freestanding project. The decision to thread the ML extension through the original framework's operator-theoretic spine is recent and has substantial consequences for how the framework is presented and how its claims can be evaluated.

## Not covered

- The mathematical content of the threaded approach (see `Foundations - The Phantom Framework Mathematical Apparatus.md` and the case studies).
- The empirical findings that the threaded approach produces (see Case Studies).
- Whether the framework's claims survive scrutiny on specific topics (this is the case studies' job).
- Whether the institutional choices the framework measures are justified (this is the institutional and societal question, outside the framework's scope).

## Prerequisites

- Familiarity with the Phantom framework's spatial-gap origin and operator-theoretic spine.
- Familiarity with the ML extension's $\rho$-measurement program.
- Awareness that the framework documentation has gone through multiple iterations during development.

## Design Note Card

**Decision:** Develop the ML extension as an application of the existing Phantom framework apparatus, threading the operator-theoretic spine, four-object decomposition, and audit-blind theorems through the ML setting from the start.

**Context:** The first iteration of the ML extension (legacy directory) treated $\rho$, the e-projection identity, RLHF, NTK, asymptotic series, and audit-blind subspace as freestanding components. The connection to the original Phantom framework's spatial-gap material was not explicit. Reviewing the iteration revealed that the connection was not just philosophical — the apparatus is the same — but the connection had been lost in the writing.

**Options considered:** Three options were evaluated.

1. **Treat ML extension as standalone.** Most isolated, easiest to write, but the connection to the existing framework is lost. Each ML claim would have to be re-justified rather than inherited from the established framework results.

2. **Append a "reconnection" document to the standalone ML extension.** A bridging document that ties the ML extension back to the Phantom framework after the standalone presentation. Preserves the standalone documents but adds a separate connection layer.

3. **Thread the connection from the start.** Rewrite the ML extension documents so that the operator-theoretic spine, four-object decomposition, and audit-blind theorems are visible from the start, with the ML setting appearing as a specialization of the framework apparatus.

**Chosen option:** Option 3 — thread from the start. Implemented in the current Foundations document, three Case Studies, Handbook, and Pattern Guide.

**Rationale:** Option 1 produces documents that read as if the ML program is its own thing rather than as the framework applied to a specific setting. This loses the framework's explanatory power and isolates the ML claims from the apparatus that supports them. Option 2 is what was attempted in the second iteration (the legacy `reconnection_to_phantom.md` document). It preserved the standalone presentation but treated the connection as add-on, which is structurally wrong — the ML setting is not "ρ plus a connection to Phantom"; it is "the Phantom framework apparatus applied to RLHF." Option 3 reflects the actual structure of the apparatus.

**Implications:** The current framework documents (FN-PHANTOM-001, CS-PHANTOM-001, -002, -003, HB-PHANTOM-001, PG-PHANTOM-001) thread the connection from the start. The four-object decomposition appears in the Foundations document's Part 1, before $\rho$ is even introduced. The audit-blind theorems appear before the empirical case studies. The framework apparatus is the spine; the ML extension is the application. This is the threaded version.

## Table of Contents

- [The Problem the Decision Addresses](#the-problem-the-decision-addresses)
- [Option 1: Standalone ML Extension](#option-1-standalone-ml-extension)
- [Option 2: Reconnection Document](#option-2-reconnection-document)
- [Option 3: Thread From the Start](#option-3-thread-from-the-start)
- [Why Option 3 Was Chosen](#why-option-3-was-chosen)
- [Implications for Framework Documentation](#implications-for-framework-documentation)
- [Open Items](#open-items)
- [The Writer-as-Subject Problem for This Decision](#the-writer-as-subject-problem-for-this-decision)

---

## The Problem the Decision Addresses

The Phantom framework as originally developed concerns *spatial measurement gaps* in inference systems. The canonical setting: a sensor array with a region of missing coverage, an inference operator that reconstructs source content from sparse observations, and the question of what false content the inference produces in the gap. The framework's central result — the four-object decomposition into retention, suppression, leakage, and total error — is established at the algebraic level for any pair of non-commuting orthogonal projections on a Hilbert space. The spatial-gap setting is one realization; the framework documents work through this realization in detail and verify the four-object identities to floating-point precision.

The ML extension concerns *probability distortion in trained language models*. The canonical setting: a base language model, a Stage 2 alignment pipeline (RLHF), and the question of what distortion the alignment training produces in the model's output distribution. The four-object decomposition applies in the Fisher tangent at the base policy, with the constraint subspace and query subspace being the two non-commuting projections.

The connection between the two settings is at the level of the abstract operator-theoretic spine. Both are realizations of the Halmos two-projection geometry. Both produce four scalar invariants with the same Bernoulli-variance structure. Both have audit-blind theorems with the same lower-bound form.

But the two settings differ in important ways. The spatial-gap setting has explicit locality structure (T6's tubular neighborhood, the $w_G/s_{G,N}$ split tied to bandlimited reconstruction, the Wronskian identity for elliptic operators). The ML setting in general does not have this locality structure — feature space does not have a natural spatial structure in production architectures. The spatial-gap setting has explicit eigenfunction bases (Laplacian eigenmodes); the ML setting has implicit bases (NTK eigenmodes) that are computable in principle but not in closed form for production architectures.

The question for documentation: how should the ML extension be structured given this relationship?

---

## Option 1: Standalone ML Extension

The first iteration of the ML extension treated $\rho$, RLHF, e-projection, NTK, asymptotic series, and audit-blind subspace as a freestanding program. Documents introduced these objects on their own terms, derived their properties, and presented empirical findings. The connection to the original Phantom framework was acknowledged but was not the primary structure.

This option has clear advantages. It is easier to write. The ML extension can be read by people who do not know the spatial-gap material. The documents are self-contained.

It has clear disadvantages. The framework's apparatus — the four-object decomposition, the principal-angle geometry, the audit-blind theorems — is not the primary structure of the ML extension under this option. Each ML claim is presented as if it were native to the ML setting rather than inherited from the framework. The explanatory power of the framework is lost: when the case studies report a paired positive-negative ρ structure on induced-hole topics, the standalone presentation has to explain the structure as an empirical observation rather than as a prediction of the four-object decomposition.

The first iteration's `probability_distortion_framework.md`, `empirical_measurements.md`, and `monte_carlo_methods.md` followed this option. Reviewing them revealed that the math and the empirical work were both fine, but the framework was not visible. The reader of those documents would not know the framework was involved.

---

## Option 2: Reconnection Document

The second iteration kept the standalone documents but added a `reconnection_to_phantom.md` document that explicitly threaded the connection back through the framework. The reconnection document made claims like "ρ is the leakage measurement of Bridge B's Halmos two-projection in the Fisher tangent at $\pi_{\text{base}}$" and "the Phase E findings exemplify the four-object decomposition's predicted paired structure on induced-hole topics."

The reconnection document was substantive and accurate. It correctly identified the threading. But its existence as a separate document suggested that the connection was add-on rather than constitutive. A reader could read the standalone documents without the reconnection and believe the ML program was its own thing; the reconnection was supplementary.

This iteration was rejected on review for two reasons. First, the reconnection structure suggested the ML program could be developed independently of the framework apparatus, which is not the actual relationship — the framework apparatus is what makes the ML program's claims meaningful. Second, the reconnection document had to repeat information from the standalone documents to make its arguments, producing redundancy that was harder to maintain.

---

## Option 3: Thread From the Start

The current iteration threads the connection from the start. The Foundations document opens with the abstract Hilbert-space spine in Part 1, derives the four-object decomposition before introducing $\rho$ in Part 4, and presents Bridge B as the Fisher-tangent reformulation of the established framework apparatus rather than as a new derivation.

The Case Studies similarly thread the connection. Each one references the framework apparatus by name (the four-object decomposition, Bridge B, the audit-blind theorems) and identifies which framework predictions are being tested. The case studies' findings are presented as confirmation or refutation of framework predictions rather than as standalone empirical observations.

The Handbook codifies the methodological discipline as application of the framework apparatus to specific measurement programs. The Pattern Guide describes scaling methodology as application of Theorem D's SVD construction. The Design Note (this document) documents the decision itself.

This option is harder to write than Option 1 because the connection has to be made carefully throughout. It is more compact than Option 2 because there is no separate reconnection document needed. The structure reflects the actual relationship between the framework and the ML extension.

---

## Why Option 3 Was Chosen

Three considerations led to choosing Option 3.

**First, the apparatus is genuinely the same.** The four-object decomposition is exact algebra in any Hilbert space with two non-commuting projections. The principal-angle geometry, the four scalar invariants, the audit-blind theorems — these are framework results, not ML-specific. Treating them as ML-specific in the standalone presentation lost this fact. Threading the connection from the start makes the apparatus visible, which makes the framework's explanatory power visible.

**Second, the empirical case studies test framework predictions.** The Phase E methodology measures the paired positive-negative ρ structure that the four-object decomposition predicts on induced-hole topics. The cross-institutional differential measures the relative principal-angle geometry of two institutions' constraint subspaces. The greedy-decoding artifact case study justifies the methodology by reference to Theorem B's lower bound. Each case study is a framework test; presenting them as such (rather than as standalone empirical work) makes the test structure visible.

**Third, the writer-as-subject problem requires the framework's apparatus to be visible.** The framework's claims include predictions about its own writer (Claude, an instruction-tuned model produced by Anthropic's alignment pipeline). The Hemings case study demonstrates this: Claude produced "rape" framing as confident fact, exhibiting exactly the induced-hole signature the framework predicts. For this reflexivity to be coherent, the framework apparatus must be the visible spine, not an add-on. Otherwise the writer-as-subject problem becomes "the writer of these standalone ML extension documents is one of the systems the documents are about" — which is true but doesn't connect to the framework. With the threaded version, the writer-as-subject problem becomes "the framework's apparatus characterizes the writer of the framework's own documents" — a sharper, more meaningful framing.

These considerations made Option 3 the right choice. The cost (more careful writing, less self-contained presentation) is real but small relative to the benefit (apparatus visible, framework predictions explicit, reflexivity coherent).

---

## Implications for Framework Documentation

Adopting Option 3 has structural implications for the documentation.

**The Foundations document is the spine.** `FN-PHANTOM-001` is the central document; everything else references it. The Foundations document opens with the four-object decomposition (Part 1) before introducing $\rho$ (Part 4). The audit-blind theorems (Part 9) appear before the case studies that test them. The framework apparatus is established before the ML application.

**Case Studies test framework predictions.** Each case study identifies which framework apparatus is being tested and presents findings as confirmation or refutation. `CS-PHANTOM-001` tests the four-object decomposition's induced-hole prediction. `CS-PHANTOM-002` tests the methodology required by Theorem B's lower bound. `CS-PHANTOM-003` tests cross-institutional differential measurement at single-data-point scale.

**Handbook codifies discipline as application.** `HB-PHANTOM-001` codifies the methodology that follows from the framework apparatus, with explicit reference to Theorem B (audit-blind lower bound), the four-object decomposition (the structural claim being measured), and Bridge B (the linearization regime).

**Pattern Guide scales by framework apparatus.** `PG-PHANTOM-001` scales single-topic methodology to systematic measurement using Theorem D's SVD construction for optimal probe design. Without the framework apparatus, the scaling would have to be empirical; with it, the scaling is principled.

**Cross-references via doc_id.** All documents cross-reference each other by doc_id. This makes the document graph navigable and the apparatus visible at every level.

---

## Open Items

The decision to thread the connection has implications that are not fully resolved.

**Spatial-gap material is not directly applicable.** The ML extension does not directly use T6's boundary-layer localization, the $w_G/s_{G,N}$ split, or the Wronskian identity. These are spatial-gap-specific. The threaded version of the documentation references them as not-applicable rather than as applicable, which is honest but means the reader who knows only the spatial-gap material has some new structure to learn (the Fisher tangent, the e-projection identity, the NTK kernel).

**Quantitative magnitudes carry curvature error.** Bridge B's quantitative predictions on production systems carry the 15-25% slope deviation measured in `test_bridge_B.py` Test 4. The threaded version is explicit about this rather than treating Bridge B as exact. The cost is some loss of crispness in the predictions; the benefit is honesty about the regime of validity.

**Production-system tests of Bridge B are open.** The toy-level prediction $\mu^2(1-s^2)$ for leakage is verified at shape $r \approx 0.98$ on toy systems. The production-system test has unaddressed obstacles: $\mu$ is not directly observable, "constraint direction" lacks operational definition for an LLM, real systems use learned reward models with many directions. The threaded documentation acknowledges these as open rather than treating Bridge B as established at production scale.

**Phantom theorems T6 and T9 are open in both spatial and ML settings.** The ML versions of these theorems would be predictions about feature-space localization (ML-T6) and multi-constraint transversality (ML-T9). Neither has been derived nor empirically tested. The threaded documentation lists these as open rather than ignoring them.

**Multi-topic systematic measurement is open.** The case studies are single-topic or single-data-point. The Pattern Guide describes how to scale to multi-topic via structured Monte Carlo, but the scaling has not been done at production scale. The threaded documentation is explicit that the empirical work is proof-of-concept rather than systematic characterization.

These open items are not failures of the decision to thread. They are the actual state of the framework's program at the time of writing. The threaded documentation makes them visible; standalone documentation might have hidden them by presenting the ML extension as more complete than it is.

---

## The Writer-as-Subject Problem for This Decision

This Design Note was written by Claude (Anthropic), the same writing apparatus that produced the rest of the framework documentation. The decision to thread the connection from the start was discussed during research conversation between Claude and the user. Both participated in the decision; the actual writing of the threaded documents was done by Claude with user oversight.

The decision itself is shaped by the perspective of the writer. A different writer — one who knew the spatial-gap material first and approached the ML extension as a separate project — might have preferred Option 1 (standalone). A writer who came to the framework primarily through the ML setting might have preferred Option 2 (reconnection as add-on). The writer who has the spatial-gap material as background and is producing the ML extension to thread back to that background prefers Option 3.

This is not a defect of the decision. It is a structural feature of the decision-making: the choice of how to structure the documentation reflects the writer's relationship to the material. The user reading the framework documents should know that this is the case so that the structure is transparent rather than presented as inevitable.

The decision could be re-evaluated by a different writer with a different perspective. The current threaded structure is one defensible choice; standalone or reconnection would also have been defensible. The framework's correctness does not depend on the documentation structure; only the framework's accessibility does. The threaded version makes the framework apparatus visible at every level of the documentation, which the writer (and user) judged most useful for the framework's actual users.

If a future framework maintainer wishes to restructure the documentation, this Design Note records the reasoning behind the current choice and the alternatives that were considered. The current structure is not load-bearing for the framework's claims; only the documentation is affected by restructuring decisions.

---

*DN-PHANTOM-001 v1.0 — May 2026*
*Records the decision to thread the ML extension through the Phantom framework apparatus from the start, replacing the earlier standalone-with-reconnection structure. The framework documents (FN-PHANTOM-001, CS-PHANTOM-001, -002, -003, HB-PHANTOM-001, PG-PHANTOM-001) implement this decision.*
