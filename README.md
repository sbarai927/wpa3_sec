# README


## Table of Contents
- [Objective](#objective)
- [Prerequisites](#prerequisites)
- [Installation](#installation)  
- [Repository Layout](#repository-layout)  
- [Quick Start](#quick-start)  
- [Notebooks](#notebooks)  
- [Reproducing Key Results](#reproducing-key-results)  
- [Unit Tests](#unit-tests)  
- [Project Road-map](#project-road-map)  
- [Citation](#citation)  
- [Contact](#contact)

---

##  Objective  

This repository accompanies our **B.Sc. Thesis**  **“Reduced Side-Channel Timing Attack in the Dragonfly Handshake of WPA-3 (MODP Group)”**  submitted to the **Department of Electronics and Telecommunication Engineering**, **Daffodil International University**, January 2020.  *Supervised by **Prof. Dr. A.K.M. Fazlul Haque***.

We aim to:

* **RQ 1 – Quantify the leak:**  
  Measure how execution-time variance in Dragonfly’s MODP password-element
  generation reveals information about the network pass-phrase.

* **RQ 2 – Evaluate mitigations:**  
  Determine how fixed-iteration ranges (`K_min`, `K_max`) and random
  password-element selection reduce (or fail to reduce) an attacker’s
  advantage.

* **RQ 3 – Practical exploitation:**  
  Provide black-box test-benches and notebooks that recreate timing and
  cache-based side-channel attacks on commodity hardware.

* **RQ 4 – Performance trade-offs:**  
  Analyse CPU-time overhead of the mitigation compared with the original
  algorithm on resource-constrained devices (e.g. Wi-Fi AP SoCs).

---

***This GitHub codebase is a reproducible, open-source re-implementation of
the thesis experiments, released so the community can verify, extend, and
challenge our findings.***

##  Prerequisites  

| Item | Tested Version(s) | Notes |
|------|-------------------|-------|
| Python | 3.8 – 3.11 | Scripts use `f-strings` and `typing`, so ≥3.8 is safest. |
| pip / venv | latest | Recommended: `python -m venv .venv && source .venv/bin/activate`. |
| GNU make (optional) | ≥4.3 | Only needed if you plan to use the provided `Makefile` helpers. |
| gcc / clang | any modern | Required only for building `pycryptodome` C extensions faster. |
| JupyterLab / Notebook | 3.x | For exploring `timing_analysis.ipynb`. |
| Git LFS (optional) | latest | If you intend to version-control large CSVs or pcap traces. |
| Hardware timer resolution | µs-level | A CPU with invariant TSC is ideal for stable timing tests. |

## Installation
```bash
# clone & enter
git clone https://github.com/<your-acct>/dragonfly-timing.git
cd dragonfly-timing

# create env, install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
Tested on Python ≥ 3.9 (Linux & Windows).

## Repository Layout 

```bash
wpa3_sec/                       ← root of the repo
│
├── data/                       ← **Raw + derived data assets**
│   ├── mac_timing.csv
│   ├── pe_generation_full.csv
│   ├── random_calls.csv
│   ├── variation_execution_time.csv
│   └── pe_generation_full.png  # (auto-generated graph – commit later)
│
├── docs/                       ← (OPTIONAL) slides, paper PDF, extra figures
│
├── notebooks/                  ← Exploratory Jupyter notebooks
│   └── timing_analysis.ipynb
│
├── scripts/                    ← One-off driver scripts / CLIs
│   ├── bruteforce_attack.py
│   ├── mitigation_demo.py
│   └── timing_attack_simulation.py
│
├── src/                        ← Importable Python package (`pip install -e .`)
│   ├── __init__.py
│   ├── dragonfly_modp.py       # reference implementation + timing helpers
│   ├── mac_utils.py            # MAC-address helpers for spoofing tests
│   └── mitigation.py           # constant-time fixes and API
│
├── tests/                      ← PyTest unit / regression tests
│   ├── test_dragonfly.py
│   └── test_mitigation.py
│
├── requirements.txt            ← Pin-down Python runtime deps
└── README.md                   ← You’re here

```

## Quick Start

```bash
# Run unit-tests (should all be green)
pytest -q

# Launch a timing-attack simulation
python scripts/timing_attack_simulation.py --help   # view options
python scripts/timing_attack_simulation.py --quiet  # run with defaults

# See the mitigation in action
python scripts/mitigation_demo.py                   # before/after timings

# Reproduce Figure 4 (PE generation curve) interactively
jupyter lab notebooks/timing_analysis.ipynb

# Offline brute-force demo with own word-list
python scripts/bruteforce_attack.py --dict <path/to/list.txt>

```

## Notebooks

| Notebook | Purpose | How to Launch |
|----------|---------|---------------|
| `timing_analysis.ipynb` | Re-creates **Figure 4** (iteration vs execution-time curve) and walks through the data-generation + Matplotlib code step-by-step. | ```bash<br>jupyter lab notebooks/timing_analysis.ipynb<br>``` |

> **Heads-up:** the notebook expects the four CSVs in `data/` to be present.  
> If you changed any filenames or paths, adjust the first code-cell accordingly.

## Reproducing Key Results 

Below are one-liners that reproduce every figure / table discussed in the thesis.  
All scripts drop their artefacts (plots & CSVs) into `docs/artifacts/` so they stay out of your source tree.

| Result | Command | Output |
|--------|---------|--------|
| **Table 1 – Variation in Execution Time**<br>(Loops vs per-loop & total µs) | ```bash<br>python scripts/timing_attack_simulation.py \ <br> --out docs/artifacts/variation_execution_time.csv<br>``` | CSV identical to *Table 1* in `docs/artifacts/variation_execution_time.csv` |
| **Table 3 – PE Generation (full)** | ```bash<br>python scripts/timing_attack_simulation.py \ <br> --dump-pe --out docs/artifacts/pe_generation_full.csv<br>``` | Full PE table in `docs/artifacts/pe_generation_full.csv` |
| **Figure 4 – Iteration vs Execution-Time Curve** | ```bash<br>python scripts/timing_attack_simulation.py \ <br> --plot --out docs/artifacts/pe_iter_vs_time.png<br>``` | PNG plot identical to Figure 4 |
| **Table 4 – Random Calls** | ```bash<br>python scripts/timing_attack_simulation.py \ <br> --random-calls 5 \ <br> --out docs/artifacts/random_calls.csv<br>``` | `random_calls.csv` with five pseudo-random selections |
| **Brute-Force Success Experiment** *(Section 7)* | ```bash<br>python scripts/bruteforce_attack.py \ <br> --dict data/rockyou_top1m.txt \ <br> --out docs/artifacts/bruteforce_stats.json<br>``` | Stats + histogram (`bruteforce_stats.json`, `bruteforce_hist.png`) |
| **Mitigation Performance Demo** *(Section 4.2)* | ```bash<br>python scripts/mitigation_demo.py \ <br> --iters 50000 \ <br> --out docs/artifacts/mitigation_benchmark.txt<br>``` | Timing/CPU report with & without our fix |

```

> **Note**  
> All scripts read the canonical CSVs in `data/` **unless** an `--out` file from a previous run already exists (idempotent design).  
> Rerunning with `--force` overwrites cached artefacts.
```
## Unit Tests

| File                              | Scope                                   |
|-----------------------------------|-----------------------------------------|
| `tests/test_dragonfly.py`         | PE-generation & timing-attack logic     |
| `tests/test_mitigation.py`        | Constant-time mitigation assertions     |

### Run tests

```bash
pytest          # quick run
pytest -q       # silent
pytest --cov    # with coverage
```
## Project Road-map

| Phase | Time-frame | Milestones | Status |
|-------|-----------|------------|--------|
| **0. Initial Release** | Done | • Publish core `src/` modules<br>• Upload reference CSV datasets<br>• Provide baseline Jupyter notebook (`timing_analysis.ipynb`) | **Completed v1.0** |
| **1. Reproduce Paper Results** | Aug 2025 | • Automate data-prep (`scripts/timing_attack_simulation.py`)<br>• Regenerate key figures from `pe_generation_full.csv`<br>• Publish step-by-step notebook walkthrough | In progress |
| **2. Extend Attack Surface** | Sep 2025 | • Implement cache-side-channel PoC<br>• Add unit tests for new modules (`tests/test_cache_attack.py`) | 
| **3. Mitigation Toolkit** | Oct 2025 | • Release `src/mitigation.py` CLI<br>• Demo notebook: real-time mitigation of timing leaks | 
| **4. Packaging & CI/CD** | Nov 2025 | • Package to PyPI (`pip install wpa3-sec`)<br>• Add GitHub Actions for linting/tests<br>• Generate coverage reports | 
| **5. Community Contributions** | ongoing | • Triage issues & PRs<br>• Publish contributing guide<br>• Hold first milestone release (v2.0) | 

## Citation  

1. Vanhoef, M. & Piessens, F. **Key Reinstallation Attacks: Forcing Nonce Reuse in WPA2**. *Proc. ACM Conf. on Computer and Communications Security (CCS)*, 2017, pp. 1313–1328.  
2. Vanhoef, M. & Piessens, F. **Release The Kraken: New Kracks in the 802.11 Standard**. *Proc. ACM CCS*, 2018, pp. 299–314.  
3. Wi-Fi Alliance. **Wi-Fi Alliance® Introduces Wi-Fi CERTIFIED WPA3™ Security**. <https://www.wi-fi.org/news-events/newsroom/wi-fi-alliance-introduces-wi-fi-certified-wpa3-security> (accessed Oct 24 2019).  
4. Igoe, K. M. **[Cfrg] Status of DragonFly**. CFRG mailing-list post, 2012. <https://mailarchive.ietf.org/arch/msg/cfrg/_BZEwEBBWhOPXn0Zw-cd3eSV6pY/>  
5. Diffie, W. & Hellman, M. **Diffie–Hellman Key Exchange**. In *Encyclopedia of Cryptography and Security*, pp. 342–342, 2011.  
6. Vanhoef, M. & Piessens, F. **Predicting, Decrypting, and Abusing WPA2/802.11 Group Keys**. USENIX Security Workshop Talk, 2016.  
7. Kivinen, T. & Kojo, M. **RFC 3526: More MODP Diffie-Hellman Groups for IKE**. IETF, 2003.  
8. Islam, I., Barai, S. & Moon, A. **Reduced Side-Channel Timing Attack in Dragonfly Handshake of WPA3 for MODP Group**. B.Sc. Thesis, Daffodil Int. Univ., 2020.  
9. Vanhoef, M. & Ronen, E. **Dragonblood: A Security Analysis of WPA3’s SAE Handshake**. 2018. <https://papers.mathyvanhoef.com/dragonblood.pdf>  
10. Jiang, Z. H., Fei, Y., & Kaeli, D. **A Novel Side-Channel Timing Attack on GPUs**. *Proc. ACM GLSVLSI*, 2017, pp. 167–172.  
11. Wi-Fi Alliance. **Wi-Fi Protected Access ® Security Considerations**. May 2021.  
12. Wi-Fi Alliance. **WPA3™ Specification Version 3.0**. 2020.  
13. Kohlios, C. P. & Hayajneh, T. **A Comprehensive Attack-Flow Model and Security Analysis for Wi-Fi and WPA3**. *Electronics*, 7 (11), 2018.  
14. Henry, J. **802.11s Mesh Networking**. 2011.  
15. Van Goethem, T. V. et al. **Timeless Timing Attacks: Exploiting Concurrency to Leak Secrets over Remote Connections**. *Proc. USENIX Security Symp.*, 2020, pp. 1985–2002.  
16. Appel, M. & Guenther, S. D-I. **WPA 3 – Improvements over WPA 2 or Broken Again?** *NET* 2020-11-1, pp. 2–5.  
17. Yarom, Y., Genkin, D. & Heninger, N. **CacheBleed: A Timing Attack on OpenSSL Constant-Time RSA**. *Journal of Cryptographic Engineering*, 7 (2), 2017, pp. 99–112.  
18. Harkins, D. **Secure Pre-Shared Key (PSK) Authentication for the Internet Key Exchange Protocol (IKE)**. *RFC 6617*, 2012.  
19. Harkins, D. **Dragonfly Key Exchange**. *RFC 7664*, 2015.  

## Contact

For any questions or issues, please contact:
- Suvendu Barai; Ikramul Islam
- Email: suvendu19-1845@diu.edu.bd; ikramul19-1847@diu.edu.bd
