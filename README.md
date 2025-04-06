# SigmaFold

**SigmaFold** is a PyTorch-based reproduction of **AlphaFold 1 & 3**, focusing on multimodal biomolecular structure prediction. It aims to unify protein folding, RNA structure modeling, and ligand docking into a single, differentiable, end-to-end learnable system. This repository reflects **Dan's understanding of AlphaFold 1 & 3**.


## Project Intro

- Reproduce core architectural ideas behind AlphaFold 1 and AlphaFold 3
- Support proteins, nucleic acids, and small molecules
- Enable ligand docking through joint attention and coordinate prediction
- Provide a training-ready and extensible framework for future development


## Features

- Protein & RNA embedding support
- Evoformer++ for multimodal attention
- Structure module with SE(3)-equivariant reasoning
- Ligand-protein binding modeling
- Dataset loaders for PDB, Rfam, ZINC, and more (WIP)

## Setup Instructions

*Note: Detailed instructions for datasets and pretrained weights will be added soon.*


## Evaluation Benchmarks (Planned)

- CASP14 Free Modeling Targets
- RNA-Puzzles dataset
- DockQ score for protein-ligand complexes
- AlphaFoldDB cross-validation


## References

- Jumper et al. (2021). [AlphaFold](https://www.nature.com/articles/s41586-021-03819-2)
- DeepMind (2024). [AlphaFold 3](https://www.deepmind.com/research/highlighted-research/alphafold)
- Fuchs et al. (2020). [SE(3)-Transformer](https://arxiv.org/abs/2006.10503)
- EquiDock, Uni-Mol, Atom3D

---

## 📬 Contact
Made with curiosity by **Dan Peng**  
