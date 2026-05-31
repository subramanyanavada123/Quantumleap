# QuantumGuard HNDL Risk Observatory
## Concept, Reasoning, and Scoring Engine Design

*A self-contained explainer. Anyone reading this — engineer, investor, or security lead — should be able to understand what we are building, why, how the score works, and what is still unsolved, without any prior context.*

Version 0.2 · Working design document

---

## 1. What this document is

This document explains, end to end:

1. The real-world problem we are solving and the vocabulary needed to follow it.
2. What QuantumGuard does, and just as importantly, what it deliberately does *not* do.
3. The honest competitive and regulatory landscape we are entering.
4. The core engine — the Quantum Exposure Score (QES) — explained input by input, with the math, default weights, worked examples, and the reasoning behind every design choice.
5. What parts of this are genuine research and development versus commodity engineering we should buy or integrate.
6. The hard problems that are still unsolved, stated plainly.

Nothing here is hand-waved. Where a number or weight appears, the reasoning behind it is given.

---

## 2. The problem, in plain terms

### 2.1 Why "post-quantum" is a real deadline, not science fiction

Almost all of today's secure communication relies on two families of public-key cryptography:

- **RSA** — security rests on the difficulty of factoring very large numbers.
- **ECC** (elliptic-curve cryptography) — security rests on a related hard math problem.

A sufficiently powerful quantum computer running **Shor's algorithm** can solve both of these problems efficiently. When such a machine exists — referred to as a *cryptographically relevant quantum computer*, or CRQC — RSA and ECC are not weakened, they are broken outright.

This is why standards bodies have set firm dates. NIST's roadmap (Internal Report 8547) designates the common public-key algorithms (RSA-2048, ECC P-256) for **deprecation after 2030** and the **disallowance of all quantum-vulnerable public-key algorithms after 2035**, aligned with U.S. National Security Memorandum 10. The NSA's CNSA 2.0 suite requires national-security systems to begin adopting quantum-resistant cryptography for new acquisitions as early as **2027**. These dates are widely treated as de facto mandates for regulated industries such as finance and healthcare.

The replacement algorithms already exist and are standardized: **ML-KEM** (key exchange), **ML-DSA** and **SLH-DSA** (signatures), with **HQC** as a backup key-exchange mechanism. The cryptography problem is essentially solved. The *operational* problem — migrating thousands of real systems before the deadline — is not.

### 2.2 Symmetric cryptography is mostly fine — this matters

Not all cryptography is equally threatened, and getting this distinction right is central to everything we do.

- **Asymmetric / public-key (RSA, ECC, Diffie-Hellman, ECDSA):** broken by Shor's algorithm. Catastrophic. These are the real targets.
- **Symmetric (AES) and hashes (SHA-2/3):** only mildly affected by **Grover's algorithm**, which gives a quadratic speedup. In practice this means AES-256 retains roughly 128 bits of effective security — still completely safe. AES-128 is weakened but generally still acceptable. Hash collision resistance is halved.

So an asset encrypted with AES-256 is essentially *not* a quantum problem, no matter how sensitive it is. An asset protected by RSA is a quantum problem even if it seems mundane. Any honest scoring model must treat the algorithm family as a hard gate, not just another weighted input. (Our model does — see Section 6.)

### 2.3 Harvest-Now-Decrypt-Later (HNDL)

An attacker does not need a quantum computer *today* to threaten data *today*. They only need to copy encrypted data now and store it. When a CRQC arrives, they decrypt the stored copy.

This means the threat is already live for any data that:

- is being intercepted or exfiltrated now (in transit, in cloud storage, in backups), **and**
- must remain confidential for years into the future.

Examples that fit both conditions: financial transaction archives, customer identity records, wallet backup vaults, long-term regulatory records, CBDC infrastructure traffic.

### 2.4 The other half of the threat: "Trust-Now-Forge-Later"

HNDL is about **confidentiality** — secrets being read later. But quantum computers also break **signatures and authentication**. You cannot "harvest" a future signature, but you *can* wait until a CRQC lets you forge one. The risk applies to:

