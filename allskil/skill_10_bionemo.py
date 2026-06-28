import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WORK_DIR

SKILL_NAME = "NVIDIA BioNeMo"
SKILL_DESC = "NVIDIA BioNeMo framework for biological AI — protein structure prediction, drug discovery, molecular generation, and genomics"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bionemo_protein_folding",
            "description": "Predict protein 3D structure from amino acid sequence using ESMFold or AlphaFold2 via BioNeMo",
            "parameters": {
                "type": "object",
                "properties": {
                    "sequence": {"type": "string", "description": "Amino acid sequence in single-letter code, e.g. 'MKTLLLTLVVVTIVCLDLGYT...'"},
                    "model": {
                        "type": "string",
                        "enum": ["esmfold", "alphafold2", "openfold"],
                        "description": "Structure prediction model to use",
                        "default": "esmfold"
                    },
                    "output_pdb": {"type": "string", "description": "Output PDB file path for predicted structure"}
                },
                "required": ["sequence"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bionemo_molecule_generate",
            "description": "Generate novel drug-like molecules using MolMIM or other generative models",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "enum": ["molmim", "megamolbart", "diffdock"],
                        "description": "Generative model to use"
                    },
                    "seed_smiles": {"type": "string", "description": "Seed molecule in SMILES notation (optional), e.g. 'CC(=O)OC1=CC=CC=C1C(=O)O'"},
                    "num_molecules": {"type": "integer", "description": "Number of molecules to generate", "default": 10},
                    "property_targets": {
                        "type": "object",
                        "description": "Target molecular properties, e.g. {'QED': 0.8, 'LogP': 2.5}"
                    }
                },
                "required": ["model"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bionemo_docking",
            "description": "Predict protein-ligand binding using DiffDock or AutoDock via BioNeMo",
            "parameters": {
                "type": "object",
                "properties": {
                    "protein_pdb": {"type": "string", "description": "Path to protein PDB file"},
                    "ligand_smiles": {"type": "string", "description": "Ligand molecule in SMILES format"},
                    "model": {
                        "type": "string",
                        "enum": ["diffdock", "autodock-vina", "gnina"],
                        "description": "Docking model to use",
                        "default": "diffdock"
                    },
                    "num_poses": {"type": "integer", "description": "Number of binding poses to generate", "default": 10}
                },
                "required": ["protein_pdb", "ligand_smiles"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bionemo_embeddings",
            "description": "Generate biological embeddings from protein/DNA/RNA sequences using BioNeMo models",
            "parameters": {
                "type": "object",
                "properties": {
                    "sequences": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of biological sequences"
                    },
                    "model": {
                        "type": "string",
                        "enum": ["esm2-650m", "esm2-3b", "geneformer", "nucleotide-transformer", "prot-t5"],
                        "description": "Embedding model to use"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["numpy", "pytorch", "csv"],
                        "description": "Output format for embeddings",
                        "default": "numpy"
                    }
                },
                "required": ["sequences", "model"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bionemo_setup",
            "description": "Set up NVIDIA BioNeMo framework and download models",
            "parameters": {
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "enum": ["bionemo-framework", "esmfold-nim", "molmim-nim", "diffdock-nim", "alphafold2-nim"],
                        "description": "BioNeMo component to set up"
                    },
                    "install_method": {
                        "type": "string",
                        "enum": ["pip", "docker", "nim"],
                        "description": "Installation method"
                    }
                },
                "required": ["component", "install_method"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bionemo_finetune",
            "description": "Fine-tune a BioNeMo model on custom biological data",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_model": {"type": "string", "description": "Base model to fine-tune, e.g. 'esm2-650m', 'molmim'"},
                    "dataset_path": {"type": "string", "description": "Path to training dataset (FASTA for proteins, SMILES for molecules)"},
                    "task": {
                        "type": "string",
                        "enum": ["property_prediction", "generation", "classification", "regression"],
                        "description": "Downstream task to fine-tune for"
                    },
                    "epochs": {"type": "integer", "description": "Training epochs", "default": 10},
                    "output_name": {"type": "string", "description": "Fine-tuned model name"}
                },
                "required": ["base_model", "dataset_path", "task", "output_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bionemo_explain",
            "description": "Explain NVIDIA BioNeMo capabilities, models, and use cases",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": ["overview", "protein_folding", "drug_discovery", "embeddings", "nim_models", "genomics"],
                        "description": "Topic to explain"
                    }
                },
                "required": ["topic"]
            }
        }
    }
]


