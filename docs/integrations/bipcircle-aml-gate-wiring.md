# BIPCircle ↔ AML Gate Integration — Wiring Briefing

> **Status:** Pre-meeting briefing for the wiring session with Nick V on 2026-04-11.
> **Audience:** AML Gate maintainers, BIPCircle maintainers, integration reviewers.
> **Purpose:** Snapshot of what is already wired between BIPCircle and AML Gate, what is still missing, and the decisions that need to be agreed before any merge can happen.
> **Sources:** Live read of `bipcircle/api/src` and `AML-Gate/bipcircle-integration/` on 2026-04-11. Code citations are by function/file name only — line numbers drift.

This document is published into the OpenKYCAML repo because the integration patterns it captures (Pub/Sub event schema, wallet DID convention, dual-read fallback, MLRO case auto-creation) are intended to become reusable adoption guidance, not BIPCircle-specific wiring notes. The decisions made in the meeting will harden into OpenKYCAML reference patterns.

---

## 1. Executive Summary

The two systems are about **70% wired** but the last 30% is the part that actually makes the integration work end-to-end on a transaction.

**Already in place:**
- BIPCircle has a working OIDC-authenticated AML Gate HTTP client (`platform/services/amlGateClient.js`) used today by the platform admin / jurisdiction admin / AI health routes
- BIPCircle has its own version of `amlStatusSubscriber.js` already merged into the product layer (266 lines, ESM)
- ID Circle integration is production: `silentReVerify` runs fail-closed on every login, HMAC-verified webhooks, attestation signature verification
- All four MLRO case types (`sanctions_match`, `aml_gate_match`, `review_expired`, `travel_rule_failure`) are registered in BIPCircle's MLRO routes
- Wallet DID field is populated in audit trails and MLRO middleware

**Missing or partial — these block end-to-end testing:**
- The `AML_GATE_CLEARED` check name appears in BIPCircle's compliance gate citations but the switch statement falls through to the fail-closed default. It is not registered in `REQUIRED_CHECKS` for any value-moving transaction.
- BIPCircle's existing `amlStatusSubscriber.js` is **not wired to a Pub/Sub push endpoint** — the handler is callable but no route mounts it.
- The BIPCircle subscriber and the AML Gate integration template **disagree on the event schema** (see §3 — this is the critical finding).
- `AML_GATE_URL` and `PUBSUB_TOPIC_AML_EVENTS` are missing from `.env`, `.env.local`, `.env.example`, and `start-dev.sh`.
- `services/travelRuleService.js` exists but is a 0-line empty placeholder.
- The heartbeat doc (`system/aml_pubsub_health`) is **written** by the subscriber but **not read** by the compliance gate, so the dual-read fallback never fires.
- The `pending_kyc_revocations` queue is written on `blocked` events but no processor consumes it against the ERC-3643 ONCHAINID contract.

---

## 2. Current State Matrix

| # | Component | Status | Evidence | Blocker for end-to-end test? |
|---|---|---|---|---|
| 1 | `amlGateClient` (OIDC HTTP client) | ✅ Wired | `platform/services/amlGateClient.js` — `callAmlGate()`, `getAmlGateBreakerState()`. Used by `platformAdmin.js` (rescreen, health), `jurisdictionAdmin.js` (PDF extraction), `ai.js` (health) | No |
| 2 | `amlStatusSubscriber` handler | ⚠️ Code present, not wired | `products/bipcircle/services/amlStatusSubscriber.js` exists with `handleAmlStatusEvent()` exported, but no route mounts it. Schema mismatch with AML-Gate template (see §3) | **Yes** |
| 3 | `AML_GATE_CLEARED` compliance check | ❌ Stub only | Check name appears in `complianceGate.js` RULE_CITATIONS but switch statement default-fails. Not in REQUIRED_CHECKS for any txn type | **Yes** |
| 4 | Heartbeat staleness fallback | ⚠️ Half-wired | Subscriber writes `system/aml_pubsub_health`. `platformAdmin.js` reads it for the health dashboard. Compliance gate does NOT read it for dual-read trigger | **Yes** |
| 5 | Travel Rule | ❌ Missing | `services/travelRuleService.js` is 0 lines. `amlTravelRuleTrigger.js` (125 lines, ready) lives in `AML-Gate/bipcircle-integration/` but never merged. No call sites in any signing path | Yes (deferable) |
| 6 | MLRO case auto-creation | ✅ Wired | All 4 types registered in `routes/mlro.js`. BIPCircle subscriber creates cases on `blocked` / `review_required` | No |
| 7 | `AML_GATE_URL` env var | ❌ Missing | Not in `.env`, `.env.local`, `.env.example`, `start-dev.sh`. Code falls back to `null` and skips calls | **Yes** |
| 8 | `PUBSUB_TOPIC_AML_EVENTS` env var | ❌ Missing | Not configured. Topic + push subscription must be created on the GCP side too | **Yes** |
| 9 | ID Circle integration | ✅ Wired | `services/idCircle.js` — `silentReVerify`, HMAC webhook, attestation signature verification. Fail-closed | No |
| 10 | Wallet DID as universal identifier | ⚠️ Partial | `walletDID` field populated from attestations in audit trails and MLRO middleware, but value is the bare hex/XRPL address — NOT the W3C `did:xrpl:rXXX` form AML Gate expects | Yes (decision in meeting) |
| 11 | `pending_kyc_revocations` processor | ❌ Missing | Subscriber queues revocations but no job/route consumes the queue and calls the ERC-3643 ONCHAINID contract | Yes (deferable) |
| 12 | AML AI tools / system prompt | ⚠️ Available, not merged | `amlGateAiTools.js` (212 LOC) and `amlGateAiSystemPrompt.js` (167 LOC) ready in integration repo, not yet imported into BIPCircle's `aiDataTools.js` / `aiSystemPrompt.js` | No |

