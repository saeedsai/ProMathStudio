# Cryptography & Security Toolbox — Feature Catalog

**Status: PLANNED ONLY; no cryptographic implementation is claimed.** This is a separate selectable toolbox in ProMathStudio's Engineering Toolbox workspace. Feature names and short descriptions only, with emphasis on modern defensive cryptography, cryptographic mathematics, encryption/decryption, digital signatures, keys, certificates, secure communications and interoperability with Python libraries. Shared numerical, encoding, file I/O, visualization, validation and export components must be reused. Use vetted libraries and platform cryptographic APIs rather than implementing production cryptographic primitives from scratch; clearly label educational demonstrations and obsolete algorithms.

## Foundations and number theory

| Feature | Description |
|---|---|
| Modular arithmetic | Modular addition, multiplication, exponentiation and inverse |
| Greatest common divisor | Euclidean and extended Euclidean algorithms |
| Prime generation | Generate candidate and probable prime numbers |
| Primality testing | Probabilistic and deterministic tests within supported bounds |
| Integer factorization demonstrations | Educational factorization of small integers |
| Chinese remainder theorem | Solve simultaneous modular congruences |
| Finite fields | Arithmetic in prime and binary extension fields |
| Polynomial arithmetic | Finite-field polynomial operations |
| Elliptic curve arithmetic | Point operations and curve parameter validation |
| Entropy measurement | Estimate randomness and key-space strength |
| Encoding conversions | Hex, base64, binary, UTF-8 and byte conversions |
| Constant-time primitives | Timing-safe comparisons and vetted primitive use |

## Randomness and key management

| Feature | Description |
|---|---|
| Cryptographically secure random bytes | CSPRNG-backed key and nonce material |
| Randomness diagnostics | Statistical tests with clear non-security guarantees |
| Symmetric key generation | Generate valid AES and ChaCha20 keys |
| Asymmetric key-pair generation | Generate supported RSA and elliptic-curve keys |
| Key derivation | HKDF and approved extraction/expansion schemes |
| Password-based key derivation | Argon2id, scrypt and PBKDF2 |
| Key serialization | PEM, DER, JWK and supported key formats |
| Public/private key import | Validate and import compatible key material |
| Key fingerprints | Stable key identifier and fingerprint display |
| Key rotation planning | Key versions, lifecycle and expiration metadata |
| Key wrapping | Authenticated encryption of key material |
| Envelope encryption | Data keys protected by key-encryption keys |
| Key separation | Derive independent keys for different purposes |
| Secret redaction | Hide private material in UI, logs and exports |
| Secure key storage adapters | Optional OS keystore or HSM integrations |
| Key backup and recovery | Encrypted export and restore with safeguards |

## Hashing, MAC and password security

| Feature | Description |
|---|---|
| SHA-2 hashes | SHA-224/256/384/512 and variants |
| SHA-3 and SHAKE | Sponge hashes and extendable-output functions |
| BLAKE2 and BLAKE3 | Fast cryptographic hashing |
| HMAC | Keyed message authentication |
| KMAC | SHA-3-based keyed authentication |
| CMAC | Block-cipher message authentication |
| Poly1305 | One-time authenticator with correct nonce/key handling |
| File integrity hashes | Stream hashing for large files |
| Hash tree and Merkle proofs | Build and verify Merkle trees |
| Password hashing | Argon2id and scrypt credential hashing |
| Password verification | Constant-time password hash verification |
| Password strength estimator | Length and guessability feedback |
| Salt and pepper handling | Unique salts and optional secret pepper metadata |
| Checksum versus cryptographic hash | Clearly distinguish non-security CRC from cryptographic digest |

## Symmetric encryption and authenticated modes

| Feature | Description |
|---|---|
| AES-GCM | Authenticated AES encryption and decryption |
| AES-GCM-SIV | Nonce-misuse-resistant authenticated encryption |
| AES-CCM | Authenticated AES for constrained protocols |
| ChaCha20-Poly1305 | Authenticated stream cipher mode |
| XChaCha20-Poly1305 | Extended-nonce authenticated encryption |
| AES-SIV | Deterministic misuse-resistant authenticated encryption |
| AES-CTR | Counter mode with nonce-reuse warnings |
| AES-CBC | Legacy block mode with explicit authentication requirements |
| Padding validation | PKCS#7 padding and error handling |
| Authenticated encryption with associated data | Bind headers and context to ciphertext |
| Nonce and IV generation | Algorithm-specific unique or random values |
| Encryption file format | Versioned authenticated ciphertext container |
| Streaming file encryption | Chunked authenticated encryption with finalization |
| Ciphertext tamper detection | Reject modified authentication tags |
| Algorithm compatibility matrix | Key, nonce, tag and data-size constraints |

## Public-key cryptography and signatures

| Feature | Description |
|---|---|
| RSA-OAEP | Public-key encryption with OAEP |
| RSA-PSS | Probabilistic RSA digital signatures |
| ECDSA | Elliptic-curve digital signatures |
| Ed25519 and Ed448 | Edwards-curve signatures |
| ECDH | Elliptic-curve Diffie–Hellman exchange |
| X25519 and X448 | Modern elliptic-curve key agreement |
| Hybrid public-key encryption | HPKE and KEM/DEM workflows |
| Signature verification | Verify message and file signatures |
| Detached and attached signatures | Signature packaging variants |
| Multi-signature verification | Verify multiple authorized signers |
| Certificate public-key extraction | Use X.509 public keys |
| Key exchange transcript binding | Bind shared secrets to session context |
| Asymmetric algorithm selection | Choose supported keys and security levels |
| Deterministic test vectors | Known-answer tests for asymmetric primitives |

