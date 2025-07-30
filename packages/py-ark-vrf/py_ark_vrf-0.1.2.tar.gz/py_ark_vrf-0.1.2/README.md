# py-ark-vrf

Python bindings for ARK VRF (Verifiable Random Function) implementation.

## Installation

You can install the package using pip:

```bash
pip install py-ark-vrf
```

## Usage

Here's a basic example of how to use the VRF functionality:

```python
import py_ark_vrf as vrf

# Create a secret key
sk = vrf.SecretKey(b"your-secret-key")
pk = sk.public()

# Create a VRF input
input_data = b"test input"
vrf_input = vrf.VRFInput(input_data)

# Generate IETF proof
ietf_proof = sk.prove_ietf(vrf_input)
is_valid = pk.verify_ietf(vrf_input, ietf_proof.output, ietf_proof)

# Generate Pedersen proof
pedersen_proof = sk.prove_pedersen(vrf_input)
is_valid = pk.verify_pedersen(vrf_input, pedersen_proof.output, pedersen_proof)
```

## Features

- IETF VRF proof generation and verification
- Pedersen VRF proof generation and verification
- Ring VRF support
- Type hints support

## Requirements

- Python 3.7 or higher

## License

This project is licensed under the MIT License - see the LICENSE file for details.