---

## 3. The Critical Finding: Two Incompatible Event Schemas

**This is the single most important thing for the meeting.**

Both repos contain an `amlStatusSubscriber.js`. They were written in parallel and never reconciled. They expect **different event payloads** and **different field naming conventions**. If AML Gate publishes events in its current format today, BIPCircle's existing subscriber will throw on the very first message and Pub/Sub will dead-letter every event.

### 3.1 BIPCircle's version

`/Users/markflynn/Local Sites/bipcircle/api/src/products/bipcircle/services/amlStatusSubscriber.js` (266 lines, ESM)

```js
// Validates event shape and rejects anything that isn't this exact eventType
if (event.eventType !== 'aml.status_changed') {
  throw new Error(`aml event: unexpected eventType "${event.eventType}"`);
}
const {
  userId, fundTenantId, status, previousStatus, reason,
  screeningId, decisionId, jurisdictionCode,
  jurisdictionPackVersion, confidence, matchedLists,
  correlationId, rawPayload,
} = event;
```

**Expected envelope:**
```json
{
  "eventType": "aml.status_changed",
  "userId": "abc123",
  "fundTenantId": "Test",
  "status": "blocked",
  "previousStatus": "cleared",
  "reason": "OFAC SDN match",
  "screeningId": "scr_xyz",
  "decisionId": "dec_xyz",
  "jurisdictionCode": "GG",
  "jurisdictionPackVersion": "v1.2.0",
  "confidence": 0.97,
  "matchedLists": ["OFAC_SDN"],
  "correlationId": "corr_xyz",
  "rawPayload": { /* full provider response */ }
}
```

**Behaviour:**
- Field naming: **camelCase**
- Dedupes via `db.runTransaction` (atomic claim)
- Calls `revokeOnchainClaims(db, mockReq, userId, [1, 2], { ... })` **directly** for `blocked` status (claim topics 1 = KYC, 2 = AML)
- Throws on revocation failure so Pub/Sub retries
- Releases held transactions on `cleared` (paginated, batches of 50)
- Heartbeat: ISO timestamp string

### 3.2 AML-Gate integration template version

`/Users/markflynn/Local Sites/AML-Gate/bipcircle-integration/amlStatusSubscriber.js` (239 lines, CommonJS)

```js
if (event.event === "customer.status_changed") {
  await processStatusChange(db, event, messageId);
}
// ...
const { tenant_id, external_id, status, risk_tier, fatal_flags, screening_id } = event;
```

**Expected envelope:**
```json
{
  "event": "customer.status_changed",
  "message_id": "uuid-v4",
  "tenant_id": "Test",
  "external_id": "abc123",
  "status": "blocked",
  "risk_tier": "critical",
  "fatal_flags": ["confirmed_sanctions_match"],
  "screening_id": "scr_xyz",
  "country_code": "RU",
  "correlation_id": "corr_xyz",
  "changed_at": "2026-04-11T10:00:00Z"
}
```

**Behaviour:**
- Field naming: **snake_case**
- Property name for the event type is `event` (not `eventType`)
- Identity field is `external_id` (not `userId`)
- Tenant field is `tenant_id` (not `fundTenantId`)
- Resolves `fundTenantId` from `fund_tenant_members.where(userId == external_id)` lookup
- **Queues** KYC revocation to `pending_kyc_revocations` instead of calling `revokeOnchainClaims` directly — assumes a separate processor
- MLRO case creation is **non-fatal** (errors logged, not thrown — does not retry)
- Heartbeat: `FieldValue.serverTimestamp()`
- Generates `randomUUID()` for caseId

### 3.3 Side-by-side diff (the parts that matter)

