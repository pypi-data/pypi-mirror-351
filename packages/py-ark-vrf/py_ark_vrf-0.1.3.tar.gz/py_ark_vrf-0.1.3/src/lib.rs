//! Minimal Python bindings for ark-vrf (Bandersnatch suite).

use pyo3::prelude::*;
use std::fs::File;
use std::io::Read;
use std::io::Cursor;
use hex;
use ark_serialize::{CanonicalSerialize, CanonicalDeserialize};

use once_cell::sync::OnceCell;
use std::path::PathBuf;

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
use ark_vrf::ietf::{self, Prover as IetfProver};
type IetfProofRust = ietf::Proof<Suite>;

/* ---- Optional Pedersen / Ring ------------------------------------ */
use ark_vrf::pedersen::{self as ped, Prover as PedProver};
type PedersenProofRust = ped::Proof<Suite>;

use ark_vrf::ring::{self};
type RingProofRust = ring::Proof<Suite>;

/* ================================================================== */
/*   SRS File Handling                                                */
/* ================================================================== */

static SRS_FILE_PATH: OnceCell<PathBuf> = OnceCell::new();

fn find_srs_file(py: Python<'_>) -> Result<PathBuf, PyErr> {
    // 1. Check environment variable
    if let Ok(path_str) = std::env::var("ARK_VRF_SRS_PATH") {
        let path = PathBuf::from(path_str);
        if path.exists() {
            return Ok(path);
        }
    }

    // 2. Try to find it relative to the module file
    let current_module_path_result = PyModule::import(py, "py_ark_vrf")
        .and_then(|module_bound| module_bound.filename())
        .and_then(|path_obj| path_obj.to_str().map(PathBuf::from).map_err(|_| PyErr::new::<pyo3::exceptions::PyTypeError, _>("Module path is not valid UTF-8")));

    if let Ok(module_file) = current_module_path_result {
        if module_file.is_file() {
            // Check in the same directory as the .so file
            let mut srs_path_candidate_1 = module_file.clone();
            srs_path_candidate_1.pop(); // directory of the .so file
            srs_path_candidate_1.push("bandersnatch_ring.srs");
            if srs_path_candidate_1.exists() {
                return Ok(srs_path_candidate_1);
            }

            // Check in the parent directory of the .so file's directory (e.g., site-packages/ for site-packages/py_ark_vrf/module.so)
            let mut srs_path_candidate_2 = module_file.clone(); // path to .so
            srs_path_candidate_2.pop(); // .so -> dir containing .so (e.g. .../py_ark_vrf/)
            if srs_path_candidate_2.pop() { // dir containing .so -> parent of that dir (e.g. .../site-packages/)
                srs_path_candidate_2.push("bandersnatch_ring.srs");
                if srs_path_candidate_2.exists() {
                    return Ok(srs_path_candidate_2);
                }
            }
        }
    }

    // 3. Fallback to current working directory
    let cwd = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    let cwd_path = cwd.join("bandersnatch_ring.srs");
    if cwd_path.exists() {
        return Ok(cwd_path);
    }
    
    Err(PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
        "bandersnatch_ring.srs not found. Searched ARK_VRF_SRS_PATH, paths relative to the installed py_ark_vrf module, and the current working directory. Please ensure 'bandersnatch_ring.srs' is correctly placed (e.g., next to the py_ark_vrf.*.so file or in the package root), or set the ARK_VRF_SRS_PATH environment variable."
    ))
}

fn init_srs_path(py: Python<'_>) -> PyResult<&PathBuf> {
    SRS_FILE_PATH.get_or_try_init(|| find_srs_file(py))
}

fn load_ring_params(py: Python<'_>, ring_size: usize) -> PyResult<ring::RingProofParams<Suite>> {
    let srs_path = init_srs_path(py)?;
    
    let mut file = File::open(srs_path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(format!(
            "Failed to open SRS file at '{}': {}. Ensure the file exists, is accessible, and ARK_VRF_SRS_PATH is set correctly if used.",
            srs_path.display(), e
        ))
    })?;
    let mut buf = Vec::new();
    file.read_to_end(&mut buf).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
            "Failed to read SRS file contents from '{}': {}",
            srs_path.display(), e
        ))
    })?;
    let pcs_params = ring::PcsParams::<Suite>::deserialize_uncompressed_unchecked(&mut &buf[..])
        .map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Failed to deserialize SRS data from '{}': {}. The file might be corrupted or not a valid SRS file.",
                srs_path.display(), e
            ))
        })?;
    ring::RingProofParams::from_pcs_params(ring_size, pcs_params).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
            "Invalid SRS parameters created from file '{}': {:?}. The SRS file might not be compatible or of the correct size.",
            srs_path.display(), e // Using {:?} for the error as its Display impl might vary
        ))
    })
}

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
        let (proof, _) = PedProver::prove(
            &self.inner,
            input.inner.clone(),
            output_pt.clone(),
            aux.unwrap_or(&[]),
        );
        Ok(PedersenProof { inner: proof, output: VRFOutput { inner: output_pt } })
    }

    #[pyo3(signature = (input, ring, aux = None, index = None))]
    fn prove_ring(&self, py: Python<'_>, input: &VRFInput, ring: Vec<PublicKey>, aux: Option<&[u8]>, index: Option<usize>) -> PyResult<RingProof> {
        let ring_inner: Vec<_> = ring.iter().map(|pk| pk.inner.0.clone()).collect();
        let idx = index.unwrap_or_else(|| {
            ring_inner.iter().position(|pk| *pk == self.inner.public().0).expect("SecretKey's public key not in ring")
        });
        let params = load_ring_params(py, ring_inner.len())?;
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
    #[pyo3(signature = (public_keys_bytes))]
    fn get_ring_commitment_bytes(py: Python<'_>, public_keys_bytes: Vec<Vec<u8>>) -> PyResult<Vec<u8>> {
        let public_keys: Vec<PublicKey> = public_keys_bytes
            .into_iter()
            .map(|bytes| PublicKey::new(&bytes))
            .collect::<PyResult<Vec<_>>>()?;

        if public_keys.is_empty() {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("No public keys provided"));
        }

        let ring_inner: Vec<_> = public_keys.iter().map(|pk| pk.inner.0.clone()).collect();
        let params = load_ring_params(py, ring_inner.len())?;
        let verifier_key = params.verifier_key(&ring_inner);
        let commitment = RingCommitment { inner: verifier_key.commitment() };
        
        Ok(commitment.to_bytes())
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
