# TruckFood — Data & Licensing Rules

**Version:** 1.0.0  
**Status:** Discovery baseline  
**Date:** 2026-09-15

## Core Rule

A dataset being technically accessible does not mean TruckFood has permission to copy, store, transform, redistribute or commercially exploit it.

Every external source must be reviewed for:

- licence;
- attribution;
- commercial use;
- storage/caching rights;
- derivative-data rules;
- redistribution requirements;
- API terms;
- rate limits;
- geographic limitations;
- retention requirements;
- termination/change risk.

## OpenStreetMap

OpenStreetMap data is licensed under the Open Database License (ODbL). Use requires appropriate attribution. Where OSM data or derivative databases are distributed, ODbL share-alike obligations can apply.

TruckFood must therefore keep OSM-derived data legally separable from proprietary TruckFood data where appropriate and obtain legal review before publishing a combined database or derived dataset.

OSM may still be used as a map/data foundation, but the architecture must deliberately respect its licence.

## Commercial Routing Providers

Commercial routing providers may provide strong truck-aware capabilities, but their terms can govern:

- whether route results may be stored;
- whether results may be used to train or enrich proprietary datasets;
- whether route geometry may be cached;
- how long data may be retained;
- whether results can be shown to users in a commercial application;
- whether provider attribution is mandatory.

These questions must be answered provider-by-provider before production integration.

## Proprietary TruckFood Data

The following should remain proprietary to TruckFood where legally possible:

- TruckFood-created user profiles;
- TruckFood community observations;
- TruckFood moderation decisions;
- TruckFood trust calculations;
- proprietary business logic;
- proprietary ranking/recommendation logic;
- original software code;
- original documentation;
- independently created enrichment data.

This does not override the licence of any third-party data used to produce or influence such information.

## Source Registry Requirement

No external source should become a production dependency without a registry entry containing its legal and technical status.

## Legal Review Gate

Before public launch of any map/routing/data feature that depends materially on third-party data, the project should perform a dedicated licensing review for the actual commercial use case and jurisdictions involved.

This document is an engineering governance document, not legal advice.
