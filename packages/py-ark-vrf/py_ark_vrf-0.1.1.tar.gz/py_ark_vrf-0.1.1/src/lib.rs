//! Minimal Python bindings for ark-vrf (Bandersnatch suite).

use pyo3::prelude::*;
use std::fs::File;
use std::io::Read;
use std::io::Cursor;
use hex;
use ark_serialize::{CanonicalSerialize, CanonicalDeserialize};

/* ------------------------------------------------------------------ */
/*   Ark-VRF concrete suite aliases                                    */
/* ------------------------------------------------------------------ */
use ark_vrf::suites::bandersnatch as suite;
type Suite      = suite::BandersnatchSha512Ell2;
type SecretRust = suite::Secret;
type PublicRust = suite::Public;
type InputRust  = suite::Input;
type OutputRust = suite::Output;

/* ---- IETF objects & traits --------------------------------------- */
use ark_vrf::ietf::{self, Prover as IetfProver, Verifier as IetfVerifier};
type IetfProofRust = ietf::Proof<Suite>;

/* ---- Optional Pedersen / Ring ------------------------------------ */
use ark_vrf::pedersen::{self as ped, Prover as PedProver, Verifier as PedVerifier};
type PedersenProofRust = ped::Proof<Suite>;

use ark_vrf::ring::{self};
type RingProofRust = ring::Proof<Suite>;

/* ================================================================== */
/*   Secret key                                                       */
/* ================================================================== */

#[pyclass]
#[derive(Clone)]
struct SecretKey {
    inner: SecretRust,
}

#[pymethods]
impl SecretKey {
    #[new]
    #[pyo3(signature = (seed))]
    fn new(seed: &[u8]) -> Self {
        let inner = SecretRust::from_seed(seed);
        Self { inner }
    }

    fn public(&self) -> PyResult<PublicKey> {
        Ok(PublicKey { inner: self.inner.public() })
    }

    /* IETF */
    #[pyo3(signature = (input, aux = None))]
    fn prove_ietf(&self, input: &VRFInput, aux: Option<&[u8]>) -> PyResult<IETFProof> {
        let output_pt = self.inner.output(input.inner.clone());

        // disambiguate -> IetfProver::prove
        let proof = IetfProver::prove(
            &self.inner,
            input.inner.clone(),
            output_pt.clone(),
            aux.unwrap_or(&[]),
        );

        Ok(IETFProof { inner: proof, output: VRFOutput { inner: output_pt } })
    }

    /* Pedersen */
    #[pyo3(signature = (input, aux = None))]
    fn prove_pedersen(&self, input: &VRFInput, aux: Option<&[u8]>) -> PyResult<PedersenProof> {
        let output_pt = self.inner.output(input.inner.clone());

        // disambiguate -> PedProver::prove
        let (proof, _) = PedProver::prove(
            &self.inner,
            input.inner.clone(),
            output_pt.clone(),
            aux.unwrap_or(&[]),
        );

        Ok(PedersenProof { inner: proof, output: VRFOutput { inner: output_pt } })
    }

    #[pyo3(signature = (input, ring, aux = None, index = None))]
    fn prove_ring(&self, input: &VRFInput, ring: Vec<PublicKey>, aux: Option<&[u8]>, index: Option<usize>) -> PyResult<RingProof> {
        let ring_inner: Vec<_> = ring.iter().map(|pk| pk.inner.0.clone()).collect();
        let idx = index.unwrap_or_else(|| {
            ring_inner.iter().position(|pk| *pk == self.inner.public().0).expect("SecretKey's public key not in ring")
        });
        let params = load_ring_params(ring_inner.len());
        let prover_key = params.prover_key(&ring_inner);
        let prover = params.prover(prover_key, idx);
        let output_pt = self.inner.output(input.inner.clone());
        let proof = <SecretRust as ring::Prover<Suite>>::prove(&self.inner, input.inner.clone(), output_pt.clone(), aux.unwrap_or(&[]), &prover);
        Ok(RingProof { inner: proof, output: VRFOutput { inner: output_pt } })
    }
}

