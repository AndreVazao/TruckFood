# ADR-0006 — Provenance, Trust & Explainable Confidence Model

**Status:** Accepted — Discovery / Foundation
**Date:** 2026-09-26
**Decision:** TruckFood will represent trust as traceable evidence plus an explainable assessment, rather than as a single opaque global score.

## 1. Context

TruckFood combines information from official authorities, commercial/map providers, community observations and TruckFood-derived inference.

For professional truck use, especially road access and restrictions, the system must be able to answer:

- Where did this information come from?
- What exactly does the source support?
- When was it observed or received?
- When was it last validated?
- Is it still temporally applicable?
- Is another source in conflict?
- How precise is the geographic information?
- Why is TruckFood currently presenting this information as confirmed, reported, uncertain or unknown?

The existing product rules establish four provenance classes: Official, Provider, Community and Inference.

## 2. Decision

TruckFood separates four concepts:

1. Source — who or what supplied information.
2. Evidence — the specific fact, observation or external record supporting a claim.
3. Assessment — TruckFood's interpretation of available evidence.
4. Presentation state — how the product communicates the current level of certainty.

A single confidence number is not the canonical representation of trust.

A derived numeric score may be used internally later, but it must never replace the underlying evidence or become the sole explanation shown to drivers.

## 3. Provenance Classes

### Official
Information originating from a competent authority, public body, concessionaire or other formally authoritative source for the relevant fact.

Official does not automatically mean complete or current. Freshness and scope still apply.

### Provider
Information supplied by a contracted or mapping/data provider.

Provider data is subject to the provider's coverage, methodology and licensing terms.

### Community
Information reported or confirmed by drivers or other users.

Community information is evidence and must not automatically become authoritative fact.

### Inference
Information calculated or derived by TruckFood from other evidence.

Inference must retain links to the evidence and rules that produced it.

## 4. Source Record

A Source Record identifies the origin of information.

Conceptual fields:

- id
- provenance class
- source owner
- source name
- source system/type
- source record identifier
- permitted reference/URL where licensing allows
- licence/use-policy reference
- geographic coverage
- known update frequency
- ingestion method
- active/inactive status
- created/updated timestamps

A source record describes the origin; it does not itself prove that every fact from that source is correct.

## 5. Evidence Record

An Evidence Record represents a concrete piece of information received from a source.

Conceptual fields:

- id
- source record
- target entity/fact
- fact type
- value/condition
- observed-at
- received-at
- validated-at
- valid-from
- valid-until
- review-after
- geographic precision
- evidence status
- conflict group/reference where applicable
- created/updated timestamps

Evidence remains attributable to its source.

Historical evidence should not be silently overwritten when a newer observation arrives.

## 6. Evidence Status

Initial conceptual states:

- active
- superseded
- expired
- withdrawn
- conflicting
- invalidated

A superseded or expired evidence record may remain stored for historical/audit purposes.

Invalidated means the evidence itself was determined to be unusable; it must not be silently deleted when historical integrity is relevant.

## 7. Freshness

Freshness is not the same thing as confidence.

TruckFood therefore keeps these timestamps distinct:

- Observed — when the fact was true/reported at the source.
- Received — when TruckFood obtained it.
- Validated — when TruckFood or an authorised process last checked it.
- Review After — when the system should reconsider it.
- Valid From / Until — when the fact itself applies, if known.

No universal expiry duration is established by this ADR. Different fact types require different freshness policies.

## 8. Geographic Precision

Evidence must indicate how precisely it applies geographically.

Conceptual levels:

- exact point
- entrance
- service area
- road segment
- road corridor
- administrative area
- approximate
- unknown

The system must not apply a highly local fact to a larger area merely because the source lacks precision.

## 9. Corroboration and Conflict

Multiple independent evidence records may support the same fact.

TruckFood should preserve:

- supporting evidence;
- contradicting evidence;
- source independence where known;
- timestamps;
- geographic scope;
- resolution state.

A conflict must not be hidden by selecting one source and deleting the other.

Conceptual conflict states:

- none
- supporting
- conflicting
- resolved
- unresolved

When conflict remains unresolved, the product should communicate uncertainty.

## 10. Confidence Model

Confidence is an explainable assessment derived from evidence.

The initial model considers at least:

- source class/quality;
- freshness;
- corroboration;
- contradiction;
- geographic precision;
- historical reliability where measurable;
- validation state;
- temporal applicability.

No fixed universal weighting is frozen in this ADR.

The key rule is:

**Confidence must be explainable from evidence and context.**

The UI should prefer plain-language explanations over unexplained percentages.

## 11. Presentation States