- Root certificate authorities and PKI with long validity periods.
- Code-signing and firmware-signing keys (firmware may need to verify as trustworthy for 15–20 years).
- Identity systems and transaction-authorization keys.
- In digital-asset custody specifically, the signatures protecting funds on a blockchain.

A platform that scores only the confidentiality side misses an entire — and arguably more operationally urgent — class of risk. Our engine covers both (Section 6.6).

---

## 3. What QuantumGuard is trying to do

### 3.1 The one-sentence purpose

> QuantumGuard identifies which cryptographic assets are most exposed to quantum attack, and produces a defensible, risk-ranked roadmap for the order in which they should be migrated.

### 3.2 The core insight

Most organizations cannot answer a simple question: *"Of our thousands of certificates, keys, databases, and tunnels — which do we fix first?"*

Discovery tools tell you **where** cryptography exists. They increasingly do not tell you, in a rigorous and auditable way, **what to migrate first and why**. QuantumGuard exists to answer that question with a transparent number a CISO can defend to a board or a regulator.

### 3.3 What we explicitly do NOT do

- We do **not** perform the cryptographic migration itself. We tell you where to point your migration effort.
- We do **not** invent new cryptography. We use the standardized PQC algorithms as the destination.

This narrow scope is a feature. It keeps the product focused and the value proposition clear.

### 3.4 Initial target market

BFSI and digital-asset custody — crypto exchanges, custodians, banks, fintechs, and CBDC pilot environments — because they hold long-lived, high-value encrypted assets that are the textbook HNDL target, and because they face the heaviest regulatory pressure.

---

## 4. The honest competitive reality

This is important and must not be glossed over. An early version of the concept claimed: *"Existing tools answer 'what cryptography do you have'; we answer 'what to migrate first.'"*

**As of 2026 that distinction no longer holds.** Risk-based prioritization is now a standard claim across the market. Vendors including Encryption Consulting, SafeLogic, Fortanix, QuSecure, IBM Quantum Safe, SandboxAQ, InfoSec Global, Keyfactor, and Venafi all offer discovery plus some form of prioritization. SafeLogic, for example, already frames its model around exactly the two axes we use — Harvest-Now-Decrypt-Later for confidentiality and Trust-Now-Forge-Later for authentication.

The implication: **"we prioritize" is table stakes, not a differentiator.** Our defensible edge has to come from one or both of:

1. **Rigor and auditability of the score** — a methodology a regulator will accept, not a proprietary black box.
2. **Deep verticalization into BFSI / custody** — data-lifetime modeling, signature-forgery risk, and regulatory mappings tuned to that sector specifically.

We should stop selling "prioritization" and start selling *defensibility* and *depth*.

---

## 5. The core engine: Quantum Exposure Score (QES)

Every discovered cryptographic asset receives a score from **0 to 100**. Higher means migrate sooner. The score is built to be explainable: every point traces back to a factor a reviewer can interrogate.

### 5.1 The guiding principle — Mosca's inequality

The accepted academic framework for *timing* this risk is **Mosca's inequality**. You have a problem when:

> **X + Y > Z**

where:

- **X** = how long the protected thing must stay secure (years).
- **Y** = how long migrating this asset will take (years).
- **Z** = how long until a CRQC exists (years).

The intuition: if it takes you `Y` years to migrate, and the data must stay safe for `X` years, then you must finish migrating `X + Y` years of protection before the quantum threat arrives at year `Z`. If `X + Y` exceeds `Z`, you are already behind.

We define the **exposure gap**:

> **G = X + Y − Z**

A positive `G` means this asset is genuinely at risk and worth an attacker's effort to harvest today.

### 5.2 The three timing inputs, explained

| Term | Meaning | Where it comes from |
|------|---------|--------------------|
| **X** — shelf-life | Years the data must stay confidential (HNDL track) **or** years the key/cert must stay unforgeable (authentication track) | Data classification, retention policy, certificate validity. *This is the hardest input to obtain automatically — see Section 7.* |
| **Y** — migration time | Years to re-tool this specific asset | A complexity tier (Section 6.4) |
| **Z** — threat horizon | Years until a CRQC | A **user-set parameter**, not a baked-in constant. This is deliberate — see below. |