| Concern | BIPCircle subscriber | AML-Gate template | Why it matters |
|---|---|---|---|
| Type field name | `eventType` | `event` | If AML Gate publishes today's payload, BIPCircle throws "unexpected eventType undefined" |
| Type value | `aml.status_changed` | `customer.status_changed` | Even if you alias the field, the values don't match |
| Naming | camelCase | snake_case | Either one side renames or one side has a translator layer |
| User ID field | `userId` | `external_id` | Affects every downstream lookup |
| Tenant ID field | `fundTenantId` | `tenant_id` (resolved via member lookup) | Affects MLRO case routing |
| Dedupe | `db.runTransaction` | `dedupRef.get()` then `set()` | BIPCircle's is race-safe; template's has a (small) window |
| KYC revoke | Direct call, throws on fail | Queue write, no processor | BIPCircle relies on `amlClaimManager`; template assumes a queue consumer |
| MLRO case fail mode | Throws (Pub/Sub retries) | Logged + ignored | Compliance-critical writes should retry |
| Heartbeat type | ISO string | Server timestamp | Reader must handle both forms |
| Module system | ESM `import/export` | CommonJS `require/module.exports` | BIPCircle is ESM end-to-end — the template needs porting |

### 3.4 Recommended canonical schema (for the meeting)

The OpenKYCAML envelope is the long-term home for this. For the immediate fix the simplest converging path is:

1. **Adopt AML Gate's `customer.status_changed` event name and snake_case field names** as the canonical wire format. AML Gate is the publisher; the publisher's schema is authoritative.
2. **Keep BIPCircle's behavioural model** (transactional dedupe, direct revocation call, fail-closed retries, paginated held-tx release) — that side is more correct.
3. **Port the BIPCircle subscriber** to consume the snake_case schema by aliasing fields at the validation step. Roughly 30 lines of code change in `handleAmlStatusEvent()`.
4. **Add the snake_case schema to OpenKYCAML's event spec** so any future consumer (not just BIPCircle) has a single source of truth.

This decision must be made in the meeting before any code lands.

---

## 4. The Five Production-Ready Files in `AML-Gate/bipcircle-integration/`

These are not stubs. They are written for production merge into BIPCircle. **925 lines, 5 files.**

| File | Lines | Drop into | Purpose |
|---|---|---|---|
| `amlStatusSubscriber.js` | 239 | `services/amlStatusSubscriber.js` (already exists in BIPCircle — see §3, must reconcile not blindly overwrite) | Pub/Sub handler → cache write → MLRO case → KYC revoke queue + heartbeat |
| `amlComplianceCheck.js` | 182 | `services/complianceGate.js` REQUIRED_CHECKS + new switch case | `AML_GATE_CLEARED` check, dual-read for high-value, 5-min heartbeat staleness, fail-closed |
| `amlTravelRuleTrigger.js` | 125 | New `services/travelRuleService.js` (currently empty placeholder) | Pre-sign Travel Rule check, holds tx in `held_transactions` |
| `amlGateAiTools.js` | 212 | `services/aiDataTools.js` registry | 13 AML AI tools with `<tool_data>` XML prompt-injection defence |
| `amlGateAiSystemPrompt.js` | 167 | `services/aiSystemPrompt.js` | Per-tenant regulatory knowledge with 15-min cache + fallback |

---

## 5. AML Gate Service Endpoints (the API surface)

Base URL: `https://api-bmuvem3rrq-nw.a.run.app`. All `/v1/*` endpoints except `/v1/health` require GCP OIDC bearer token with audience matching `AML_GATE_URL`.

| Endpoint | Purpose | Caller |
|---|---|---|
| `GET /v1/health` | Liveness (no auth) | Platform health probe |
| `POST /v1/screen` | Full screening (sync or 202 + poll) | KYC wallet onboarding flow |
| `GET /v1/customer/{userId}/status?tenant_id=X` | Dual-read live check | `amlComplianceCheck` for high-value or stale-heartbeat dual-read |
| `POST /v1/travel-rule/outbound` | Initiate Travel Rule saga | `amlTravelRuleTrigger` pre-sign |
| `GET /v1/ai/knowledge?tenant_id=X` | Regulatory knowledge for AI prompt | `amlGateAiSystemPrompt` |
| `GET /v1/ai/tools` | AML AI tool definitions | Startup |
| `POST /v1/ai/execute-tool` | Execute one AML tool | AI tool router |

---

## 6. Pub/Sub Event Schemas

**Topic:** `aml-gate-events` (env: `PUBSUB_TOPIC_AML_EVENTS`)
**Subscription:** `bipcircle-aml-status` (push endpoint to be created in BIPCircle — see Appendix A)

### `customer.status_changed` (canonical, snake_case — see §3.4)

```json
{
  "event": "customer.status_changed",
  "message_id": "uuid-v4",
  "tenant_id": "Test",
  "external_id": "user-id-in-bipcircle",
  "status": "cleared|blocked|review_required|expired",
  "risk_tier": "low|medium|high|critical",
  "fatal_flags": ["confirmed_sanctions_match", "fatf_blacklist"],
  "screening_id": "string",
  "country_code": "ISO",
  "correlation_id": "uuid",
  "changed_at": "ISO8601"
}
```