Initial driver-facing conceptual states:

- confirmed
- likely
- reported
- unverified
- conflicting
- expired_needs_review
- unknown

These are communication states, not legal classifications.

Example presentation:

> Reported by drivers 2 hours ago; last official verification unavailable.

rather than an unexplained percentage such as 87%.

Exact wording will be refined through UX testing.

## 12. Assessment

A TruckFood Assessment is a derived interpretation of available evidence.

An assessment should retain:

- target entity/fact;
- evaluation timestamp;
- relevant vehicle/profile context where applicable;
- evidence references;
- rule/version used;
- resulting state;
- explanation/reason codes;
- expiry/review condition.

Assessments must be reproducible enough to explain why the product reached a state at a given time.

## 13. Suitability and Trust

Suitability is not equivalent to trust.

Examples:

- A trusted location can still be unsuitable for a particular truck.
- An uncertain location can still be physically usable, but TruckFood may need to show unknown.
- A trusted parking record can be temporarily unavailable because the parking is full.
- A trusted restriction can make a route unsuitable without implying that every alternative route is safe.

Suitability combines vehicle context, access/restriction rules, evidence, time and assessment rules.

Trust describes the quality of the evidence behind those inputs.

## 14. Safety Boundary

TruckFood must never transform absence of evidence into evidence of safety.

Specifically:

- no restriction found means unknown, not automatically safe;
- no parking report means parking availability unknown;
- provider says truck access allowed does not override a known physical/legal restriction from stronger relevant evidence;
- community report is evidence, not automatic legal truth;
- stale evidence must not be presented as current certainty.

The system must prefer an explicit uncertainty state over a misleading positive assertion.

## 15. Source Priority

TruckFood will not implement a universal hierarchy such as Official > Provider > Community > Inference for every fact.

Source relevance depends on the fact being evaluated.

For example, a driver currently observing a blocked entrance may provide more current evidence about present physical access than an old business directory record.

Source class is therefore an input to assessment, not an unconditional winner.

## 16. User Corrections and Community Confirmation

Users should be able to:

- report a change;
- confirm an existing fact;
- contradict a fact;
- provide context;
- attach permitted evidence/media where supported.

A community action creates evidence. It does not directly rewrite authoritative source data.

Repeated independent confirmations may increase corroboration, but must not manufacture certainty where the underlying fact remains legally or physically ambiguous.

## 17. Privacy and Attribution Boundary

Evidence involving users must retain only the personal information necessary for product operation, moderation, accountability and legal requirements.

Public presentation should not expose unnecessary personal information.

Exact retention, deletion and anonymisation rules belong to the security/privacy architecture work.

## 18. Provider and Licensing Boundary

Source records must preserve licensing/use constraints where relevant.

TruckFood must not assume that because a source can be technically read, its raw evidence can be permanently stored, redistributed or exposed to users.

Provider-specific raw snapshots are therefore subject to provider terms and may need to remain outside long-term canonical persistence.

## 19. MVP Direction

The MVP should support:

- source records;
- evidence records;
- provenance class;
- observed/received/validated timestamps;
- basic freshness/review state;
- conflict indication;
- explainable presentation state;
- community observations;
- source attribution where required.

The MVP does not need:

- a sophisticated machine-learning trust model;
- a universal percentage confidence score;
- autonomous conflict resolution;
- predictive freshness;
- a global reputation algorithm.

## 20. Non-Goals

This ADR does not decide:

- exact confidence weights;
- exact numeric scoring;
- legal evidential hierarchy;
- final UI wording;
- final retention periods;
- automatic source ranking for every domain;
- machine-learning trust prediction;
- route safety guarantees;
- final SQL schema.

## 21. Consequences

### Positive

- Makes uncertainty explicit.
- Preserves the origin and history of critical information.
- Allows multiple sources to disagree without data destruction.
- Separates evidence quality from vehicle/location suitability.
- Gives future UI a factual basis for explaining why information is shown.
- Supports incremental sophistication without requiring a black-box trust engine.

### Costs / trade-offs

- More records and relationships must be persisted.
- Assessments need explainable inputs and versioning.
- Conflict handling becomes an operational concern.
- Freshness policies must be defined by data family.
- Community contributions require moderation and abuse controls.

These costs are accepted because trust is part of TruckFood's core product value.

## 22. Follow-up Decisions

Next work should define:

1. restriction/effective-time domain;
2. system/module architecture;
3. API boundaries;
4. security/privacy and Supabase RLS;
5. spatial storage/query strategy;
6. provider adapter contracts;
7. initial MVP database migration;
8. practical freshness policies by data family.