**Why Z is user-set:** nobody knows when a CRQC will arrive. Hard-coding a single guess would make the whole score look arbitrary. Instead the user picks a posture:

- **Defender-conservative:** ~4 years (assume it comes soon, around 2030).
- **Moderate:** ~9 years (around 2035, NIST's disallowance line).
- **Optimistic:** ~14 years (around 2040).

The product should show how scores shift across these scenarios. That sensitivity *is* part of the analysis, not a weakness to hide.

---

## 6. The QES formula, factor by factor

The score is a **gate multiplied by a weighted sum**:

> **QES = 100 × V_alg × ( w_T·T + w_I·Impact + w_E·E )**

Each of the four factors lives on a 0-to-1 scale. We walk through each one.

### 6.1 V_alg — the quantum vulnerability gate

This encodes the Shor-versus-Grover distinction from Section 2.2. It is a *gate*: if the algorithm is quantum-safe, this factor is near zero and the entire score collapses — which is the correct behavior. A perfectly safe AES-256 asset should never score as a quantum risk, however sensitive or exposed it is.

| Algorithm class | V_alg | Why |
|---|---|---|
| RSA, DH, DSA, ECC, ECDH, ECDSA — any key size | 1.00 | Shor gives a polynomial-time break |
| Unknown / proprietary / no encryption | 1.00 | Conservative worst-case default |
| AES-128, 3DES, SHA-256 used for collision resistance | 0.30 | Grover/BHT erodes the margin |
| AES-192/256, SHA-384/512, SHA-3 | 0.05 | Grover leaves ample margin |
| Classical + PQC hybrid / composite | 0.10 | Small residual transitional risk |
| Pure PQC (ML-KEM, ML-DSA, SLH-DSA, HQC) | 0.00 | Quantum-resistant |

### 6.2 E — harvestability / exposure

Can an adversary actually collect the protected material today? HNDL only works if the ciphertext can be captured.

| Exposure profile | E |
|---|---|
| Public-internet facing / in transit over the open internet | 1.00 |
| Cloud-at-rest, off-prem backup, or third-party/partner link | 0.70 |
| Internal network only | 0.40 |
| Air-gapped / isolated enclave | 0.15 |

Note the internal-only floor is 0.40, not 0 — insiders, breaches, and lateral movement mean "internal" is not "unreachable."

### 6.3 Impact — business criticality

How bad is it if this asset is compromised?

| Classification | Impact |
|---|---|
| Regulated PII, financial records, key-encrypting keys, root trust | 1.00 |
| Confidential business / customer data | 0.70 |
| Internal operational | 0.40 |
| Public / non-sensitive | 0.10 |

Shared roots of trust (a root CA, a key that wraps other keys) should be set to 1.00 regardless of their nominal classification, because their blast radius is the entire estate. (A future version computes this automatically — see Section 7.)

### 6.4 Y — migration effort tiers

These feed the timing term:

| Asset type | Y (years) |
|---|---|
| Software config change / certificate reissue | 0.5 |
| Application / library upgrade | 1.5 |
| Protocol / infrastructure / PKI change | 3.0 |
| Hardware, HSM, embedded/OT, or third-party-gated | 5.0 |

### 6.5 T — the timing factor (Mosca made continuous)

Mosca's inequality is binary (you are either past the line or not). For a smooth 0–100 score we convert the gap `G` into a continuous factor with a logistic curve:

> **T = 1 / (1 + e^(−G / τ))**, with **τ ≈ 3 years**

- `G = 0` (right on the boundary) → T = 0.50
- `G = +8` → T ≈ 0.93
- `G = −7` → T ≈ 0.10

The smoothing constant `τ` is not arbitrary: it represents our genuine uncertainty about `Z`. A sharp cliff at `G = 0` would falsely imply we know the threat date precisely. The gentle slope reflects that we do not.

### 6.6 The authentication track — same skeleton, two swapped inputs

To cover Trust-Now-Forge-Later (Section 2.4), keep the identical formula and reinterpret two inputs:

- **X becomes the trust/validity lifetime** — how long the key or certificate must remain unforgeable. A root CA valid until 2040 has a large X, which correctly produces a high T.
- **E becomes forgeability exposure** — is the public key observable, and does it authenticate things an attacker would want to forge (firmware, transactions, identities)?

`V_alg` and `Impact` are unchanged. The fact that one engine handles both risk classes by changing only the *meaning* of two inputs — not the math — is a sign the framework is sound.

### 6.7 Default weights and priority bands

Default weights (tunable, then re-normalized so they sum to 1):

| Weight | Default | Why |
|---|---|---|
| w_T (timing) | 0.50 | Timing is the quantum-specific signal; it should dominate |
| w_I (impact) | 0.30 | Severity of compromise |
| w_E (exposure) | 0.20 | Harvestability |

Priority bands:

| QES | Band |
|---|---|
| ≥ 80 | CRITICAL |
| 60 – 79 | HIGH |
| 35 – 59 | MEDIUM |
| 15 – 34 | LOW |
| < 15 | NEGLIGIBLE |

### 6.8 Why "gate × weighted sum" and not a flat weighted sum

A naive risk score adds everything up: `risk = w1·algorithm + w2·exposure + w3·impact + ...`. That structure is wrong for quantum risk because it would still award points to an AES-256 asset for being sensitive and internet-facing — even though AES-256 has essentially no quantum exposure. Multiplying by the `V_alg` gate forces quantum-safe assets to near zero, which is correct. Keeping the *other* three factors as a weighted sum (rather than also multiplying them) keeps the score interpretable — you can say "half the score is timing, a third is impact, a fifth is exposure" — and avoids over-collapsing assets that are merely low on one axis. The structure is the design's most important single decision.

---

## 7. Worked examples

These reproduce the two examples from the original concept, validating the model against intuitions we already trust.

### Example A — customer archive database

- Algorithm: RSA-2048 → **V_alg = 1.00**
- Exposure: internet-facing → **E = 0.90**
- Impact: customer PII → **Impact = 1.00**
- Shelf-life **X = 15 y**, migration **Y = 2 y**, threat horizon **Z = 9 y** (moderate)
- Gap **G = 15 + 2 − 9 = 8** → **T = 0.93**

> QES = 100 × 1.00 × (0.5·0.93 + 0.3·1.00 + 0.2·0.90) = **≈ 95 → CRITICAL**

(The original concept hand-assigned this asset a 94. The model reproduces it.)

### Example B — internal temporary cache

- Algorithm: AES-256 → **V_alg = 0.05**
- Exposure: internal only → **E = 0.40**
- Impact: low-value cache → **Impact = 0.30**
- Shelf-life **X = 1 y**, migration **Y = 0.5 y**, **Z = 9 y**
- Gap **G = 1 + 0.5 − 9 = −7.5** → **T ≈ 0.08**

> QES = 100 × 0.05 × (0.5·0.08 + 0.3·0.30 + 0.2·0.40) = **≈ 1 → NEGLIGIBLE**

The original concept gave this a 12. Our model says ~1. Both are bottom-tier, and a near-zero *quantum* score for AES-256 is the more defensible answer — the gate is doing its job.

---

## 8. What is genuine R&D versus commodity engineering

A clear-eyed split of where to spend scarce research effort versus where to integrate existing tools.

### 8.1 Genuine R&D — this is where the defensible IP lives

1. **The scoring model itself** — a formal, calibrated, auditable QES anchored to Mosca and to NIST IR 8547, with `Z` parameterized and validated against expert judgment. This is the product.
2. **Confidentiality-requirement / data-lifetime inference (the X term).** Deriving "this data must stay secret for 15 years" automatically from classification tags, schema and table names, retention policies, and regulatory mappings. Hard, novel, and the input everyone else fudges.
3. **Migration-effort estimation (the Y term).** Modeling how costly and slow an asset is to migrate — protocol constraints, library and hardware dependencies, third-party blockers. Without it you cannot truly sequence.
4. **Dependency / blast-radius graph.** An asset's true risk depends on what relies on it; a root CA or a shared key-wrapping key should propagate its exposure to everything beneath it. Graph-based propagation is research-flavored and a real differentiator.
5. **The authentication / forge-later scoring axis**, tuned for custody and CBDC where signature forgery is the headline threat.

### 8.2 Commodity engineering — integrate or buy, do not invent

- TLS endpoint scanning.
- Certificate discovery (Venafi/Keyfactor territory).
- Basic algorithm inventory.
- The dashboard and reporting UI.
- **CBOM (Cryptography Bill of Materials) serialization.** The CycloneDX standard already exists. Implement it — and make it the *native output format* of the scoring engine from day one, not a late add-on, because compliance buyers want machine-readable inventory that drops into their existing governance tooling.

---

## 9. The hard problems that are still unsolved

Stated honestly, so they are planned for rather than discovered painfully later.

1. **The X input has no automated source.** Shelf-life and trust-lifetime drive the whole score, and a crypto scanner cannot read them off the wire — they are data-governance facts. Early pilots that rely on hand-entered X values will quietly become consulting engagements. That is an acceptable wedge, but plan for it.

2. **There is no ground truth for calibration.** Nobody can prove an asset "will be decrypted in 2034." The score's credibility therefore comes entirely from a transparent, parameterized, auditable methodology — never from a proprietary black box. Keep a record of calibration decisions; that record is the evidence.

3. **Discovery is genuinely hard for data at rest.** You often cannot tell which algorithm encrypted a stored blob from outside the system, and key material in third-party SaaS is largely invisible.

4. **The market is already crowded.** Differentiation must come from depth and defensibility, not from the prioritization claim itself (Section 4).

---

## 10. Suggested phased roadmap

**Phase 1 — defensible core**
- Manual asset onboarding.
- The QES engine exactly as specified here, with the `Z` threat-horizon parameter and tunable weights.
- Dashboard and ranked migration plan.
- CBOM-native output from the start.

**Phase 2 — reduce the manual burden**
- Automated discovery: TLS/endpoint scanning, certificate stores, KMS/HSM key inventory.
- First attempts at data-lifetime (X) inference from classification and retention sources.
- Dependency graph for blast-radius propagation into the Impact factor.

**Phase 3 — continuous and integrated**
- Continuous monitoring and re-scoring.
- Migration-effort (Y) modeling.
- Enterprise GRC integrations and compliance-report exports aligned to NIST IR 8547, CNSA 2.0, and sector regulators.

---

## 11. Glossary

- **PQC** — post-quantum cryptography; algorithms resistant to quantum attack.
- **CRQC** — cryptographically relevant quantum computer; one powerful enough to break RSA/ECC.
- **HNDL** — Harvest-Now-Decrypt-Later; capturing encrypted data today to decrypt once a CRQC exists.
- **Trust-Now-Forge-Later** — the signature/authentication analogue: waiting to forge signatures once a CRQC exists.
- **Shor's algorithm** — quantum algorithm that breaks RSA, ECC, and Diffie-Hellman.
- **Grover's algorithm** — quantum algorithm giving a quadratic speedup against symmetric crypto; only mildly threatening (AES-256 stays safe).
- **Mosca's inequality** — `X + Y > Z`; the standard timing test for quantum risk.
- **ML-KEM / ML-DSA / SLH-DSA / HQC** — the standardized post-quantum algorithms.
- **CBOM** — Cryptography Bill of Materials; a machine-readable inventory format (CycloneDX).
- **QES** — Quantum Exposure Score; our 0–100 per-asset risk-and-priority score.
- **V_alg, E, Impact, T** — the four factors of the QES (vulnerability gate, exposure, business impact, timing).
- **X, Y, Z** — shelf-life/trust-lifetime, migration time, and threat horizon, from Mosca's inequality.

---

*This is a working document. The factor tables, weights, and bands are starting points to be calibrated against real assets; every one of them is a tunable knob, and the calibration record is itself the artifact that makes the score defensible.*