## Post-quantum cryptography

| Feature | Description |
|---|---|
| ML-KEM | NIST-standardized lattice-based key encapsulation |
| ML-DSA | NIST-standardized lattice-based signatures |
| SLH-DSA | NIST-standardized hash-based signatures |
| Hybrid classical/post-quantum key exchange | Combine independent classical and PQ secrets |
| Hybrid signature workflows | Multiple signature verification policies |
| Post-quantum key and signature serialization | Encode and validate PQ key material |
| Post-quantum algorithm benchmarks | Measure key, signature and ciphertext sizes |
| Post-quantum migration assessment | Identify classical algorithms requiring transition |

## Certificates, PKI and trust

| Feature | Description |
|---|---|
| X.509 certificate parsing | Inspect identities, extensions and validity |
| Certificate signing requests | Create and inspect CSRs |
| Certificate chain validation | Verify issuer signatures and trust chains |
| Hostname verification | Validate DNS identity and SAN entries |
| Certificate expiration monitoring | Inspect validity periods |
| Revocation checks | CRL and OCSP validation |
| Certificate transparency inspection | Inspect SCT and log proofs |
| CA certificate issuance | Generate constrained local test certificates |
| PKCS#12 import/export | Handle certificate and key bundles |
| Trust store inspection | Inspect configured certificate authorities |
| Public-key pinning analysis | Evaluate pin sets and rotation |
| Certificate policy validation | Key usage, EKU and path constraints |

## Protocols and secure communication

| Feature | Description |
|---|---|
| TLS 1.3 inspection | Cipher suites, handshakes and key schedules |
| TLS certificate diagnostics | Inspect server identity and chain |
| HTTPS client configuration | Secure transport options and certificate validation |
| mTLS workflows | Client/server certificate authentication |
| Noise protocol framework | Secure channel handshake patterns |
| SSH key tools | Generate, parse and fingerprint SSH keys |
| OpenPGP interoperability | Encryption and signing file workflows |
| JWT signing and verification | JWS algorithm and key validation |
| JWE encrypted tokens | Authenticated encrypted token workflows |
| COSE and CBOR signing | Compact signed/encrypted messages |
| JOSE and JWK handling | Web crypto keys and token formats |
| Secure messaging concepts | Forward secrecy and session key ratchets |
| Replay protection | Counters, nonces and timestamp validation |
| Protocol transcript analysis | Educational inspection of key derivation |

## Secret sharing and advanced cryptography

| Feature | Description |
|---|---|
| Shamir secret sharing | Split and reconstruct secrets with thresholds |
| Threshold signature concepts | Multi-party signing workflows |
| Commitment schemes | Create and verify cryptographic commitments |
| Zero-knowledge proof primitives | Proof and verification for supported relations |
| Merkle inclusion proofs | Prove set membership via hash trees |
| Authenticated data structures | Integrity proofs for structured data |
| Blind signatures | Privacy-preserving signing workflows |
| Verifiable random functions | Proof-backed pseudorandom outputs |
| Private set intersection concepts | Privacy-preserving set comparisons |
| Homomorphic encryption introduction | Supported encrypted arithmetic demos |
| Multi-party computation concepts | Collaborative private computation models |
| Key transparency proofs | Auditable key-directory commitments |

## File, data and application security

| Feature | Description |
|---|---|
| Text encryption workbench | Encrypt/decrypt short user messages |
| File encryption workbench | Authenticated local file encryption |
| Directory encryption manifests | Encrypted file collections and metadata |
| Digital document signing | Sign and verify document bytes |
| Software artifact verification | Verify package signatures and checksums |
| Password vault format support | Encrypted secrets storage interoperability |
| Database field encryption | Per-field authenticated encryption patterns |
| Secure backup archive | Versioned encrypted backup packages |
| Sensitive metadata handling | Avoid exposing names and context |
| Encrypted data export | Portable authenticated result files |
| Secure deletion limitations | Explain limitations of file overwrite and browser storage |
| Key lifecycle audit | Metadata-only record of cryptographic operations |

## Analysis, validation and interoperability

| Feature | Description |
|---|---|
| Known-answer test suites | NIST and RFC reference vector verification |
| Interoperability test vectors | Compare with Python cryptography and other libraries |
| Cryptographic algorithm benchmarking | Measure time, memory and output size |
| Security level comparison | Equivalent bit-strength estimates |
| Key and nonce misuse warnings | Detect unsafe sizes and repeated nonces where observable |
| Legacy algorithm identification | Mark MD5, SHA-1 signatures, DES and RC4 as insecure |
| Safe defaults and parameter validation | Reject invalid keys, modes and algorithms |
| Authenticated error reporting | Avoid leaking sensitive validation details |
| Threat model templates | Document assets, attackers and trust boundaries |
| Cryptographic protocol visualization | Show key exchange and trust relationships |
| Test fixture and vector import | Load known input/output examples |
| Audit and reproducibility reports | Document algorithm versions and assumptions |
| Python library interoperability | Exchange supported objects with cryptography/PyCryptodome |
| WebCrypto interoperability | Browser-native supported primitive integration |
| FIPS and standards metadata | Show algorithm approval context without claiming certification |
| Cryptographic API documentation | Safe usage examples and limitations |

**Catalog total:** 145 named feature entries across 11 categories. This is a planning count, not a unique-feature or completion count; some entries overlap existing mathematics, signal engineering, coding and electronics capabilities. Security-sensitive implementations require algorithm-specific reference vectors, negative tests, safe key/nonce handling, no plaintext or secret logging, and clear distinctions between demonstration and production-ready functionality.