/* ================================================================== */
/*   Public key                                                       */
/* ================================================================== */

#[pyclass]
#[derive(Clone)]
struct PublicKey {
    inner: PublicRust,
}

#[pymethods]
impl PublicKey {
    #[new]
    fn new(public_key_bytes: &[u8]) -> PyResult<Self> {
        let inner = PublicRust::deserialize_compressed(&mut Cursor::new(public_key_bytes))
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        Ok(Self { inner })
    }

    #[staticmethod]
    fn from_hex(hex_str: &str) -> PyResult<Self> {
        let bytes = hex::decode(hex_str)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid hex: {}", e)))?;
        Self::new(&bytes)
    }

    fn to_bytes(&self) -> Vec<u8> {
        let mut buf = Vec::new();
        self.inner.serialize_compressed(&mut buf).unwrap();
        buf
    }

    #[staticmethod]
    fn get_ring_commitment_bytes(public_keys_bytes: Vec<Vec<u8>>) -> PyResult<Vec<u8>> {
        // Convert bytes to PublicKey objects
        let public_keys: Vec<PublicKey> = public_keys_bytes
            .into_iter()
            .map(|bytes| PublicKey::new(&bytes))
            .collect::<PyResult<Vec<_>>>()?;

        // Get the first public key to use for commitment generation
        let first_pk = public_keys.first()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("No public keys provided"))?;

        // Generate ring commitment
        let ring_inner: Vec<_> = public_keys.iter().map(|pk| pk.inner.0.clone()).collect();
        let params = load_ring_params(ring_inner.len());
        let verifier_key = params.verifier_key(&ring_inner);
        let commitment = RingCommitment { inner: verifier_key.commitment() };
        
        // Convert commitment to bytes
        Ok(commitment.to_bytes())
    }

    fn verify_ring_with_commitment(&self, input: &VRFInput, output: &VRFOutput, proof: &RingProof, commitment: &RingCommitment, aux: Option<&[u8]>) -> bool {
        let params = load_ring_params(1); // Size doesn't matter for commitment verification
        let verifier_key = params.verifier_key_from_commitment(commitment.inner.clone());
        let verifier = params.verifier(verifier_key);
        <PublicRust as ring::Verifier<Suite>>::verify(
            input.inner.clone(),
            output.inner.clone(),
            aux.unwrap_or(&[]),
            &proof.inner,
            &verifier,
        ).is_ok()
    }

    fn verify_ring_with_commitment_bytes(
        &self,
        input_bytes: &[u8],
        output_bytes: &[u8],
        proof_bytes: &[u8],
        commitment_bytes: &[u8],
        aux: Option<&[u8]>
    ) -> PyResult<bool> {
        // Convert input bytes to VRFInput
        let input = VRFInput::new(input_bytes)?;
        
        // Convert output bytes to VRFOutput
        let output = VRFOutput { 
            inner: OutputRust::deserialize_compressed(&mut Cursor::new(output_bytes))
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?
        };
        
        // Convert proof bytes to RingProof
        let proof = RingProof::from_bytes(proof_bytes, output.clone())?;
        
        // Convert commitment bytes to RingCommitment
        let commitment = RingCommitment::from_bytes(commitment_bytes)?;
        
        // Verify the proof
        Ok(self.verify_ring_with_commitment(&input, &output, &proof, &commitment, aux))
    }

    #[pyo3(signature = (input, output, proof, ring, aux = None))]
    fn verify_ring(&self, input: &VRFInput, output: &VRFOutput, proof: &RingProof, ring: Vec<PublicKey>, aux: Option<&[u8]>) -> bool {
        let ring_inner: Vec<_> = ring.iter().map(|pk| pk.inner.0.clone()).collect();
        let params = load_ring_params(ring_inner.len());
        let verifier_key = params.verifier_key(&ring_inner);
        let verifier = params.verifier(verifier_key);
        <PublicRust as ring::Verifier<Suite>>::verify(
            input.inner.clone(),
            output.inner.clone(),
            aux.unwrap_or(&[]),
            &proof.inner,
            &verifier,
        ).is_ok()
    }
}

