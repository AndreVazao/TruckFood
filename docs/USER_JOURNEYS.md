# TruckFood — Critical User Journeys

**Version:** 1.0.0  
**Status:** Discovery baseline

## Journey 1 — Before Departure

**Goal:** prepare a realistic journey.

1. Driver opens TruckFood.
2. Driver selects or confirms vehicle profile.
3. Driver enters origin and destination.
4. System obtains route context from the selected routing capability.
5. TruckFood evaluates known truck-relevant facts and restrictions.
6. System highlights potential issues with confidence/provenance.
7. Driver reviews possible stopping, parking, food and rest opportunities.

The first MVP may stop short of full route calculation and provide context around a selected route.

## Journey 2 — Approaching a Stop

**Goal:** find a practical stop before reaching a difficult situation.

1. Driver searches near the route.
2. System prioritises relevant truck-suitable locations.
3. Driver filters by parking, food, services or rest.
4. Driver opens a location.
5. System shows practical facts, source/freshness and community information.
6. Driver decides whether to stop.

## Journey 3 — Find Food

**Goal:** eat without creating unnecessary problems for the truck.

The system should help answer:

- Can my truck get there?
- Can I park?
- Is it open?
- Is it suitable for a quick meal?
- What do other drivers say?

## Journey 4 — Report Reality

**Goal:** improve information for the next driver.

1. Driver selects a location or road fact.
2. Driver reports an observation or correction.
3. System records the contributor, time and relevant context.
4. Moderation/trust logic evaluates the contribution.
5. The information may become a confirmation, warning, pending change or rejected report.

## Journey 5 — Continue After Stop

**Goal:** return to the journey with the next useful decision.

TruckFood should preserve enough context to help the driver continue without forcing the driver to rebuild the entire search from zero.

## Critical UX Rule

A professional driver may be using the application under time pressure. The most important information must be discoverable quickly, readable at a glance and never hidden behind unnecessary interaction.
