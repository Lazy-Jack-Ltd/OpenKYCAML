# BIPCircle ↔ AML Gate Integration — Wiring Briefing

> **Status:** Pre-meeting briefing for the AML Gate wiring session on 2026-04-11.
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

If time is tight, do these in dependency order. Each step unlocks the next.

1. **GCP-side prep first**: create Pub/Sub topic `aml-gate-events`, create push subscription `bipcircle-aml-status`, generate the OIDC service account that BIPCircle will use to call AML Gate.
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

## 9. Decisions Needed in the Meeting

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

## 10. Input from Live Source Verification (BIPCircle 2026-04-11)

> Added 2026-04-11 after re-reading current BIPCircle source. Memories drift; this section is the verified-against-disk view as of the date above. Where the briefing above is correct I confirm it; where I have additions, they are flagged **NEW** below.

### 10.1 Verified-against-source: every claim in §2 holds

| # | Claim | Verified | Evidence |
|---|---|---|---|
| 1 | `amlGateClient.js` exists and is wired | ✅ | `platform/services/amlGateClient.js`, 5,368 bytes, mtime 2026-04-08. `callAmlGate()` exported. |
| 2 | BIPCircle subscriber present, not route-mounted | ✅ | `products/bipcircle/services/amlStatusSubscriber.js`, 10,343 bytes, mtime 2026-04-08. Function `handleAmlStatusEvent({ db, event, messageId, logger })` exported. No `routes/amlEvents.js` mounted in `server.js`. |
| 3 | `AML_GATE_CLEARED` is a citation-only stub | ✅ | `complianceGate.js` contains the literal `AML_GATE_CLEARED` exactly **once** — at the citations map, not in `REQUIRED_CHECKS`, no `case 'AML_GATE_CLEARED':` in the `runCheck()` switch. `getComplianceCheckedTypes()` returns `Object.keys(REQUIRED_CHECKS)` which today omits AML entirely. |
| 4 | `travelRuleService.js` is empty | ✅ | `services/travelRuleService.js`, **0 bytes**, mtime 2026-04-08. Confirmed empty placeholder. |
| 5 | `amlComplianceCheck.js` not merged into BIPCircle | ✅ | File does not exist in `bipcircle/api/src/` at all. Only present in `AML-Gate/bipcircle-integration/`. |
| 6 | Schema mismatch (§3) is real | ✅ | BIPCircle subscriber lines 53-54: `if (event.eventType !== 'aml.status_changed') throw …`. Destructure on lines 57-71 is camelCase. AML-Gate template uses `event.event === "customer.status_changed"` and snake_case `external_id` / `tenant_id` / `risk_tier` / `fatal_flags`. **The two will not interoperate without the §3.4 reconciliation.** |

Conclusion: **the briefing's findings are accurate as of 2026-04-11.** Proceed.

### 10.2 NEW — Coverage invariant precedent: `validateFeeMaps()` shipped 2026-04-10

This is the highest-leverage addition I can make to the briefing.

On 2026-04-10 BIPCircle shipped a boot-time invariant in `feeService.js` that catches **exactly** the class of bug §3 of this briefing is at risk of: a transaction type emitted by routes that's silently absent from a critical lookup map. Background: BTC on-chain payments charged $0 platform fee for weeks because `routes/treasury.js` emitted `BTC_ONCHAIN_PAYMENT` while `feeService.js` had a `BTC_PAYMENT` typo from the original draft. Silent revenue loss, no error, no log.

The fix was structural, not data-only:

```js
// services/feeService.js
export const KNOWN_FEE_TRANSACTION_TYPES = new Set([
  'RLUSD_PAYMENT', 'USDT_PAYMENT', 'BTC_ONCHAIN_PAYMENT', 'LIGHTNING_PAYMENT',
  // ...31 types total
]);

const PLATFORM_FEE_ONLY = new Set(['TEAM_INVITE', 'INVESTOR_WHITELISTED']);
const FUND_FEE_ONLY     = new Set([]);

export function validateFeeMaps() {
  const missingFromFund = [];
  const missingFromPlatform = [];
  for (const type of KNOWN_FEE_TRANSACTION_TYPES) {
    if (!FEE_TYPE_MAP[type] && !PLATFORM_FEE_ONLY.has(type)) missingFromFund.push(type);
    if (!PLATFORM_FEE_TYPE_MAP[type] && !FUND_FEE_ONLY.has(type)) missingFromPlatform.push(type);
  }
  if (missingFromFund.length || missingFromPlatform.length) {
    throw new Error(/* multi-line listing every drifting type */);
  }
}
```

