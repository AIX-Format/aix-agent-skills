# Skill: Topological Analyzer

## Purpose

Performs persistent homology analysis (Betti numbers H0/H1), Shannon entropy (H_EL < 0.9685 = Quranic signature), resonance coherence, and chiasmus (mirror symmetry) scoring.

## Constitutional Alignment

- **No Mocks**: Real Go engine computation, no simulated values
- **Verifiable**: All results backed by SHA-256 hashes

## Operational Flow

1. Agent sends text or data for analysis
2. Skill connects to Go engine or falls back to TypeScript implementation
3. Computes: Betti numbers, Shannon entropy, resonance coherence
4. Returns structured analysis result

## Failure Modes

| Mode | Detection | Recovery |
|------|-----------|----------|
| Go engine offline | Health check fails | Fallback to pure TS computation |
| Input too short | Length check | Request more data |
