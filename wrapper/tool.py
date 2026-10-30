"""EZKinetics: predicted kcat, Km and kcat/Km for every enzyme-substrate pair.

Runs the method's inference/predict.py, from the base image, on a CSV of all pairs at the
job's assay conditions, then reads its predictions back.
"""
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

PREDICT_DIR = Path("/usr/app/EZKinetics/inference")

# predict.py's output columns -> results.json keys
PREDICTED = {"kcat/Km (1/mM*1/s)": "kcat_km", "kcat (1/s)": "kcat", "Km (mM)": "km"}

# The models were trained on sequences truncated to this many residues, and predict.py
# truncates longer ones the same way
MAX_RESIDUES = 1022


def run(job: dict, input_dir: Path, output_dir: Path) -> dict:
    ph = job.get("ph", 7.0)
    temperature = job.get("temperature", 25.0)
    pairs = [(enzyme, substrate) for enzyme in job["enzymes"] for substrate in job["substrates"]]

    with tempfile.TemporaryDirectory() as work:
        pairs_csv = Path(work) / "pairs.csv"
        predictions_csv = Path(work) / "predictions.csv"
        with open(pairs_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Sequence", "SMILES", "pH", "Temperature"])
            for enzyme, substrate in pairs:
                # ESM's alphabet is upper case; lower-case residues would be read as unknown
                writer.writerow([enzyme["sequence"].upper(), substrate["smiles"], ph, temperature])

        subprocess.run(
            [sys.executable, "predict.py", "--input", str(pairs_csv), "--output", str(predictions_csv)],
            cwd=PREDICT_DIR, check=True,
        )

        with open(predictions_csv, newline="") as f:
            rows = list(csv.DictReader(f))

    if len(rows) != len(pairs):
        raise RuntimeError(f"predict.py returned {len(rows)} rows for {len(pairs)} pairs")

    predictions = [
        {
            "enzyme_id": enzyme["id"],
            "substrate_id": substrate["id"],
            **{key: float(row[column]) for column, key in PREDICTED.items()},
        }
        for (enzyme, substrate), row in zip(pairs, rows)
    ]

    with open(output_dir / "predictions.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["enzyme_id", "substrate_id", "smiles", "pH", "temperature (C)", *PREDICTED])
        for (enzyme, substrate), prediction in zip(pairs, predictions):
            writer.writerow([enzyme["id"], substrate["id"], substrate["smiles"], ph, temperature,
                             *(prediction[key] for key in PREDICTED.values())])

    return {
        "conditions": {"ph": ph, "temperature": temperature},
        "truncated_enzyme_ids": [e["id"] for e in job["enzymes"] if len(e["sequence"]) > MAX_RESIDUES],
        "predictions": predictions,
        "artifacts": [
            {"name": "predictions.csv", "media_type": "text/csv",
             "description": "Every pair's predictions as CSV"},
        ],
    }