def bionemo_protein_folding(sequence: str, model: str = "esmfold", output_pdb: str = None) -> str:
    pdb_out = output_pdb or os.path.join(WORK_DIR, f"structure_{model}.pdb")
    seq_short = sequence[:40] + "..." if len(sequence) > 40 else sequence
    return (
        f"🧬 **Protein Structure Prediction**\n"
        f"Model: `{model}` | Sequence length: {len(sequence)} aa\n"
        f"Sequence: `{seq_short}`\n"
        f"Output: `{pdb_out}`\n\n"
        f"```python\nimport bionemo\nfrom bionemo.model.protein.esm1nv import ESM1nvInference\n\n"
        f"# Load {model} from BioNeMo\npredictor = ESM1nvInference.from_pretrained('{model}')\n\n"
        f"# Predict structure\nstructure = predictor.predict_structure(\n"
        f"    sequence='{sequence[:30]}...',\n"
        f"    output_pdb='{pdb_out}'\n"
        f")\nprint(f'pLDDT score: {{structure.plddt.mean():.2f}}')\n"
        f"print(f'Structure saved: {pdb_out}')\n```\n\n"
        f"Via NIM API:\n```bash\ncurl -X POST https://health.api.nvidia.com/v1/biology/{model} \\\n"
        f"  -H 'Authorization: Bearer $NVIDIA_API_KEY' \\\n"
        f"  -d '{{\"sequence\": \"{sequence[:30]}...\"}}'  | python3 -m json.tool\n```"
    )


def bionemo_molecule_generate(model: str, seed_smiles: str = None, num_molecules: int = 10, property_targets: dict = None) -> str:
    props = property_targets or {"QED": 0.7, "LogP": 2.0}
    seed_str = f"seed_smiles='{seed_smiles}'" if seed_smiles else "# no seed — de novo generation"
    return (
        f"💊 **Molecule Generation: {model}**\n"
        f"Count: {num_molecules} | Targets: {props}\n"
        f"Seed: `{seed_smiles or 'none (de novo)'}`\n\n"
        f"```python\nfrom bionemo.model.molecule.molmim import MolMIMInference\n\n"
        f"model = MolMIMInference.from_pretrained('{model}')\n\n"
        f"molecules = model.sample(\n"
        f"    {seed_str},\n"
        f"    num_molecules={num_molecules},\n"
        f"    property_targets={props},\n"
        f"    temperature=1.0\n"
        f")\n\n"
        f"for mol in molecules:\n"
        f"    print(f'SMILES: {{mol.smiles}} | QED: {{mol.qed:.3f}} | LogP: {{mol.logp:.3f}}')\n```\n\n"
        f"Or via NVIDIA API Catalog: https://api.nvidia.com/v1/biology/{model}"
    )


def bionemo_docking(protein_pdb: str, ligand_smiles: str, model: str = "diffdock", num_poses: int = 10) -> str:
    return (
        f"🔬 **Protein-Ligand Docking: {model}**\n"
        f"Protein: `{protein_pdb}` | Ligand: `{ligand_smiles[:30]}...`\n"
        f"Poses: {num_poses}\n\n"
        f"```python\nfrom bionemo.model.molecule.diffdock import DiffDockInference\n\n"
        f"docker = DiffDockInference.from_pretrained('diffdock')\n\n"
        f"poses = docker.predict(\n"
        f"    protein_path='{protein_pdb}',\n"
        f"    ligand_smiles='{ligand_smiles}',\n"
        f"    num_poses={num_poses},\n"
        f"    output_dir='./docking_results'\n"
        f")\n\n"
        f"for i, pose in enumerate(poses):\n"
        f"    print(f'Pose {{i+1}}: confidence={{pose.confidence:.3f}}, RMSD={{pose.rmsd:.2f}}Å')\n```\n\n"
        f"Results: SDF files with binding poses + confidence scores"
    )


def bionemo_embeddings(sequences: list, model: str, output_format: str = "numpy") -> str:
    seqs_short = [s[:20] + "..." if len(s) > 20 else s for s in sequences[:3]]
    return (
        f"🧮 **Biological Embeddings: {model}**\n"
        f"Sequences: {len(sequences)} | Format: {output_format}\n"
        f"Sample: {seqs_short}\n\n"
        f"```python\nfrom bionemo.model.protein.esm1nv import ESM2Inference\nimport numpy as np\n\n"
        f"encoder = ESM2Inference.from_pretrained('{model}')\n\n"
        f"sequences = {sequences[:3]}\n"
        f"embeddings = encoder.encode(sequences)  # shape: (N, seq_len, hidden_dim)\n\n"
        f"# Mean pool over sequence length\nrepresentations = embeddings.mean(dim=1)  # (N, hidden_dim)\n"
        f"print(f'Embedding shape: {{representations.shape}}')\n\n"
        f"{'np.save(\"embeddings.npy\", representations.numpy())' if output_format == 'numpy' else 'torch.save(representations, \"embeddings.pt\")'}\n```"
    )