Pub/Sub message attributes (set on the message itself, not the body):
```
event_type:        customer.status_changed
tenant_id:         Test
correlation_id:    uuid (fallback to message_id)
```

### `screening.completed` (informational)

Smaller payload — `screening_id`, `action`, `completed_at`. Used by ID Circle to know when to poll. BIPCircle currently no-ops on these.

---

## 7. Wallet DID Convention

AML Gate accepts the W3C DID format in the `wallet_did` field on `POST /v1/screen` and `POST /v1/travel-rule/outbound`:

| DID method | Example | Notes |
|---|---|---|
| `did:xrpl:rXXX...` | `did:xrpl:rKYaAiTRaMrCDFDpwohMHHDPZxhPC6cFpG` | XRPL accounts |
| `did:eth:0xXXX...` | `did:eth:0xaCD9E18a80efcAD15b9Ab4503e126131E3F8d741` | Ethereum/EVM accounts |
| `did:ebsi:*` | EBSI base32z identifiers | EU self-sovereign |
| `did:web:domain.tld` | `did:web:bipcircle.com` | Domain-anchored. Path segments containing PII are SHA-256 truncated to 16 hex chars |
| `did:key:*`, `did:ion:*`, `did:peer:*` | various | Key-anchored, never contain PII |

**Bare wallet addresses are NOT accepted as wallet DIDs.** They must be wrapped (`did:xrpl:rXXX`) or passed in a separate `originator_address` field for Travel Rule.

**BIPCircle today stores raw hex/XRPL addresses in the `walletDID` audit field.** This is the schema decision the meeting must resolve:

- **Option A** — Mass-rewrite the `walletDID` field everywhere. Pros: clean. Cons: touches every audit row, every MLRO case, every attestation. Migration risk.
- **Option B** — Add a `walletDIDCanonical` mirror field at write time, keep the legacy raw form for backwards compat. Read paths fall back to legacy if canonical missing. Pros: zero migration. Cons: two fields to keep in sync, schema drift risk.
- **Option C** — Add a `toWalletDid(chain, address) → did:xrpl:rXXX | did:eth:0xXXX` helper at the boundaries (when we call AML Gate / publish events) and leave the storage shape unchanged. Pros: zero schema impact. Cons: every boundary must remember to call the helper.

Recommendation: **Option C** for short-term wiring, **Option B** as the medium-term mirror, **Option A** when the OpenKYCAML envelope is fully canonicalised.

A sketch of the helper is in **Appendix C**.

---

## 8. Recommended Meeting Order

If time is tight with Nick, do these in dependency order. Each step unlocks the next.

1. **GCP-side prep first** (Nick or both): create Pub/Sub topic `aml-gate-events`, create push subscription `bipcircle-aml-status`, generate the OIDC service account that BIPCircle will use to call AML Gate.
2. **Set `AML_GATE_URL` + `PUBSUB_TOPIC_AML_EVENTS`** in BIPCircle `.env.local` and Cloud Run env.
3. **Decide canonical event schema** (§3.4) — this is the single highest-leverage decision.
4. **Reconcile the two `amlStatusSubscriber.js` versions** based on the §3.4 decision. Port BIPCircle's behavioural model onto AML Gate's wire schema.
5. **Drop in `amlComplianceCheck.js`**, register `AML_GATE_CLEARED` in REQUIRED_CHECKS for at least USDT_PAYMENT, RLUSD_PAYMENT, BTC_ONCHAIN_PAYMENT, TOKENS_TRANSFERRED (the value-moving txns that already exist). Patch sketch in **Appendix B**.
6. **Mount the Pub/Sub push endpoint** (`routes/amlEvents.js` mirroring `jurisdictionWebhooks.js`). Draft in **Appendix A**.
7. **Wallet DID schema decision** (§7).
8. **End-to-end smoke test:**
   - Clean customer in ID Circle → screening passes → BIPCircle cache update → USDT payment proceeds.
   - Blocked customer → cache update → USDT payment blocked + MLRO case created.
9. **Travel Rule + KYC revocation processor** — defer to a follow-up session, each ≥1 hour. The smoke test above is the meeting's success criterion.

---

## 9. Decisions Nick Needs to Make in the Meeting

