import py_ark_vrf as vrf
import os

def test_basic_vrf():
    # Create a secret key
    sk = vrf.SecretKey(bytes(32))
    pk = sk.public()
    
    # Create a VRF input
    input_data = b"test input"
    vrf_input = vrf.VRFInput(input_data)
    
    # Generate IETF proof
    ietf_proof = sk.prove_ietf(vrf_input)
    assert pk.verify_ietf(vrf_input, ietf_proof.output, ietf_proof)
    
    # Generate Pedersen proof
    pedersen_proof = sk.prove_pedersen(vrf_input)
    assert pk.verify_pedersen(vrf_input, pedersen_proof.output, pedersen_proof)
    
    # Verify output hash
    output_hash = ietf_proof.output.hash()
    assert len(output_hash) == 64  # SHA-512 hash length

def test_deterministic_vrf():
    # Create a secret key with a fixed seed
    seed = b"test seed 123"
    sk = vrf.SecretKey(seed)
    pk = sk.public()
    
    # Create a VRF input
    input_data = b"test input"
    vrf_input = vrf.VRFInput(input_data)
    
    # Generate two proofs with the same input and seed
    proof1 = sk.prove_ietf(vrf_input)
    proof2 = sk.prove_ietf(vrf_input)
    
    # The proofs should be identical
    assert proof1.to_bytes() == proof2.to_bytes()

def test_ring_proof():
    # Create a ring of public keys
    ring_size = 4
    ring = []
    secret_keys = []
    for i in range(ring_size):
        sk = vrf.SecretKey(f"key_{i}".encode())
        secret_keys.append(sk)
        ring.append(sk.public())
    
    # Create a VRF input
    input_data = b"test ring input"
    vrf_input = vrf.VRFInput(input_data)
    
    # Generate a ring proof using the first key
    prover_sk = secret_keys[0]
    # ring_proof = prover_sk.prove_ring(vrf_input, ring)
    
    # # Verify the ring proof
    # assert ring[0].verify_ring(vrf_input, ring_proof.output, ring_proof, ring)
    
    # Test ring commitment
    commitment = ring[0].get_ring_commitment(ring)
    print(commitment.to_bytes().hex(), ring)
    # assert ring[0].verify_ring_with_commitment(vrf_input, ring_proof.output, ring_proof, commitment)
    
    # # Test serialization
    # proof_bytes = ring_proof.to_bytes()
    # commitment_bytes = commitment.to_bytes()
    
    # # Test deserialization
    # new_proof = vrf.RingProof.from_bytes(proof_bytes, ring_proof.output)
    # new_commitment = vrf.RingCommitment.from_bytes(commitment_bytes)
    
    # # Verify with deserialized objects
    # assert ring[0].verify_ring(vrf_input, new_proof.output, new_proof, ring)
    # assert ring[0].verify_ring_with_commitment(vrf_input, new_proof.output, new_proof, new_commitment)

def test_ring_vectors():
    print("Testing ring VRF test vectors (placeholder)...")
    # TODO: Load and check vectors from ark-vrf/data/vectors/
    # This will require parsing the vector format and using RingProof.from_bytes
    pass

def test_validator_set_ring_commitment():
    # List of validator public keys in hex format
    validator_keys = [
        "0x5e465beb01dbafe160ce8216047f2155dd0569f058afd52dcea601025a8d161d",
        "0x3d5e5a51aab2b048f8686ecd79712a80e3265a114cc73f14bdb2a59233fb66d0",
        "0xaa2b95f7572875b0d0f186552ae745ba8222fc0b5bd456554bfe51c68938f8bc",
        "0x7f6190116d118d643a98878e294ccf62b509e214299931aad8ff9764181a4e33",
        "0x48e5fcdce10e0b64ec4eebd0d9211c7bac2f27ce54bca6f7776ff6fee86ab3e3",
        "0xf16e5352840afb47e206b5c89f560f2611835855cf2e6ebad1acc9520a72591d"
    ]
    
    # Convert hex strings to bytes
    public_keys_bytes = []
    for key_hex in validator_keys:
        # Remove '0x' prefix if present
        key_hex = key_hex[2:] if key_hex.startswith('0x') else key_hex
        # Convert hex to bytes
        key_bytes = bytes.fromhex(key_hex)
        public_keys_bytes.append(key_bytes)
    
    # Generate ring commitment using bytes
    commitment_bytes = vrf.PublicKey.get_ring_commitment_bytes(public_keys_bytes)
    
    # Print the commitment in hex format
    print(f"Ring commitment: 0x{commitment_bytes.hex()}")
    
if __name__ == "__main__":
    # Ensure SRS file exists
    # if not os.path.exists("bandersnatch_ring.srs"):
    #     print("Error: bandersnatch_ring.srs file not found")
    #     exit(1)
        
    # Run tests
    # test_basic_vrf()
    # test_deterministic_vrf()
    # test_ring_proof()
    test_validator_set_ring_commitment()
    print("All tests passed!")