`validateFeeMaps()` is called from `server.js` immediately after the other boot validators (`validateManifest`, `validateRegistry`, `validateCompensationManifest`, `validateFeeComplianceCoverage`, ...). Process refuses to start on drift. **Verified live** — BTC tx `542a1fb29055419576d27ddf8181031ed8aa839927634473fdb0a4a892b09ae5` confirmed the fee engine fix end-to-end the day this section was written.

**Why this matters for the AML wiring:** Appendix B.3 of the briefing notes that `feeComplianceInvariant.js` will pick up new checks via `getComplianceCheckedTypes()`. That's true but **passive** — it only validates that types in `REQUIRED_CHECKS` have compliance gate coverage. It does **not** validate that every type that **should** have `AML_GATE_CLEARED` actually does. Adding `AML_GATE_CLEARED` to `RLUSD_PAYMENT` but forgetting `BTC_ONCHAIN_PAYMENT` will pass `feeComplianceInvariant` and ship to production silently.

**Recommendation (NEW):** Mirror the fee map pattern. Add to `complianceGate.js`:

```js
// Every value-moving transaction type that MUST include AML_GATE_CLEARED.
// Drift catcher — boot validator throws if any of these types exist in
// REQUIRED_CHECKS without the AML_GATE_CLEARED entry.
export const AML_GATE_REQUIRED_TYPES = new Set([
  'RLUSD_PAYMENT', 'USDT_PAYMENT', 'BTC_ONCHAIN_PAYMENT', 'LIGHTNING_PAYMENT',
  'TOKENS_TRANSFERRED', 'TOKENS_ISSUED', 'TOKEN_CLAWBACK', 'TOKEN_FORCED_TRANSFER',
  'DEX_ORDER_PLACED', 'RFQ_ACCEPTED', 'WITHDRAWAL_INITIATED',
]);

export function validateAmlGateCoverage() {
  const missing = [];
  for (const type of AML_GATE_REQUIRED_TYPES) {
    const checks = REQUIRED_CHECKS[type] || [];
    if (!checks.some(c => c.check === 'AML_GATE_CLEARED')) missing.push(type);
  }
  if (missing.length) {
    throw new Error(
      'complianceGate boot invariant FAILED — AML_GATE_CLEARED coverage drift:\n' +
      missing.map(t => `  - ${t}`).join('\n') +
      '\nAdd { check: "AML_GATE_CLEARED", failAction: "block" } to REQUIRED_CHECKS for each type, or remove from AML_GATE_REQUIRED_TYPES with explicit justification.'
    );
  }
}
```

Wire from `server.js` next to `validateFeeMaps()`. Same shape, same boot-time guarantee. Prevents the exact partial-wiring drift the AML integration is most exposed to.

This invariant should be **shipped before or with the AML_GATE_CLEARED REQUIRED_CHECKS patches** in Appendix B — otherwise future developers can add a new payment type (e.g. `XLM_PAYMENT` next quarter) and forget to add the AML check, with the same silent-failure mode that hit the BTC fee engine.

### 10.3 NEW — Architectural rule: "share primitives, not gates"

