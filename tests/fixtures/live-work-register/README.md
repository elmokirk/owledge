# Live Work Register Fixtures

`stale-register-mutations.json` applies deterministic mutations to the canonical
valid register. It proves that a stale version claim and a historical open item
silently relabelled as shipped both fail validation. Unit tests keep the source
register as the single positive fixture and avoid maintaining a second,
drift-prone copy of all 21 entries.
