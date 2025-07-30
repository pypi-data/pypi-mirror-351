import os
import sys
import time
import csv
import torch
import esm
import platform
import argparse
import json
import shutil
import tempfile
import subprocess
import pandas as pd
from pathlib import Path
from Bio import SeqIO
from huggingface_hub import hf_hub_download
from antifp2.python_scripts.classifier_module import ProteinClassifier


def parse_envfile(envfile_path):
    if not os.path.exists(envfile_path):
        print(f"Error: The environment file '{envfile_path}' is missing.", file=sys.stderr)
        sys.exit(1)
    paths = {}
    with open(envfile_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                paths[key.strip()] = value.strip()
    return paths


def get_os_specific_key(base_key):
    os_name = platform.system().lower()
    if 'linux' in os_name:
        return f"{base_key}_ubuntu"
    elif 'windows' in os_name:
        return f"{base_key}_windows"
    elif 'darwin' in os_name:
        return f"{base_key}_macos"
    else:
        print(f"Unsupported OS: {os_name}", file=sys.stderr)
        sys.exit(1)


def parse_coverage_section(content):
    hits = set()
    for line in content.splitlines():
        if line.startswith(">"):
            hits.add(line[1:].strip())
    return hits



def adjust_with_blast_and_motif(df, blast_file, motif_file):
    df["blast_adjustment"] = 0.0
    df["motif_adjustment"] = 0.0

    blast_hits = set()
    motif_hits = set()

    if blast_file and Path(blast_file).exists() and Path(blast_file).stat().st_size > 0:
        try:
            blast_df = pd.read_csv(blast_file, sep="\t", header=None)
            for _, row in blast_df.iterrows():
                qid, sid = row[0], row[1]
                if qid in df["ID"].values:
                    if sid.endswith("_1"):
                        df.loc[df["ID"] == qid, "blast_adjustment"] = 0.5
                        blast_hits.add(qid)
                    elif sid.endswith("_0"):
                        df.loc[df["ID"] == qid, "blast_adjustment"] = -0.5
                        blast_hits.add(qid)
        except pd.errors.EmptyDataError:
            print("⚠️ Warning: BLAST output is empty. Skipping BLAST adjustment.")

    if motif_file and Path(motif_file).exists() and Path(motif_file).stat().st_size > 0:
        try:
            content = Path(motif_file).read_text()
            motif_hits = parse_coverage_section(content)
            df.loc[df["ID"].isin(motif_hits), "motif_adjustment"] = 0.5
        except Exception as e:
            print(f"⚠️ Warning: Could not parse MERCI output: {e}")

    df["combined"] = df["probability"] + df["blast_adjustment"] + df["motif_adjustment"]
    df["combined"] = df["combined"].clip(0, 1)
    df["prediction"] = (df["combined"] >= 0.5).astype(int)

    total = len(df)
    blast_only = len(blast_hits - motif_hits)
    motif_only = len(motif_hits - blast_hits)
    both = len(blast_hits & motif_hits)
    none = total - len(blast_hits | motif_hits)

    print(f"\n📊 Adjustment summary:")
    print(f"  Total sequences: {total}")
    print(f"  Adjusted by BLAST only: {blast_only}")
    print(f"  Adjusted by Motif only: {motif_only}")
    print(f"  Adjusted by both BLAST and Motif: {both}")
    print(f"  No adjustment (no hits): {none}")

    return df
# Load environment variables
BASE_PATH = Path(__file__).resolve().parent
PACKAGE_ROOT = BASE_PATH.parent
env_paths = parse_envfile(BASE_PATH / "envfile")

blast_key = get_os_specific_key('BLAST')
blastp_path = PACKAGE_ROOT / env_paths.get(blast_key)
blast_db_path = PACKAGE_ROOT / env_paths.get('BLAST_database')
merci_script_path = PACKAGE_ROOT / env_paths.get('MERCI')
merci_motif_file = PACKAGE_ROOT / env_paths.get('MERCI_motif_file')

def run_prediction(fasta_input_path, output_dir_path, cleanup=True):
    start_time = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"✅ Using device: {device}")

    fasta_input = Path(fasta_input_path)
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    fasta_basename = fasta_input.stem
    final_output_path = output_dir / f"{fasta_basename}.adjusted.csv"

    temp_dir_path = output_dir / "temp"
    temp_dir_path.mkdir(parents=True, exist_ok=True)

    output_csv = temp_dir_path / "results.csv"
    adjusted_csv = temp_dir_path / "results.adjusted.csv"
    rejected_log_path = temp_dir_path / "rejected_log.txt"
    blast_output = temp_dir_path / "results.blast.tsv"
    merci_output = temp_dir_path / "results.merci.out"

    valid_aas = set("ACDEFGHIKLMNPQRSTVWY")
    valid_sequences = []

    with open(rejected_log_path, "w") as rejlog:
        for record in SeqIO.parse(fasta_input, "fasta"):
            seq = str(record.seq).upper()
            if len(seq) < 50:
                rejlog.write(f"{record.id}: Rejected (length < 50)\n")
                continue
            if len(seq) > 3000:
                rejlog.write(f"{record.id}: Rejected (length > 3000)\n")
                continue
            if any(aa not in valid_aas for aa in seq):
                rejlog.write(f"{record.id}: Rejected (non-standard amino acids)\n")
                continue
            valid_sequences.append(record)

    if not valid_sequences:
        raise ValueError("❌ No valid sequences found. Check rejected_log.txt for details.")

    print("⏬ Downloading model files from Hugging Face (if not cached)...")
    repo_id = "raghavagps-group/antifp2"
    torch.serialization.add_safe_globals([esm.data.Alphabet])
    config_path = hf_hub_download(repo_id=repo_id, filename="config.json")
    weights_path = hf_hub_download(repo_id=repo_id, filename="pytorch_model.bin")
    alphabet_path = hf_hub_download(repo_id=repo_id, filename="alphabet.bin")

    with open(config_path, "r") as f:
        config = json.load(f)

    embedding_dim = config["embedding_dim"]
    num_classes = config["num_classes"]

    torch.serialization.add_safe_globals([esm.data.Alphabet])
    alphabet = torch.load(alphabet_path, map_location="cpu", weights_only=False)
    batch_converter = alphabet.get_batch_converter()

    esm_model, _ = esm.pretrained.esm2_t36_3B_UR50D()
    esm_model = esm_model.to(device)

    classifier = ProteinClassifier(esm_model, embedding_dim, num_classes).to(device)
    classifier.load_state_dict(torch.load(weights_path, map_location=device))
    classifier.eval()

    print("✅ Model loaded. Beginning predictions...")

    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "probability"])

        for record in valid_sequences:
            seq = str(record.seq).upper()
            batch = [(record.id, seq)]
            _, _, tokens = batch_converter(batch)
            tokens = tokens.to(device)

            with torch.no_grad():
                logits, _ = classifier(tokens)
                prob = torch.softmax(logits, dim=1)[0][1].item()

            writer.writerow([record.id, prob])
            csvfile.flush()
            print(f"✅ {record.id}: prob={prob:.4f}")

    print("\n✅ Running BLAST...")
    blast_cmd = [
        str(blastp_path),
        "-query", str(fasta_input),
        "-db", str(blast_db_path),
        "-outfmt", "6",
        "-max_target_seqs", "1", "-evalue", "0.001", "-subject_besthit",
        "-out", str(blast_output)
    ]
    subprocess.run(blast_cmd, check=True)

    print("✅ Running MERCI...")
    merci_cmd = [
        str(merci_script_path),
        "-p", str(fasta_input),
        "-i", str(merci_motif_file),
        "-c", "KOOLMAN-ROHM",
        "-o", str(merci_output),
    ]
    subprocess.run(merci_cmd, check=True)

    print("✅ Adjusting predictions with BLAST and MERCI...")
    df = pd.read_csv(output_csv)
    df_adjusted = adjust_with_blast_and_motif(df, blast_output, merci_output)
    df_adjusted.to_csv(adjusted_csv, index=False)
    shutil.copy(adjusted_csv, final_output_path)

    elapsed_time = time.time() - start_time
    print(f"\n✅ Final output: {final_output_path}")
    print(f"⏱️ Time taken: {elapsed_time:.2f} seconds")

    if cleanup:
        shutil.rmtree(temp_dir_path)
        print("🧹 Cleaned up intermediate files")
    else:
        print(f"⚠️ Intermediate files kept at: {temp_dir_path}")


def main():
    parser = argparse.ArgumentParser(description="Predict with fine-tuned ESM2-t36 model")
    parser.add_argument("--fasta", type=str, required=True, help="Path to input FASTA file")
    parser.add_argument("--output", type=str, required=True, help="Directory where output files will be stored")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep intermediate files like raw outputs")
    args = parser.parse_args()

    run_prediction(
        fasta_input_path=args.fasta,
        output_dir_path=args.output,
        cleanup=not args.no_cleanup
    )


if __name__ == "__main__":
    main()

