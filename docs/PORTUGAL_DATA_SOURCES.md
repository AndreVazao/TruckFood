# Portugal Data Sources

**Status:** Discovery / candidate registry  
**Date:** 2026-09-15

## Purpose

Identify Portuguese sources that can support TruckFood's **CHEGAR → PARAR → COMER → DESCANSAR → CONTINUAR** mission, with special attention to professional truck transport.

This document is a discovery record, not a declaration that any source is safe, complete, authoritative for navigation, or licensed for unrestricted commercial reuse.

## 1. Road and traffic restrictions

### IMT — Instituto da Mobilidade e dos Transportes

**Role:** primary candidate for legal/regulatory information concerning road transport, dangerous goods and transport restrictions.

Relevant finding: IMT publishes specific restrictions for heavy vehicles carrying dangerous goods. Its current information includes time and road-network restrictions and special authorisations. IMT also publishes ADR material, including ADR 2025 and the Portuguese regulatory framework.

**TruckFood use:** regulatory source/reference; do not turn a regulatory page into an automatic routing rule without validation of scope, dates, exceptions and legal status.

### Infraestruturas de Portugal (IP)

**Role:** primary candidate for national-road-network information, traffic regimes, road infrastructure and operational changes.

A current 2026 example demonstrates why this source class matters: new VCI restrictions for heavy goods vehicles in Porto enter into force on 15 September 2026, with weekday time restrictions. This is exactly the type of time-dependent rule that TruckFood must model rather than flatten into a permanent road closure.

**TruckFood use:** official restriction/event source, road-network context, and candidate source for operational/temporary information.

### Diário da República / official legislation

**Role:** legal source for published legislation and regulations.

The road-network legal framework explicitly recognises service areas, rest areas and parking areas. The current consolidated Estatuto das Estradas da Rede Rodoviária Nacional includes later amendments and should be treated as a legal reference rather than a geospatial POI feed.

**TruckFood use:** legal verification and provenance for rules.

## 2. Rest areas, service areas and truck parking

Portuguese road legislation recognises **áreas de repouso**, **parques de estacionamento** and **áreas de serviço**. This gives TruckFood a useful official vocabulary and data model foundation.

However, the legal existence of a category does not provide a ready-made nationwide, real-time, truck-capacity dataset. TruckFood will therefore likely need to combine:

- official/concessionaire location data;
- OpenStreetMap/open geographic data;
- municipality/local sources where available;
- community confirmations;
- direct business/operator submissions.

### Concessionaires

Concessionaire websites can expose operational details not present in general legal sources. For example, Auto-Estradas do Atlântico lists service areas and explicitly identifies parking for heavy vehicles and driver showers at some locations. Brisa also publishes its service-area network and services.

**Important:** these pages are useful discovery sources, but commercial reuse rights and update mechanisms must be checked before ingestion into a production database.

## 3. Restaurants and driver-oriented food

There is no single Portuguese official nationwide restaurant dataset suitable as the TruckFood product database.

Candidate layers:

1. OpenStreetMap for geographic/POI baseline.
2. Commercial POI providers where licensing permits the intended use.
3. Direct restaurant/operator submissions.
4. TruckFood community observations and confirmations.

TruckFood should store provenance per fact and avoid treating a restaurant's presence on a map as proof that a truck can access or park there.

## 4. Key data model implication

Portugal research reinforces the existing TruckFood model:

`Location + Vehicle Context + Restriction + Source + Effective Time + Confidence + Freshness`

For a parking location, examples include:

- truck access allowed / unknown;
- articulated vehicles allowed / unknown;
- estimated or reported truck capacity;
- overnight parking allowed / unknown;
- lighting;
- surveillance;
- WC;
- showers;
- restaurant;
- fuel;
- paid/free;
- source;
- last confirmation;
- confidence.

For a road restriction:

- road/segment/area;
- restriction type;
- affected vehicle profile;
- legal vs physical restriction;
- start/end/effective schedule;
- source;
- publication/update date;
- confidence;
- verification state.

## 5. Critical finding

The strongest Portuguese sources are not necessarily machine-ready product feeds. TruckFood must build a **source adapter + normalisation + provenance** layer rather than scrape pages directly into the product database.

No single source found in this phase is sufficient to guarantee that a truck route or parking decision is safe.

## 6. Initial source priority

| Source class | Priority | Intended role |
|---|---:|---|
| IMT | Very high | Legal/regulatory and dangerous-goods restrictions |
| Infraestruturas de Portugal | Very high | National network and operational restrictions/events |
| Diário da República | Very high | Legal verification |
| Autoestrada concessionaires | High | Service/rest-area operational details |
| OSM | High | Geographic/POI/restriction foundation |
| Municipal/local sources | Medium | Local restrictions and facilities |
| TruckFood community | High | Reality confirmations and changes |
| Commercial POI providers | Conditional | Search/POI enrichment, subject to licensing |

## 7. Discovery conclusion

Portugal is viable as TruckFood's first market, but the product should not be built around a single government feed or a single commercial map provider.

The practical architecture is a **Portuguese source registry feeding a normalized TruckFood data model**, with explicit provenance, effective dates, confidence and conflict handling.

---

## External research references

- IMT — Autorizações Especiais de Circulação / dangerous-goods restrictions.
- IMT — ADR and dangerous-goods regulatory material.
- Infraestruturas de Portugal — VCI heavy-goods traffic regime, effective 15 September 2026.
- Diário da República / consolidated road-network statute.
- Auto-Estradas do Atlântico — service areas and services.
- Brisa Concessão — service-area network.
