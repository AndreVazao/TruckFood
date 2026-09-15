# Provider Cost Reality

**Status:** Discovery / indicative pricing  
**Date:** 2026-09-15

## Purpose

Compare the economic shape of external map, routing, geocoding and POI providers before TruckFood commits to an architecture that creates avoidable operating costs.

Prices below are indicative public list prices found during discovery and can change. They are not a commercial quotation.

## 1. Google Maps Platform

Google uses pay-as-you-go SKU pricing. Its current public pricing shows, among other services:

- Routes Compute Routes Essentials: 10,000 free monthly events, then $5 per 1,000 at the first paid tier.
- Routes Compute Routes Pro: 5,000 free monthly events, then $10 per 1,000 at the first paid tier.
- Geocoding: 10,000 free monthly events, then $5 per 1,000 at the first paid tier.
- Places Text Search Essentials: 10,000 free monthly events, then $5 per 1,000 at the first paid tier.
- Places Nearby Search Pro: 5,000 free monthly events, then $32 per 1,000 at the first paid tier.

These numbers make Google technically accessible for an MVP, but high-volume POI/search usage can become a meaningful recurring cost.

**TruckFood implication:** Google should not be the hidden foundation of every request. Cacheable TruckFood-owned data and a provider abstraction are economically important.

## 2. Mapbox

Mapbox currently exposes free tiers and usage-based pricing.

Examples from its public pricing:

- Directions API: up to 100,000 monthly requests free; then $2 per 1,000 at the first paid tier.
- Search Box requests: up to 25,000 monthly requests free under standard pricing; then $1.70 per 1,000 at the first paid tier.
- Temporary Geocoding: up to 100,000 monthly requests free; then $0.75 per 1,000 at the first paid tier.
- Permanent Geocoding is a different commercial/licensing case because results can be stored and reused; current public pricing starts at $5 per 1,000 requests for the first stated tier.

Mapbox documentation also makes clear that temporary and permanent geocoding have different data-use implications.

**TruckFood implication:** Mapbox can be attractive for an initial application layer, but storage/reuse rights must be evaluated separately from request price.

## 3. HERE

HERE is particularly relevant because its Routing API supports truck routing with vehicle characteristics and restrictions, including physical/legal restrictions, hazardous materials and time-dependent restrictions. It also supports toll information for truck routes.

For TruckFood, HERE should therefore be evaluated primarily as a **commercial truck-routing provider**, not simply as a generic map API.

A precise production cost cannot be concluded from this discovery pass without choosing the relevant HERE commercial plan and expected transaction volume. That is an explicit next research item.

## 4. TomTom

TomTom is another strong candidate for truck-aware routing and vehicle constraints. It should remain behind the routing-provider abstraction.

As with HERE, the decision cannot be made from technical capability alone. We need current commercial pricing, quotas, caching/storage rights, geographic coverage and contractual terms for the intended TruckFood usage.

## 5. OpenStreetMap

OSM is fundamentally different from commercial APIs. The OpenStreetMap data is available under the ODbL, with attribution and database-licensing obligations that depend on how data is used and combined.

The important distinction is:

**free access to data does not mean zero cost to operate.**

TruckFood still needs infrastructure, data processing, updates, geocoding/routing services where needed, map tiles or a suitable hosted provider, monitoring and quality control.

TruckFood must also avoid assuming that public OSM APIs/tiles are a free production backend for an application at arbitrary scale.

## 6. Cost architecture recommendation

For the first functional Portugal release, prefer:

1. **TruckFood-owned database** for curated locations, confirmations, trust and product-specific facts.
2. **OSM-compatible geographic foundation** where licensing and infrastructure are handled correctly.
3. **One external routing provider** behind an adapter, initially evaluated for truck capability.
4. **Geocoding/search only when needed**, not on every screen or every keystroke.
5. **Provider-independent domain model**, so a provider can be replaced without rewriting the product.
6. **Usage telemetry and cost budgets from day one.**

## 7. Example cost thinking

Suppose an MVP eventually generated 100,000 route requests/month:

- Google Routes Essentials list pricing would put the first paid tier at roughly $450/month after its 10,000 free events, before considering other SKUs.
- Mapbox Directions would still be around $0 at 100,000 requests under the stated free tier.

This is only a simple list-price comparison. It does **not** mean Mapbox is automatically better for TruckFood, because truck-specific routing capability, data coverage and licensing are more important than generic request price.

## 8. Cost conclusion

The cheapest API is not necessarily the cheapest TruckFood architecture.

The real cost equation is:

`API price + map/hosting + data storage + update/refresh + licensing + engineering + monitoring + quality assurance + fallback strategy`

TruckFood should therefore optimize for **controlled provider dependence**, not simply minimum price per request.

## External research references

- Google Maps Platform current pricing page (updated 2026-09-10).
- Mapbox current pricing page.
- Mapbox Geocoding documentation.
- Mapbox Directions documentation.
- Existing TruckFood provider research for HERE/TomTom truck-routing capabilities and OSM licensing.