def bionemo_setup(component: str, install_method: str) -> str:
    if install_method == "pip":
        return (
            f"📦 **BioNeMo pip install: {component}**\n```bash\n"
            f"pip install bionemo-framework\n"
            f"# Download model weights\npython -c \"import bionemo; bionemo.download('{component}')\"\n```"
        )
    elif install_method == "docker":
        return (
            f"🐳 **BioNeMo Docker: {component}**\n```bash\n"
            f"docker pull nvcr.io/nvidia/clara/bionemo-framework:latest\n"
            f"docker run --gpus all -it \\\n"
            f"  -e NGC_API_KEY=$NGC_API_KEY \\\n"
            f"  -v $PWD:/workspace \\\n"
            f"  nvcr.io/nvidia/clara/bionemo-framework:latest bash\n```"
        )
    else:
        nim_map = {
            "esmfold-nim": "nim/esmfold",
            "molmim-nim": "nim/molmim",
            "diffdock-nim": "nim/diffdock",
            "alphafold2-nim": "nim/alphafold2"
        }
        nim_img = nim_map.get(component, f"nim/{component}")
        return (
            f"🔌 **BioNeMo NIM: {component}**\n```bash\n"
            f"docker pull nvcr.io/nvidia/{nim_img}:latest\n"
            f"docker run --gpus all -p 8000:8000 \\\n"
            f"  -e NGC_API_KEY=$NGC_API_KEY \\\n"
            f"  nvcr.io/nvidia/{nim_img}:latest\n```\n\n"
            f"API endpoint: `http://localhost:8000/v1/biology/predict`"
        )


def bionemo_finetune(base_model: str, dataset_path: str, task: str, output_name: str, epochs: int = 10) -> str:
    return (
        f"🏋️ **BioNeMo Fine-Tuning: {base_model} → {output_name}**\n"
        f"Task: `{task}` | Data: `{dataset_path}` | Epochs: {epochs}\n\n"
        f"```bash\npython -m bionemo.model.train \\\n"
        f"  --config-name {base_model}_finetune \\\n"
        f"  model.data.dataset_path={dataset_path} \\\n"
        f"  trainer.max_epochs={epochs} \\\n"
        f"  model.downstream_task.task={task} \\\n"
        f"  exp_manager.exp_dir=./results/{output_name}\n```\n\n"
        f"Multi-GPU:\n```bash\npython -m torch.distributed.launch --nproc_per_node=4 \\\n"
        f"  -m bionemo.model.train --config-name {base_model}_finetune\n```\n\n"
        f"Evaluate: `python -m bionemo.model.eval --checkpoint ./results/{output_name}`"
    )


def bionemo_explain(topic: str) -> str:
    explanations = {
        "overview": (
            "🧬 **NVIDIA BioNeMo Overview**\n\n"
            "Large-scale biological AI framework for:\n"
            "• **Protein** — structure prediction (ESMFold, AlphaFold2), embeddings (ESM-2)\n"
            "• **Small molecules** — generation (MolMIM, MegaMolBART), docking (DiffDock)\n"
            "• **Genomics** — DNA/RNA sequence models (Nucleotide Transformer)\n"
            "• **Drug discovery** — end-to-end pipelines for hit identification\n\n"
            "All models available as NIMs (microservices) or full framework.\n"
            "Docs: https://docs.nvidia.com/bionemo-framework/"
        ),
        "protein_folding": "🔬 ESMFold predicts protein 3D structure from sequence in seconds (vs. hours for AlphaFold2). All protein models available as NVIDIA NIM microservices.",
        "drug_discovery": "💊 BioNeMo accelerates drug discovery: generate novel molecules → dock to target proteins → predict ADMET properties → optimize leads.",
        "embeddings": "🧮 ESM-2 (protein) and Nucleotide Transformer (DNA/RNA) provide rich biological embeddings for downstream ML tasks like property prediction.",
        "nim_models": "🔌 BioNeMo NIM models: esmfold, alphafold2, diffdock, molmim, megamolbart, proteinmpnn — all deployable as OpenAI-compatible microservices.",
        "genomics": "🧬 Nucleotide Transformer and GeneFormer enable genome-scale prediction tasks: gene expression, variant effect prediction, regulatory element classification."
    }
    return explanations.get(topic, f"Unknown topic: {topic}")


TOOL_HANDLERS = {
    "bionemo_protein_folding": bionemo_protein_folding,
    "bionemo_molecule_generate": bionemo_molecule_generate,
    "bionemo_docking": bionemo_docking,
    "bionemo_embeddings": bionemo_embeddings,
    "bionemo_setup": bionemo_setup,
    "bionemo_finetune": bionemo_finetune,
    "bionemo_explain": bionemo_explain,
}