1. **Event schema** — accept the canonical snake_case `customer.status_changed` envelope (§3.4)?
2. **Wallet DID storage** — Option A / B / C from §7?
3. **Tenant ID resolution** — does AML Gate's `tenant_id` map 1:1 to BIPCircle's `fundTenantId`, or does BIPCircle still need the `fund_tenant_members` lookup the integration template does today?
4. **OIDC service account** — which SA does AML Gate use to push to BIPCircle, and which SA does BIPCircle use to call AML Gate? Two separate identities, both need IAM grants in both projects.
5. **High-value threshold** — confirm $10,000 USD-equivalent as the dual-read trigger, or set per-tenant via `tenants/{id}/amlGateConfig/config`?
6. **Heartbeat staleness window** — confirm 5 minutes? (BIPCircle's `aml-gate-events` push subscription will need a healthier delivery cadence than that, otherwise the dual-read fallback fires constantly.)
7. **MLRO case priority mapping** — `blocked` = critical, `review_required` = high. Confirm or override per fatal-flag class?
8. **Merge target** — does the merged `amlStatusSubscriber.js` live in BIPCircle's `products/bipcircle/services/` (current location) or is it lifted to `platform/services/` (so it can be reused by future products like SoundBip)?

---

## Appendix A — Draft `routes/amlEvents.js` (Pub/Sub Push Endpoint)

This is a direct mirror of `routes/jurisdictionWebhooks.js`. It is offered as a draft for review, not a commit. The handler is delegated to `handleAmlStatusEvent` which already exists in `services/amlStatusSubscriber.js`. After the §3.4 decision the handler signature may change slightly (snake_case input).

```js
/**
 * AML Gate webhooks — Cloud Pub/Sub push endpoint for
 * `customer.status_changed` events from AML Gate.
 *
 * Mounted BEFORE App Check because Pub/Sub push delivery does not
 * carry App Check tokens — the caller is Google's Pub/Sub service.
 * Authentication is via Google-issued OIDC tokens in the
 * Authorization header, verified against the expected audience and
 * service-account email.
 *
 * AML Gate publishes to the `aml-gate-events` topic in the aml-gate
 * GCP project. A push subscription targets this endpoint and Google
 * signs each delivery with an ID token bound to the BIPCircle audience.
 *
 * Route: POST /api/webhooks/aml-events
 *
 * Mirror of routes/jurisdictionWebhooks.js — keep them in sync.
 */

import { Router } from 'express';
import { z } from 'zod';
import { OAuth2Client } from 'google-auth-library';
import { log } from '../../../platform/utils/logger.js';
import { sendSuccess, sendError, validateBody } from '../../../platform/utils/response.js';
import { handleAmlStatusEvent } from '../services/amlStatusSubscriber.js';

const router = Router();

const pubsubPushSchema = z.object({
  message: z.object({
    data: z.string().min(1),
    messageId: z.string().min(1).max(256),
    publishTime: z.string().optional(),
    attributes: z.record(z.any()).optional(),
  }),
  subscription: z.string().optional(),
});

const oauthClient = new OAuth2Client();

const EXPECTED_AUDIENCE =
  process.env.PUBSUB_AML_AUDIENCE ||
  process.env.BIPCIRCLE_API_URL ||
  null;

const EXPECTED_PUBLISHER_SA = process.env.PUBSUB_AML_PUBLISHER_SA || null;

router.post('/aml-events', validateBody(pubsubPushSchema), async (req, res) => {
  try {
    // ── Verify Google OIDC token ─────────────────────────────────────
    const authHeader = req.headers['authorization'] || '';
    const isProduction = process.env.NODE_ENV === 'production';

    if (authHeader.startsWith('Bearer ')) {
      const token = authHeader.slice(7);
      try {
        const ticket = await oauthClient.verifyIdToken({
          idToken: token,
          audience: EXPECTED_AUDIENCE || undefined,
        });
        const claims = ticket.getPayload();
        if (EXPECTED_PUBLISHER_SA && claims.email !== EXPECTED_PUBLISHER_SA) {
          log.warn({
            tokenEmail: claims.email,
            expected: EXPECTED_PUBLISHER_SA,
          }, 'AML Gate push: unexpected publisher service account');
          return sendError(res, 'Forbidden', 403);
        }
      } catch (verifyErr) {
        log.error({ err: verifyErr.message }, 'AML Gate push: OIDC verification failed');
        if (isProduction) return sendError(res, 'Unauthorized', 401);
        log.warn('AML Gate push: accepting unverified token in non-production');
      }
    } else if (isProduction) {
      return sendError(res, 'Unauthorized — missing bearer token', 401);
    }

    // ── Parse Pub/Sub envelope ───────────────────────────────────────
    const envelope = req.body;
    if (!envelope?.message?.data) {
      return sendError(res, 'Invalid Pub/Sub envelope — missing message.data', 400);
    }

    const messageId = envelope.message.messageId;
    if (!messageId) {
      return sendError(res, 'Invalid Pub/Sub envelope — missing messageId', 400);
    }

    let payload;
    try {
      const decoded = Buffer.from(envelope.message.data, 'base64').toString('utf8');
      payload = JSON.parse(decoded);
    } catch (parseErr) {
      log.error({ err: parseErr.message }, 'AML Gate push: failed to decode payload');
      return sendError(res, 'Invalid Pub/Sub payload encoding', 400);
    }

    // ── Delegate to handler ──────────────────────────────────────────
    // Handler is idempotent — re-delivery of the same messageId returns
    // outcome=duplicate without side effects. Errors propagate as 500
    // so Pub/Sub retries (up to the push subscription's max delivery
    // attempts, then dead-letters).
    const result = await handleAmlStatusEvent({
      db: req.db,
      event: payload,
      messageId,
      logger: req.log || log,
    });

    return sendSuccess(res, result);
  } catch (err) {
    log.error({ err: err.message, stack: err.stack }, 'AML webhook failed');
    return sendError(res, 'Webhook processing failed', 500);
  }
});

export default router;
```

**Wiring in `server.js`:**
```js
import amlEventsRouter from './products/bipcircle/routes/amlEvents.js';
// ...mount BEFORE App Check, alongside jurisdictionWebhooks:
app.use('/api/webhooks', amlEventsRouter);
```

**New env vars:**
- `PUBSUB_AML_AUDIENCE` — public URL Pub/Sub targets when pushing (Cloud Run service URL in prod, override via env in sandbox)
- `PUBSUB_AML_PUBLISHER_SA` — the service account email AML Gate uses to publish the push (closes replay vector)

---

## Appendix B — `AML_GATE_CLEARED` Compliance Gate Patches

Two changes in `services/complianceGate.js`. Both are minimum-viable: the check is added to the four payment types we exercise today, plus the token transfer path. Other transaction types can be added incrementally.

### B.1 — Register the check in `REQUIRED_CHECKS`

```js
RLUSD_PAYMENT: [
  { check: 'INITIATOR_ATTESTATION_VALID', failAction: 'block' },
  { check: 'COUNTERPARTY_ADDRESS_WHITELISTED', failAction: 'block' },
  { check: 'AML_GATE_CLEARED', failAction: 'block' },        // NEW
  { check: 'SAR_AMOUNT_THRESHOLD', failAction: 'flag' },
  { check: 'SANCTIONS_SCREENING', failAction: 'block' },
],
USDT_PAYMENT: [
  { check: 'INITIATOR_ATTESTATION_VALID', failAction: 'block' },
  { check: 'COUNTERPARTY_ADDRESS_WHITELISTED', failAction: 'block' },
  { check: 'AML_GATE_CLEARED', failAction: 'block' },        // NEW
  { check: 'SAR_AMOUNT_THRESHOLD', failAction: 'flag' },
  { check: 'SANCTIONS_SCREENING', failAction: 'block' },
],
LIGHTNING_PAYMENT: [
  { check: 'INITIATOR_ATTESTATION_VALID', failAction: 'block' },
  { check: 'AML_GATE_CLEARED', failAction: 'block' },        // NEW
  { check: 'SAR_AMOUNT_THRESHOLD', failAction: 'flag' },
],
BTC_ONCHAIN_PAYMENT: [
  { check: 'INITIATOR_ATTESTATION_VALID', failAction: 'block' },
  { check: 'COUNTERPARTY_ADDRESS_WHITELISTED', failAction: 'block' },
  { check: 'AML_GATE_CLEARED', failAction: 'block' },        // NEW
  { check: 'SAR_AMOUNT_THRESHOLD', failAction: 'flag' },
  { check: 'SANCTIONS_SCREENING', failAction: 'block' },
],
TOKENS_TRANSFERRED: [
  // ...existing checks...
  { check: 'AML_GATE_CLEARED', failAction: 'block' },        // NEW
  // ...
],
```

### B.2 — Implement the switch case

```js
import { runAmlGateCheck } from './amlComplianceCheck.js';

// Inside runCheck() switch statement, add:
case 'AML_GATE_CLEARED': {
  return runAmlGateCheck(req, params);
}
```

`runAmlGateCheck` is the function exported by `amlComplianceCheck.js` (the integration template). It:
- Reads from `aml_status_cache/{userId}` (cache fast path)
- Calls `isHeartbeatStale()` to detect Pub/Sub lag (5-min threshold)
- For high-value (≥$10k) OR stale heartbeat, performs `fetchLiveStatus()` synchronous call to AML Gate
- Returns `{ checkResult: 'pass'|'fail', detail: string }`
- Fails closed on AML Gate unreachable

**Note:** the integration template is CommonJS. Either port it to ESM at merge time, or import it via the dynamic import shim already used elsewhere in BIPCircle for legacy CommonJS modules.

### B.3 — Boot validator coverage

`platform/config/feeComplianceInvariant.js` will automatically pick up the new check via `getComplianceCheckedTypes()` (which reads `Object.keys(REQUIRED_CHECKS)`). No changes needed there.

---

## Appendix C — Wallet DID Canonicalisation Helper

A minimal helper that converts BIPCircle's stored bare addresses to the W3C DID format AML Gate expects. Place at `platform/utils/walletDid.js`.

```js
/**
 * Canonical wallet DID conversion.
 *
 * BIPCircle stores raw chain-native addresses (XRPL r-addresses, EVM
 * 0x-addresses) in the `walletDID` field today. AML Gate's wire format
 * expects W3C DID Method URIs (did:xrpl:r..., did:eth:0x...).
 *
 * This helper is the boundary translator. Call it whenever a wallet
 * identifier crosses the BIPCircle → AML Gate boundary, and on its
 * way back when reading AML Gate responses.
 *
 * Storage layer is unchanged — we add canonical form at the wire
 * boundary, not at write time. See OpenKYCAML wiring brief §7
 * (Option C).
 */

const XRPL_RE = /^r[1-9A-HJ-NP-Za-km-z]{24,34}$/;
const EVM_RE = /^0x[0-9a-fA-F]{40}$/;
const BTC_RE = /^(tb1|bc1|[123mn])[a-zA-HJ-NP-Z0-9]{24,62}$/;

/**
 * Convert a chain + address pair to a W3C DID Method URI.
 *
 * @param {string} chain  — 'xrpl' | 'ethereum' | 'bitcoin'
 * @param {string} address
 * @returns {string} did:method:identifier
 * @throws if address shape doesn't match the chain
 */
export function toWalletDid(chain, address) {
  if (!address || typeof address !== 'string') {
    throw new Error(`toWalletDid: address required (got ${typeof address})`);
  }
  const trimmed = address.trim();
  switch (chain) {
    case 'xrpl':
      if (!XRPL_RE.test(trimmed)) {
        throw new Error(`toWalletDid: invalid XRPL address shape: ${trimmed}`);
      }
      return `did:xrpl:${trimmed}`;
    case 'ethereum':
    case 'eth':
      if (!EVM_RE.test(trimmed)) {
        throw new Error(`toWalletDid: invalid EVM address shape: ${trimmed}`);
      }
      // EIP-55 checksum normalisation could go here. For now we keep
      // the case as-given to match how it's stored.
      return `did:eth:${trimmed}`;
    case 'bitcoin':
      if (!BTC_RE.test(trimmed)) {
        throw new Error(`toWalletDid: invalid BTC address shape: ${trimmed}`);
      }
      return `did:btc:${trimmed}`;
    default:
      throw new Error(`toWalletDid: unsupported chain: ${chain}`);
  }
}

/**
 * Inverse of toWalletDid — extract the bare address from a DID URI.
 * Used when reading wallet identifiers BACK from AML Gate responses
 * (e.g. screening results that echo the wallet_did field).
 *
 * @param {string} did
 * @returns {{ chain: string, address: string }}
 */
export function fromWalletDid(did) {
  if (!did || typeof did !== 'string' || !did.startsWith('did:')) {
    throw new Error(`fromWalletDid: not a DID: ${did}`);
  }
  const parts = did.split(':');
  if (parts.length < 3) {
    throw new Error(`fromWalletDid: malformed DID: ${did}`);
  }
  const [, method, ...rest] = parts;
  const identifier = rest.join(':');
  const methodToChain = {
    xrpl: 'xrpl',
    eth: 'ethereum',
    btc: 'bitcoin',
  };
  const chain = methodToChain[method];
  if (!chain) {
    throw new Error(`fromWalletDid: unsupported DID method: ${method}`);
  }
  return { chain, address: identifier };
}

/**
 * Best-effort: accept either a bare address or a DID and always return
 * the canonical DID form. Useful at boundaries where we don't know
 * which form a caller has handed us.
 *
 * @param {string} chain
 * @param {string} addressOrDid
 * @returns {string}
 */
export function ensureWalletDid(chain, addressOrDid) {
  if (typeof addressOrDid === 'string' && addressOrDid.startsWith('did:')) {
    return addressOrDid;
  }
  return toWalletDid(chain, addressOrDid);
}
```

**Call sites that should use it (immediate):**
- `services/amlGateClient.js` — convert any wallet field on outbound requests
- New `routes/amlEvents.js` (Appendix A) — convert any wallet field on inbound events before passing to handler
- `services/idCircle.js` — convert when synthesising attestation responses
- `services/amlStatusSubscriber.js` — convert when reading `external_id` (if it carries a DID-shaped identifier)

**Test ideas for the helper:**
- Round-trip: `fromWalletDid(toWalletDid(chain, addr)) === { chain, address: addr }`
- Reject empty / null / wrong-shape input for each chain
- `ensureWalletDid` is idempotent on already-canonical input

---

## Appendix D — `amlStatusSubscriber.js` Merge Notes

After §3.4 the canonical schema is settled. This appendix lists the per-section reconciliation needed to merge the BIPCircle and AML-Gate template versions into one file.

**Target shape:** ESM, snake_case wire schema, BIPCircle behavioural model.

| Section | Action |
|---|---|
| Module preamble | Keep BIPCircle's ESM imports. Drop the `"use strict"` line and `require()` calls from the template. |
| Constants | Keep both — they don't conflict. Add `PROCESSED_EVENTS_COLLECTION = 'aml_processed_events'` (same value in both). |
| Validation | Replace `event.eventType !== 'aml.status_changed'` with `event.event !== 'customer.status_changed'`. Replace destructure with snake_case fields. Map at the top: `const userId = event.external_id; const fundTenantId = event.tenant_id; ...`. Keep BIPCircle's strict status enum check. |
| Tenant resolution | Add the `fund_tenant_members` lookup from the template (BIPCircle's version assumes the event already carries `fundTenantId`, which the canonical schema does not). |
| Dedupe | Keep BIPCircle's `db.runTransaction` claim — it's race-safe. Drop the template's two-step get/set. |
| Status cache write | Keep BIPCircle's full payload (includes `previousStatus`, `decisionId`, `jurisdictionPackVersion`, `matchedLists`, `rawPayload`). Add `risk_tier` from the template since it's in the canonical schema. |
| Audit log | Keep BIPCircle's `auditLog()` call — template doesn't have one. |
| MLRO case | Use BIPCircle's transactional throw-on-failure model (compliance-critical writes must retry). Use the template's case-type derivation from `fatal_flags` array (more accurate than BIPCircle's substring match on `reason`). |
| KYC revocation | Keep BIPCircle's direct `revokeOnchainClaims` call. Also write to `pending_kyc_revocations` for backstop processing — belt and braces. |
| Held tx release | Keep BIPCircle's paginated drain (template doesn't have one). |
| Heartbeat | Use `FieldValue.serverTimestamp()` from template (template's choice is more correct — server clock, not subscriber clock). Keep field names from template (`last_heartbeat`, `last_event_type`, `last_message_id`). |
| Module export | ESM `export async function handleAmlStatusEvent`. Drop CommonJS `module.exports`. |

**Estimated diff:** ~80 lines changed in BIPCircle's `amlStatusSubscriber.js`. The template file can then be **deleted from the AML-Gate repo** (or archived as a reference example) since the merged version lives in BIPCircle.

---

## Appendix E — Environment Variables to Set

Add to `bipcircle/api/.env.local`, `bipcircle/start-dev.sh`, and Cloud Run environment:

```bash
# AML Gate service-to-service
AML_GATE_URL=https://api-bmuvem3rrq-nw.a.run.app

# Pub/Sub topic + push subscription audience
PUBSUB_TOPIC_AML_EVENTS=aml-gate-events
PUBSUB_AML_AUDIENCE=https://bipcircle-api-390262355925.us-central1.run.app
PUBSUB_AML_PUBLISHER_SA=aml-gate-publisher@aml-gate.iam.gserviceaccount.com

# Optional tunables
AML_HIGH_VALUE_THRESHOLD_USD=10000
AML_HEARTBEAT_STALE_MS=300000
```

The `PUBSUB_AML_PUBLISHER_SA` value is a placeholder — replace with the actual service account chosen in §9 decision 4.

---

## Appendix F — End-to-End Smoke Test Plan

The success criterion for the meeting is **one clean and one blocked**. Everything else can defer.

### Test 1 — Cleared customer flows through

1. Create ID Circle attestation for a clean test user
2. Trigger AML Gate `/v1/screen` (sync mode)
3. AML Gate publishes `customer.status_changed` with `status: cleared`
4. BIPCircle `aml_status_cache/{userId}` updates to `cleared` within 2 seconds
5. User initiates USDT payment to a whitelisted address
6. `complianceGate.runAmlGateCheck()` reads cache, returns `pass`
7. Payment proceeds through saga, settles on sepolia
8. **Assert:** receipt has `feeAmount > 0`, MLRO case count unchanged

### Test 2 — Blocked customer is refused + MLRO case auto-created

1. Same user, AML Gate marks as `blocked` (sanctions match)
2. AML Gate publishes `customer.status_changed` with `status: blocked, fatal_flags: ["confirmed_sanctions_match"]`
3. BIPCircle cache updates within 2 seconds
4. `pending_kyc_revocations` queue gets a new entry
5. MLRO case created with `caseType: sanctions_match, priority: critical`
6. Same user attempts another USDT payment
7. `complianceGate.runAmlGateCheck()` returns `fail`
8. Route returns 403 "Compliance check failed" with blocker `AML_GATE_CLEARED`
9. **Assert:** no saga created, no receipt, MLRO case visible in MLRO dashboard

If both tests pass, the integration is wired end-to-end.

---

## Document Status

- **Version:** 1.0.0 (initial briefing)
- **Date:** 2026-04-11
- **Author:** Pre-meeting prep, BIPCircle team
- **Next revision:** After the Nick V meeting — fold in the §9 decisions and update §3.4 with the agreed canonical schema.