/* ================================================================== */
/*   Input / Output                                                   */
/* ================================================================== */

#[pyclass]
#[derive(Clone)]
struct VRFInput {
    inner: InputRust,
}

#[pymethods]
impl VRFInput {
    #[new]
    fn new(data: &[u8]) -> PyResult<Self> {
        InputRust::new(data)
            .map(|inner| Self { inner })
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("invalid input"))
    }
}

#[pyclass]
#[derive(Clone)]
struct VRFOutput {
    inner: OutputRust,
}

#[pymethods]
impl VRFOutput {
    fn hash(&self) -> Vec<u8> {
        self.inner.hash().to_vec()
    }
}

/* ================================================================== */
/*   Proof wrappers                                                   */
/* ================================================================== */

#[pyclass]
struct IETFProof {
    inner: IetfProofRust,
    #[pyo3(get)]
    output: VRFOutput,
}

#[pyclass]
struct PedersenProof {
    inner: PedersenProofRust,
    #[pyo3(get)]
    output: VRFOutput,
}

#[pyclass]
#[derive(Clone)]
struct RingProof {
    inner: RingProofRust,
    #[pyo3(get)]
    output: VRFOutput,
}

#[pyclass]
struct RingCommitment {
    inner: ring::RingCommitment<Suite>,
}

/* ================================================================== */
/*   Module init                                                      */
/* ================================================================== */

use pyo3::Bound; // helper alias introduced in pyo3 0.25
use pyo3::types::PyModule;

fn load_ring_params(ring_size: usize) -> ring::RingProofParams<Suite> {
    // Always load SRS from a fixed file for deterministic tests
    let srs_path = "bandersnatch_ring.srs";
    let mut file = File::open(srs_path).expect("SRS file not found");
    let mut buf = Vec::new();
    file.read_to_end(&mut buf).expect("Failed to read SRS file");
    let pcs_params = ring::PcsParams::<Suite>::deserialize_uncompressed_unchecked(&mut &buf[..])
        .expect("Failed to deserialize SRS");
    ring::RingProofParams::from_pcs_params(ring_size, pcs_params).expect("Invalid SRS params")
}

#[pymodule]
fn py_ark_vrf(_py: Python<'_>, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<SecretKey>()?;
    m.add_class::<PublicKey>()?;
    m.add_class::<VRFInput>()?;
    m.add_class::<VRFOutput>()?;
    m.add_class::<IETFProof>()?;
    m.add_class::<PedersenProof>()?;
    m.add_class::<RingProof>()?;
    m.add_class::<RingCommitment>()?;
    Ok(())
}

#[pymethods]
impl RingProof {
    fn to_bytes(&self) -> Vec<u8> {
        let mut buf = Vec::new();
        self.inner.serialize_compressed(&mut buf).unwrap();
        buf
    }

    #[staticmethod]
    fn from_bytes(data: &[u8], output: VRFOutput) -> PyResult<Self> {
        let inner = RingProofRust::deserialize_compressed(data)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Deserialization error: {e}")))?;
        Ok(RingProof { inner, output })
    }
}

#[pymethods]
impl RingCommitment {
    fn to_bytes(&self) -> Vec<u8> {
        let mut buf = Vec::new();
        self.inner.serialize_compressed(&mut buf).unwrap();
        buf
    }

    #[staticmethod]
    fn from_bytes(data: &[u8]) -> PyResult<Self> {
        let inner = ring::RingCommitment::<Suite>::deserialize_compressed(data)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Deserialization error: {e}")))?;
        Ok(RingCommitment { inner })
    }
}

#[pymethods]
impl IETFProof {
    fn to_bytes(&self) -> Vec<u8> {
        let mut buf = Vec::new();
        self.inner.serialize_compressed(&mut buf).unwrap();
        buf
    }
}
