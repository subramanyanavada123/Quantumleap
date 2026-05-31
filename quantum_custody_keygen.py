# quantum_custody_keygen.py
import hashlib
import secrets
from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from fips203 import ML_KEM_768, Seed

app = FastAPI(
    title="QuantumGuard KeyGen",
    description="Quantum-seeded post-quantum key generation service for custody systems.",
    version="0.1.0",
)

SIMULATOR = AerSimulator()
WEAK_SEED_SPACE = 1 << 16
DEMO_WEAK_PREFIX = b"quantumguard-weak-demo-"


def get_quantum_seed(num_bytes: int = 64) -> bytes:
    qc = QuantumCircuit(16, 16)
    qc.h(range(16))
    qc.measure_all()

    tqc = transpile(qc, SIMULATOR)
    result = SIMULATOR.run(tqc, shots=512).result()
    counts = result.get_counts()

    raw = max(counts, key=counts.get)
    entropy = hashlib.sha512(raw.encode() + str(datetime.utcnow().timestamp()).encode()).digest()
    return entropy[:num_bytes]


def get_classical_seed(num_bytes: int = 64) -> bytes:
    return secrets.token_bytes(num_bytes)


def build_weak_seed(low_entropy_value: int, num_bytes: int = 64) -> bytes:
    material = DEMO_WEAK_PREFIX + low_entropy_value.to_bytes(2, "big")
    digest = hashlib.sha256(material).digest()
    return (digest * ((num_bytes + len(digest) - 1) // len(digest)))[:num_bytes]


def get_weak_seed(num_bytes: int = 64) -> bytes:
    low_entropy_value = secrets.randbelow(WEAK_SEED_SPACE)
    return build_weak_seed(low_entropy_value, num_bytes)


def get_hybrid_seed(num_bytes: int = 64) -> bytes:
    quantum_bytes = get_quantum_seed(num_bytes)
    classical_bytes = get_classical_seed(num_bytes)
    return bytes(a ^ b for a, b in zip(quantum_bytes, classical_bytes))


def seed_fingerprint(seed_bytes: bytes) -> str:
    return hashlib.sha256(seed_bytes).hexdigest()


def generate_pqc_key(seed_bytes: bytes) -> Dict[str, bytes]:
    seed = Seed(seed_bytes)
    kem = ML_KEM_768()
    public_key, secret_key = kem.keygen(seed)
    return {"public_key": public_key, "secret_key": secret_key}


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "service": "QuantumGuard KeyGen",
        "version": "0.1.0",
        "endpoints": "/generate-key, /recover-weak-seed-demo, /health",
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "QuantumGuard KeyGen",
        "quantum_simulator": "AerSimulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.post("/generate-key")
def generate_key(mode: str = Query("quantum", regex="^(quantum|classical|weak|hybrid)$")) -> Dict[str, Optional[str]]:
    if mode == "quantum":
        seed_bytes = get_quantum_seed()
        entropy_source = "quantum"
        warning = None
    elif mode == "classical":
        seed_bytes = get_classical_seed()
        entropy_source = "classical"
        warning = None
    elif mode == "weak":
        seed_bytes = get_weak_seed()
        entropy_source = "weak"
        warning = (
            "This mode uses intentionally low entropy for demonstration only. "
            "Do not use in production."
        )
    elif mode == "hybrid":
        seed_bytes = get_hybrid_seed()
        entropy_source = "hybrid"
        warning = (
            "Hybrid mode mixes quantum and classical entropy. "
            "It is safer than a pure weak seed, but quantum-only remains preferred."
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported mode")

    keypair = generate_pqc_key(seed_bytes)

    return {
        "mode": mode,
        "entropy_source": entropy_source,
        "public_key_hex": keypair["public_key"].hex(),
        "secret_key_fingerprint": hashlib.sha256(keypair["secret_key"]).hexdigest(),
        "seed_fingerprint": seed_fingerprint(seed_bytes),
        "warning": warning,
    }


@app.post("/recover-weak-seed-demo")
def recover_weak_seed_demo() -> Dict[str, object]:
    target_value = secrets.randbelow(WEAK_SEED_SPACE)
    target_seed = build_weak_seed(target_value)
    fingerprint = seed_fingerprint(target_seed)

    recovered_value = None
    attempts = 0
    for candidate in range(WEAK_SEED_SPACE):
        attempts += 1
        if seed_fingerprint(build_weak_seed(candidate)) == fingerprint:
            recovered_value = candidate
            break

    return {
        "status": "demo",
        "seed_fingerprint": fingerprint,
        "target_value": target_value,
        "recovered_value": recovered_value,
        "attempts": attempts,
        "warning": "This demo shows how a 16-bit entropy seed can be recovered by brute force.",
    }