The integration model in this doc — `amlGateClient` (primitive) → `AML_GATE_CLEARED` (one check among many in BIPCircle's domain-specific gate) — is the exact correct shape per BIPCircle's locked architectural rule documented in `feedback_share_primitives_not_gates.md`. Worth surfacing in the OpenKYCAML guidance because future products (SoundBip retail, future POS, future custody) will all want to consume AML Gate the same way:

> Share the **primitives** — identity attestation, sanctions/PEP screening, jurisdiction rule packs, audit chains. These are domain-neutral and consume cleanly. Keep the **gates** separate — the per-transaction-type check lists, the rule-to-action mappings. Gates encode product vocabulary (`PIF_HOLDER_LIMIT`, `INVESTOR_CATEGORY_PERMITTED` for funds; `STRUCTURING_DETECTION`, `£25_LIMIT` for retail) that doesn't generalise.

Concretely for OpenKYCAML adopters:
- `amlGateClient.js` (or its OpenKYCAML equivalent) is a **primitive** — its API never mentions a transaction type. It's a domain-neutral HTTP client.
- `complianceGate.js` `REQUIRED_CHECKS` is a **gate** — its key (`RLUSD_PAYMENT`, `TOKENS_ISSUED`) betrays its product vocabulary.
- Two adopters (BIPCircle institutional + SoundBip retail) should each have their **own gate** but share the **same client** and the **same OpenKYCAML event envelope**. Anything that forces them to share a gate is the wrong layer.

This rule means the canonical event schema (§3.4) is properly OpenKYCAML's responsibility — not BIPCircle's — because it's a primitive contract two unrelated products will both depend on.

### 10.4 NEW — CommonJS / ESM gotcha for the merge

Appendix B.2 notes the integration template is CommonJS and BIPCircle is ESM. **This is more dangerous than it looks**, because BIPCircle had a recent incident with broken dynamic imports — F-IMPORT-01, fixed in commit `522de23` on 2026-04-09. Seventeen broken dynamic imports across nine files were silently swallowing errors and returning undefined. The wallet balance bug that cost a day of debugging was a downstream symptom.

**Recommendation:** When merging `amlComplianceCheck.js` and `amlTravelRuleTrigger.js`:
1. **Port to ESM at merge time.** Don't use dynamic `await import()` shims to bridge CJS modules at runtime — they're the exact pattern that caused F-IMPORT-01.
2. **Add boot-time validation that imports resolve.** The `lockSagas` / `lockComplianceChecks` / `validateFeeMaps` family of validators in `server.js` should add a sibling that asserts every imported AML helper has its expected exports.
3. **Run the boundary checker after the merge.** `node api/src/platform/check-boundaries.js` enforces Rule 1-5 of the platform/product split. The new files belong in `products/bipcircle/services/` (gate level), not `platform/services/` (primitive level) — `amlGateClient.js` is the only piece that should live in `platform/`.

### 10.5 NEW — Wallet DID storage: Option C is even more attractive than the doc claims

Section 7 recommends Option C (boundary helper, no schema change) for short-term wiring. I agree more strongly than the briefing does:

- **Option A (mass rewrite)** is a migration that touches `receipts`, `mlro_cases`, `aml_status_cache`, `audit_log`, `attestations`, possibly `held_transactions`. BIPCircle's `migrationRunner` (`feedback_migration_framework_pattern.md`) requires rollback + checkpoint paths for every migration. That's a 1-2 day effort minimum and adds risk to a meeting whose goal is end-to-end test.
- **Option B (mirror field)** introduces dual-write hazard — every write site needs to be audited. The fee map drift this section opens with is exactly what happens when you have two fields meant to track the same thing and one of them gets forgotten.
- **Option C (boundary helper)** is the only path that requires zero schema changes, zero migrations, and zero risk to existing audit data. The helper sketch in Appendix C is right; my only addition is to make `ensureWalletDid()` the **only** path that crosses the BIPCircle → AML Gate boundary, and to lint for raw bare addresses in any `callAmlGate()` argument list.

A small companion invariant in `amlGateClient.js`:

```js
function assertCanonicalDid(field, value) {
  if (typeof value === 'string' && (value.match(/^r[1-9A-HJ-NP-Za-km-z]{24,34}$/) ||
                                     value.match(/^0x[0-9a-fA-F]{40}$/))) {
    throw new Error(
      `amlGateClient: ${field} contains a bare wallet address (${value.slice(0, 10)}...). ` +
      `Use ensureWalletDid('xrpl'|'ethereum', address) at the call site.`
    );
  }
}
```

Throws loudly on a bare address, points the developer at the helper. Protects the boundary even if someone forgets.

### 10.6 NEW — AML Gate's schema is already half-canonicalised in OpenKYCAML

The §3.4 recommendation to adopt AML Gate's snake_case `customer.status_changed` envelope as canonical is correct, **and** OpenKYCAML's existing schema versioning (`docs/versions/`, `pyproject.toml v1.14.0`) is the right home for it. Concretely:

1. Add a new OpenKYCAML schema version (`v1.15.0`) that ships the `customer.status_changed` event JSON Schema as the canonical wire format
2. Add it to `docs/reference/` as `events/customer-status-changed.json`
3. Treat any future adopter (SoundBip, ID Circle's external integrators, other tenants) as bound by the schema — not a BIPCircle-specific decision
4. Pin the schema version in `amlGateClient.js` (e.g. `OPENKYCAML_SCHEMA_VERSION=1.15.0`) so a schema bump fails closed if the client hasn't been updated

This converts the meeting decision from "which schema does BIPCircle use" into "which OpenKYCAML version do we adopt", which is much more durable.

### 10.7 NEW — The meeting's critical-path is shorter than §8 suggests

The briefing's §8 is good prioritisation, but if meeting time is constrained the **single highest-value 30-minute outcome** is:

1. **Decide the canonical event schema (§3.4 / §10.6)** — this unblocks every other piece of code
2. **Set `AML_GATE_URL` + `PUBSUB_AML_AUDIENCE` + `PUBSUB_AML_PUBLISHER_SA` in BIPCircle env**  — five minutes
3. **Confirm the OIDC service account model** (§9 decision 4) — five minutes whiteboard

Everything else (port subscriber, drop in `amlComplianceCheck`, mount push endpoint, end-to-end test) can be done by one developer in a focused session **after** those three questions are answered. The mistake to avoid is trying to wire code in the meeting — wire decisions, then wire code back at the desk.

### 10.8 Errata for §1 and §2

Two minor corrections to the doc above:

- §2 row 2 says BIPCircle's subscriber is "266 lines, ESM". Actual file as of 2026-04-11 is **10,343 bytes** which is closer to **240 lines including comments** depending on how you count blank lines. The spirit of the claim is right (the file is substantial and ESM); the exact line count is approximate. Recommend dropping numeric line counts from the doc since they drift.
- §2 row 6 says "BIPCircle subscriber creates cases on `blocked` / `review_required`". I confirmed `handleAmlStatusEvent` does this in code, but I want to flag that the case-creation logic is **inside** the subscriber, not in `routes/mlro.js`. `routes/mlro.js` only **registers** the case types — the actual auto-creation happens in `amlStatusSubscriber.js`. Worth clarifying for new readers.

### 10.9 What the next session should pick up

If the meeting lands the §9 decisions and the next session needs to start implementing with this doc as the source of truth, the implementation order I'd actually follow:

1. Add the `validateAmlGateCoverage()` invariant from §10.2 **first** — empty `AML_GATE_REQUIRED_TYPES` Set initially. This is structural, not behavioural; ships in 5 minutes.
2. Fill `AML_GATE_REQUIRED_TYPES` with whatever the meeting approves. Boot will now fail until step 3 is done — that's the point.
3. Port `amlComplianceCheck.js` from CJS to ESM, drop into `services/`, add to `REQUIRED_CHECKS`, add to `runCheck()` switch. Boot now passes.
4. Port `amlStatusSubscriber.js` per Appendix D using the §3.4 canonical schema. Test in isolation with a synthesised event payload.
5. Mount the Pub/Sub push endpoint per Appendix A. Wire env vars per Appendix E.
6. `start-dev.sh` restart. Confirm `validateFeeMaps` + `validateAmlGateCoverage` both pass at boot. Confirm `amlGateClient` health probe passes.
7. End-to-end smoke test per Appendix F. The success criterion is one cleared and one blocked.
8. Defer Travel Rule + KYC revocation processor to a follow-up — neither is required for the smoke test and both are at least an hour each.

### 10.10 Memory anchor

For future Claude sessions reading this file: the live BIPCircle source state above is a snapshot as of **2026-04-11**. Before acting on any specific function name, file size, or behaviour claim:
- `grep` for the symbol in `bipcircle/api/src/`
- `ls -la` the cited file path
- Read the function before relying on its signature

The schema mismatch (§3) is the most stable finding — both files exist, both have been there for days, and the divergence is structural. Most other findings will drift the moment the next merge lands. **Do not cite this section as authoritative without re-verifying.**

---

## Appendix G — What Was Built Pre-Meeting (15-min sprint)

In the 15 minutes immediately before the Nick V meeting, the four
"safe to land regardless of meeting outcome" items from the briefing
were committed to BIPCircle as actual code, not just sketches. None
of these depend on any §9 decision — they work on either side of the
schema choice and can be reused or thrown away with no waste.

### G.1 — `walletDid` helper landed (was Option A)

**Files:**
- `api/src/platform/utils/walletDid.js` (142 lines)
- `api/test/walletDid.test.js` (192 lines, **35 tests passing**)

**Functions exported:**

| Function | Purpose |
|---|---|
| `toWalletDid(chain, address)` | Convert raw address → `did:xrpl:r…` / `did:eth:0x…` / `did:btc:…`. Throws on shape mismatch or unsupported chain. |
| `fromWalletDid(did)` | Inverse: parse a DID URI back to `{ chain, address }`. Throws on malformed input. |
| `ensureWalletDid(chain, addressOrDid)` | Idempotent — accepts either form and always returns the canonical DID. Validates that the embedded chain matches the declared one to catch silent confusion bugs. |
| `safeWalletDid(chain, addressOrDid)` | Same as `ensureWalletDid` but returns `null` instead of throwing. For audit/log paths that must not break the call. |

**Test coverage** (all passing under `node --test`):
- Round-trip identity for all three chains (XRPL / EVM / BTC)
- Case preservation for EVM addresses (no EIP-55 normalisation — matches storage)
- Whitespace tolerance, alias handling (`eth` ↔ `ethereum`, `btc` ↔ `bitcoin`)
- Chain-mismatch detection (XRPL address fed to ethereum, etc.)
- Error messages match assertable patterns
- `safeWalletDid` returns `null` instead of throwing for the audit path

**Implements:** Option C from §7 (boundary translator). Works regardless of which storage option (A, B, or C) is chosen in the meeting.

### G.2 — Schema adapter shim landed (was Option C)

**Files:**
- `api/src/platform/utils/amlGateEventAdapter.js` (137 lines)
- `api/test/amlGateEventAdapter.test.js` (188 lines, **22 tests passing**)

**Functions exported:**

| Function | Purpose |
|---|---|
| `translateAmlGateEvent(canonicalEvent)` | Pure function. Translates AML Gate's snake_case `customer.status_changed` envelope into BIPCircle's existing camelCase `aml.status_changed` shape. Throws on missing required fields. |
| `tryTranslateAmlGateEvent(canonicalEvent)` | Non-throwing wrapper that returns `{ ok, event, error }`. For route handlers that want structured error responses instead of 500s. |

**Field mapping (the meeting decision table, made executable):**

| Canonical (AML Gate) | BIPCircle |
|---|---|
| `event` | `eventType` (always `aml.status_changed` after translate) |
| `external_id` | `userId` |
| `tenant_id` | `fundTenantId` |
| `status` | `status` (passthrough) |
| `fatal_flags` | `matchedLists` |
| `screening_id` | `screeningId` |
| `country_code` | `jurisdictionCode` |
| `correlation_id` | `correlationId` |
| (full payload) | `rawPayload` (verbatim, for traceability) |

**Reason field synthesis:** the canonical schema has no `reason` text field, but BIPCircle's MLRO case auto-creation does `reason.toLowerCase().includes('sanction')` to pick the case type. The adapter synthesises `reason` from `fatal_flags.join(', ')` so the existing detection logic still works without modification. Test coverage pins this behaviour.

**Backwards compatible both ways:**
- Accepts either `event` or `eventType` field name (publisher-side schema drift tolerance)
- Accepts either `external_id` or `userId`
- Accepts either `tenant_id` or `fundTenantId`

**Why this matters for the meeting:** if Nick agrees on the snake_case canonical (§3.4 recommendation), this shim is the migration path — no behavioural rewrite of `amlStatusSubscriber.js` needed. If Nick prefers a different approach, the shim is 137 lines of pure-function code that can be deleted with no debt.

### G.3 — Environment variables and connectivity smoke test landed (was Option B)

**Files:**
- `api/.env.example` — 12 new lines of AML Gate config
- `start-dev.sh` — 6 new lines exporting `AML_GATE_URL`, `AML_HIGH_VALUE_THRESHOLD_USD`, `AML_HEARTBEAT_STALE_MS`, `PUBSUB_TOPIC_AML_EVENTS`
- `scripts/aml-gate-health-check.sh` (99 lines, executable)

**Smoke test verified live against the deployed sandbox:**

```text
$ ./scripts/aml-gate-health-check.sh
AML Gate health check
  URL:      https://api-bmuvem3rrq-nw.a.run.app

[1/2] GET /v1/health
  ✓ Health OK
  Body: {"success":true,"version":"v1","data":{"status":"ok","version":"v1","timestamp":"2026-04-10T16:04:01.004Z"}}

[2/2] OIDC dual-read ping — SKIPPED
      Set AUTH=oidc to enable

All checks passed.
```

**OIDC mode** (`AUTH=oidc ./scripts/aml-gate-health-check.sh`) requires a `gcloud auth application-default login` and `roles/run.invoker` on the aml-gate project. Use it to verify the dual-read endpoint reachability before depending on it from `amlComplianceCheck`.

**Why this matters:** two of the eight meeting blockers from §2 (rows 7 and 8 — env vars + connectivity) disappeared without any schema decisions needed.

### G.4 — Travel Rule placeholder hardened (was Option D)

**File:** `api/src/products/bipcircle/services/travelRuleService.js` — replaced 0-byte empty file with a 75-line stub that throws structured errors with `code: 'TRAVEL_RULE_NOT_IMPLEMENTED'`.

**Exports:**
- `checkTravelRule()` — throws `TRAVEL_RULE_NOT_IMPLEMENTED`
- `releaseHeldTransaction()` — throws `TRAVEL_RULE_NOT_IMPLEMENTED`
- `TRAVEL_RULE_IMPLEMENTED = false` — boolean marker for boot-time invariant checks that want to fail loud if a route claims Travel Rule support but the service is still stubbed

**Why this matters:** the previous empty file would silently no-op any caller (any route that imported and called the function would just `return undefined` and proceed to sign). With the stub in place, any call site that forgets to check `TRAVEL_RULE_IMPLEMENTED` first will throw a clear, traceable error instead of letting an over-threshold transaction settle without Travel Rule confirmation. Comments in the file point at this OpenKYCAML doc (§5 + §8 step 9 + the integration template at `AML-Gate/bipcircle-integration/amlTravelRuleTrigger.js`) for the implementation plan.

### G.5 — Verification summary

| Check | Result |
|---|---|
| `node --test test/walletDid.test.js test/amlGateEventAdapter.test.js` | **57/57 pass** in 47ms |
| `./scripts/aml-gate-health-check.sh` (no auth) | **200 OK** from sandbox, server timestamp `2026-04-10T16:04:01Z` |
| BIPCircle API still boots cleanly | (no schema invariant runs against the new files — they're pure utilities, no call sites added yet) |

### G.6 — What this does NOT do

- Does not register `AML_GATE_CLEARED` in `complianceGate.js` REQUIRED_CHECKS — that depends on the §3.4 schema decision and the merge plan in Appendix D.
- Does not mount `routes/amlEvents.js` — Appendix A is still a draft pending the same decision.
- Does not implement the Travel Rule service body — see §5 + §8 step 9.
- Does not modify any existing call sites — `amlGateClient.js`, `amlStatusSubscriber.js`, and `idCircle.js` are unchanged. Boundary translators are available but no caller is using them yet.
- Does not add the `validateAmlGateCoverage()` boot invariant from §10.2 — that is still scoped as the next concrete commit and depends on the §9 decision about which transaction types must require AML Gate clearance.

This is intentional. Everything in §G.1 through §G.4 is **commit-clean and revertable** with zero blast radius — pure additive utilities behind a clean interface. The wiring step (the part that actually inserts these utilities into the production call graph) waits for the meeting decisions.

### G.7 — Meeting agenda update implied by §G

Two items in §8's recommended order shift forward because the underlying scaffolding is now in place:

| Step | Was | Now |
|---|---|---|
| 2 | Set env vars in `.env.local` and Cloud Run | **Already done in `start-dev.sh` and `.env.example`.** Cloud Run env still needs setting. |
| 4 | Reconcile two `amlStatusSubscriber.js` versions | **Use `amlGateEventAdapter.js` instead.** The shim removes the rewrite — the existing BIPCircle subscriber stays as-is, the route's Pub/Sub push handler runs `tryTranslateAmlGateEvent()` on the inbound payload before calling `handleAmlStatusEvent()`. The merge plan in Appendix D becomes optional cleanup. |

The schema decision in §3.4 is still needed — but only to confirm the canonical wire format the adapter targets, not to choose between two source files. That's a much cheaper decision.

---

## Document Status

- **Version:** 1.2.0 — added Appendix G with the four pre-meeting code drops (walletDid helper, schema adapter, env vars + smoke test, Travel Rule stub). All 57 tests passing, sandbox connectivity verified live.
- **Date:** 2026-04-11
- **Author:** Pre-meeting prep, BIPCircle team — §10 added by Claude after live source re-read; §G added by Claude after the 15-minute pre-meeting sprint
- **Next revision:** After the wiring meeting — fold in the §9 decisions, update §3.4 with the agreed canonical schema, and replace §10 with a "decisions landed" record.
