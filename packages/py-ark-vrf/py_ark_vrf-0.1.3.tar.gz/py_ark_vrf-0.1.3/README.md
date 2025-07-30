# py-ark-vrf

Python bindings for ark-vrf - A comprehensive library for Verifiable Random Functions (VRF) based on elliptic curve cryptography, built on the [Arkworks](https://github.com/arkworks-rs) framework.

## Features

This library provides three VRF schemes:

- **IETF VRF**: ECVRF implementation compliant with [RFC9381](https://datatracker.ietf.org/doc/rfc9381)
- **Pedersen VRF**: Key-hiding VRF using Pedersen commitments
- **Ring VRF**: Zero-knowledge VRF with signer anonymity within a key set

All schemes are built on the **Bandersnatch** curve (Edwards curve on BLS12-381) and include automatic SRS file management.

## Installation

Install from PyPI:

```bash
pip install py-ark-vrf
```

The SRS (Structured Reference String) file required for Ring VRF operations is automatically bundled with the package - no manual setup required!

## Usage

### Basic VRF Operations

```python
import py_ark_vrf as vrf

# Create a secret key from a seed
secret_key = vrf.SecretKey(b"your-32-byte-seed-here-padding")
public_key = secret_key.public()

# Create VRF input from arbitrary data
vrf_input = vrf.VRFInput(b"Hello, VRF!")

# Get the VRF output (deterministic based on secret key and input)
output = secret_key.output(vrf_input)
output_hash = output.hash()  # 64-byte SHA-512 hash
```

### IETF VRF (RFC 9381)

```python
# Generate IETF VRF proof
ietf_proof = secret_key.prove_ietf(vrf_input)

# The proof contains the output and can be serialized
proof_bytes = ietf_proof.to_bytes()

# Anyone can verify the proof using the public key
# Note: verification methods would need to be implemented
```

### Pedersen VRF (Key-hiding)

```python
# Generate Pedersen VRF proof (hides which public key was used)
pedersen_proof = secret_key.prove_pedersen(vrf_input, aux_data=b"additional_context")

# Access the VRF output
vrf_output = pedersen_proof.output
output_hash = vrf_output.hash()
```

### Ring VRF (Anonymous)

```python
# Create a ring of public keys (including yours)
ring_size = 10
ring = []
for i in range(ring_size):
    if i == 3:  # Your position in the ring
        ring.append(public_key)
    else:
        other_sk = vrf.SecretKey(f"other-key-{i}".encode().ljust(32, b'\0'))
        ring.append(other_sk.public())

# Generate anonymous ring proof
ring_proof = secret_key.prove_ring(vrf_input, ring, aux_data=b"context")
proof_bytes = ring_proof.to_bytes()

# Generate ring commitment (for efficient verification)
commitment_bytes = vrf.PublicKey.get_ring_commitment_bytes([pk.to_bytes() for pk in ring])
print(f"Ring commitment: {commitment_bytes.hex()}")
```

### Working with Public Keys

```python
# Create public key from bytes
pk_bytes = public_key.to_bytes()
restored_pk = vrf.PublicKey(pk_bytes)

# Create from hex string
pk_hex = "deadbeef..."  # 32-byte hex string
pk_from_hex = vrf.PublicKey.from_hex(pk_hex)
```

## API Reference

### Classes

- **`SecretKey`**: VRF secret key with proving capabilities
  - `SecretKey(seed: bytes)`: Create from 32-byte seed
  - `public() -> PublicKey`: Get corresponding public key
  - `prove_ietf(input, aux=None) -> IETFProof`: Generate IETF proof
  - `prove_pedersen(input, aux=None) -> PedersenProof`: Generate Pedersen proof
  - `prove_ring(input, ring, aux=None, index=None) -> RingProof`: Generate ring proof

- **`PublicKey`**: VRF public key with verification capabilities
  - `PublicKey(bytes)`: Create from serialized bytes
  - `from_hex(hex_str) -> PublicKey`: Create from hex string
  - `to_bytes() -> bytes`: Serialize to bytes
  - `get_ring_commitment_bytes(public_keys_bytes) -> bytes`: Generate ring commitment

- **`VRFInput`**: VRF input derived from arbitrary data
  - `VRFInput(data: bytes)`: Create from arbitrary bytes

- **`VRFOutput`**: VRF output with hash capability
  - `hash() -> bytes`: Get 64-byte SHA-512 hash

- **Proof Types**: `IETFProof`, `PedersenProof`, `RingProof`
  - All have `output: VRFOutput` attribute
  - `to_bytes() -> bytes`: Serialize proof

## Advanced Configuration

### Custom SRS File Location

While the SRS file is bundled automatically, you can override its location:

```bash
export ARK_VRF_SRS_PATH=/path/to/your/bandersnatch_ring.srs
```

## Requirements

- Python 3.8 or higher
- Works on macOS, Linux, and Windows

## Performance

- IETF and Pedersen VRF operations: ~1-10ms
- Ring VRF operations: ~100ms-1s (depending on ring size)
- Automatic SRS file loading is cached for subsequent operations

## Security

This library implements cryptographically secure VRF schemes:
- Built on the Bandersnatch curve (Edwards form of BLS12-381 scalar field)
- Deterministic nonce generation following RFC 8032
- Resistant to timing attacks through constant-time operations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Issues and pull requests are welcome! Please visit the [GitHub repository](https://github.com/chainscore/py-ark-vrf).
