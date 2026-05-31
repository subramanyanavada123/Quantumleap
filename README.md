**Project Documentation: QuantumGuard KeyGen**  
**Secure Quantum-Seeded Post-Quantum Cryptographic Key Generation for Crypto Custody**

---

### 1. Project Overview

**Project Name**: QuantumGuard KeyGen  
**Tagline**: "As Strong As Your Dice" – Making randomness the strongest link in post-quantum custody.

**Objective**  
Build a focused, production-ready micro-component that generates cryptographic keys for hot wallets and custodial systems using **quantum-derived entropy** seeded into **NIST FIPS 203 (ML-KEM-768)**. The primary goal is to eliminate weak entropy risks that currently threaten Indian crypto platforms.

**Target Users**  
- Indian crypto exchanges and custodians (WazirX, CoinDCX, Mudrex, etc.)
- Institutional digital asset custody providers
- RBI-regulated fintechs preparing for PQC migration

---

### 2. Problem Statement

**The Niche Pain Point**  
In Indian crypto custody platforms, hot wallet private keys (or API signing keys, withdrawal authorization keys) are often generated with insufficient entropy, especially in:

- Containerized/VM environments with delayed entropy pool initialization
- Peak load scenarios or auto-scaling clusters
- Mobile SDKs running on low-end Android devices
- Test/staging environments

**Real Impact**:
- Historical precedent: Debian OpenSSL (2008), Android SecureRandom (2013), and multiple Bitcoin wallet drains due to low-entropy keys.
- Even mathematically strong algorithms (ECDSA today, ML-KEM tomorrow) become worthless if the seed space is small.
- Regulatory pressure is rising: FIU-IND, RBI Innovation Hub, and National Quantum Mission are pushing quantum-safe practices.
- "Harvest Now, Decrypt Later" threat — encrypted wallets backed up today can be attacked later when quantum computers improve.

**Why This Niche is Worth Solving**:
- High financial stakes (real money under custody)
- Differentiated value proposition in a crowded market
- Local advantage: Bengaluru is home to QNu Labs (QRNG hardware)

---

### 3. Solution Summary

**Core Idea**  
Replace opaque classical entropy sources with **verifiably strong quantum entropy** to seed FIPS 203 ML-KEM-768 key generation.

**Key Features**
1. **Quantum Entropy Module** – Uses quantum circuit (Hadamard superposition + measurement) via Qiskit.
2. **PQC Key Generation** – Strict adherence to FIPS 203 using proper 64-byte seed (d || z).
3. **Weak Seed Attack Demonstrator** – Educational & security testing tool.
4. **Hybrid Mode** – Quantum + classical fallback.
5. **API-First Design** – Easy integration into existing custody systems.

**Non-Goals** (Scope Control)
- Not building a full custody/wallet system
- Not replacing HSMs entirely (complements them)
- Not claiming full quantum advantage yet (simulation-first)

---

### 4. Architecture

**High-Level Flow**

```
Client / Custody System
        ↓
QuantumGuard KeyGen Service (FastAPI)
        ├── Entropy Source
        │    ├── Quantum Circuit (Qiskit Aer / Real QRNG)
        │    └── Classical fallback (secrets + system entropy)
        └── Key Derivation
             └── FIPS 203 ML-KEM-768 KeyGen (with explicit seed)
        ↓
Return: Public Key + Key Fingerprint + Entropy Metadata
```

**Components**:
- **Entropy Layer**: Quantum circuit (16+ qubits) → SHA-512 extractor
- **Crypto Layer**: `fips203` or `pqc` library
- **Service Layer**: FastAPI + Uvicorn
- **Observability**: Entropy quality metrics, audit logs

---

### 5. Technical Stack

| Layer              | Technology                          | Reason |
|--------------------|-------------------------------------|--------|
| Quantum Simulation | Qiskit + Qiskit Aer                 | Mature, free, easy IBM Quantum integration |
| PQC Implementation | fips203 (Python)                    | Pure FIPS 203 compliant |
| API Framework      | FastAPI                             | Fast, modern, excellent docs |
| Security           | hashlib, secrets, cryptography      | Standard & audited |
| Future QRNG        | QNu Labs API / ID Quantique        | Local Bengaluru option |

---

### 6. Honest Constraints & Hiccups

| Issue                      | Status / Impact                              | Mitigation |
|---------------------------|----------------------------------------------|----------|
| Simulator is classical    | Not truly quantum (deterministic)           | Clearly document; upgrade path to real QRNG hardware/API |
| Performance               | Slower than pure classical (~100-500ms/key) | Acceptable for key generation (not per-transaction) |
| Real Hardware Access      | Requires token/queue time or paid QRNG      | Start with simulator; add paid tier |
| Regulatory Acceptance     | No specific mandate yet for QRNG            | Position as "best practice" & future-proof |
| Entropy Certification     | Hard to formally certify in PoC             | Add statistical tests (NIST SP 800-90B) |
| Library Maturity          | fips203 is good but young                   | Add comprehensive testing |

**Risk Level**: Medium. The biggest technical risk is over-reliance on simulator. The biggest business risk is integration friction with legacy custody systems.

---

### 7. Implementation Roadmap

**Phase 0: Foundation (1 week)**
- Setup repo, documentation, basic quantum entropy function
- Working ML-KEM keygen with quantum seed

**Phase 1: Core PoC (2 weeks)**
- FastAPI service
- Quantum vs Weak seed modes
- Brute-force recovery demonstration
- Basic entropy quality dashboard

**Phase 2: Production Readiness (3-4 weeks)**
- Hybrid mode + fallback
- Logging & audit trail
- NIST randomness tests
- Docker + Helm packaging

**Phase 3: Commercialization**
- Integration with QNu Labs QRNG
- Client SDKs (Python, Go)
- Compliance documentation for RBI/FIU

---

### 8. Success Metrics

- Successful generation of ML-KEM keys from quantum entropy
- Public demonstration of weak seed recovery in < 5 seconds
- Entropy quality passing basic statistical tests
- Clean integration test with a mock custody flow

---

### 9. Developer Setup Guide

**Prerequisites**
- Python 3.11+
- IBM Quantum token (optional)

**Installation**
```bash
git clone <repo>
cd quantumguard-keygen
pip install -r requirements.txt
```

**Running**
```bash
uvicorn quantum_custody_keygen:app --reload
```

**Implemented API Endpoints**
- `GET /` — service overview
- `GET /health` — runtime health check
- `POST /generate-key?mode=quantum` — quantum entropy seeded ML-KEM key generation
- `POST /generate-key?mode=classical` — classical entropy mode
- `POST /generate-key?mode=hybrid` — quantum + classical entropy mix
- `POST /generate-key?mode=weak` — intentionally weak entropy demo mode
- `POST /recover-weak-seed-demo` — brute-force recovery demo for weak-seed attack awareness

---

**Next Actions (Recommended)**

1. Approve this document scope
2. Create GitHub repository
3. Start building Phase 0 code together

---

This documentation is focused, realistic, and ready to be turned into a working product. It targets a genuine pain point in the Indian fintech/crypto space where quantum + PQC delivers clear value.

Would you like me to:
- Expand any section?
- Create the full `requirements.txt` and folder structure?
- Write the detailed API specification?
- Start writing the actual code files?

Let me know how you want to proceed.