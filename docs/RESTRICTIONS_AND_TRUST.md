# TruckFood — Restrictions, Provenance & Trust

**Version:** 1.0.0  
**Status:** Discovery baseline

## Why This Exists

Road and access information is potentially safety-critical. TruckFood must never turn uncertain information into a false guarantee.

## Restriction Types

The model should be able to represent restrictions such as:

- maximum height;
- maximum weight;
- maximum width;
- maximum length;
- prohibited vehicle class;
- prohibited access;
- time-dependent restriction;
- temporary restriction;
- road closure;
- bridge restriction;
- low-clearance warning;
- local access restriction.

The final taxonomy must be validated against actual data sources and legal/licensing constraints.

## Provenance Classes

Every critical external or community fact should be traceable to a provenance class such as:

1. **Official** — supplied by a competent authority or official source.
2. **Provider** — supplied by a contracted or mapping/data provider.
3. **Community** — reported or confirmed by users.
4. **Inference** — calculated or inferred by TruckFood.

These classes are not automatically equal in trust.

## Freshness

Time-sensitive information should carry enough metadata to distinguish:

- when it was observed;
- when it was received;
- when it was last validated;
- when it should be reviewed again.

## Confidence

Confidence should not be a decorative score. It should be explainable from factors such as:

- source quality;
- recency;
- corroboration;
- contradiction;
- geographic precision;
- historical reliability.

## User Interface Rule

When confidence is insufficient, the interface should communicate uncertainty instead of hiding it.

Example conceptual states:

- Confirmed
- Likely
- Reported
- Unverified
- Conflicting
- Expired / Needs Review

Exact wording and scoring will be decided later.

## Safety Boundary

TruckFood must not claim that a route is legally or physically safe solely because no restriction is known.

The absence of a known restriction is **not proof of absence of a restriction**.

This principle is mandatory for future route-intelligence features.
