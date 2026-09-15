# TruckFood — Source Registry

**Version:** 1.0.0  
**Status:** Discovery baseline

This registry records candidate external sources. A candidate is not automatically approved for production use.

| Source | Role | Candidate status | Main value | Main risk / open point |
|---|---|---|---|---|
| OpenStreetMap | Geographic base + restriction signals | Research candidate | Open global geographic data; truck-relevant restriction tags | ODbL obligations; coverage and accuracy vary |
| HERE Routing | Truck routing | Research candidate | Truck mode; vehicle dimensions; legal/physical/time-dependent restrictions | Commercial terms, cost, coverage, storage rights |
| TomTom | Truck routing / mapping | Research candidate | Truck vehicle model and dimensions/restrictions | Commercial terms, current API coverage, storage rights |
| Official government datasets | Restrictions / closures / regulations | To research | Potential authoritative information | Fragmentation, licences, update methods |
| TruckFood community | Observations / corrections / reviews | Planned proprietary domain | Local reality and freshness | Abuse, false reports, moderation, liability |
| Business/POI providers | Restaurants / parking / services | To research | Coverage and business metadata | Licence, commercial use, duplication, freshness |

## Required Review Fields

Before approval, every source must be evaluated for:

- legal licence;
- commercial permission;
- geographic coverage;
- update frequency;
- API/data access method;
- quotas and costs;
- storage/caching rights;
- attribution requirements;
- quality and known gaps;
- failure behaviour;
- provider lock-in risk.

## Current Rule

No source in this registry is yet designated as the sole authoritative source for truck safety or legal routing.
