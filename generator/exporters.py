"""
ExamOps Data Exporter & Manifest Generator
Exports generated datasets to CSV, JSON, and SQL formats, and produces cryptographic SHA-256 manifests.
"""
import os
import csv
import json
import hashlib
from typing import Dict, List, Any

def get_canonical_json_hash(data: Any) -> str:
    """Computes deterministic SHA-256 hash of canonical JSON."""
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

def export_all(
    dataset: Dict[str, List[Dict[str, Any]]],
    ground_truth: List[Dict[str, Any]],
    output_base_dir: str = "data"
) -> Dict[str, Any]:
    """
    Exports all entity datasets to CSV, JSON, and SQL seed files.
    Generates and returns canonical manifest.
    """
    csv_dir = os.path.join(output_base_dir, "csv")
    json_dir = os.path.join(output_base_dir, "json")
    sql_dir = os.path.join(output_base_dir, "sql")

    for d in [csv_dir, json_dir, sql_dir]:
        os.makedirs(d, exist_ok=True)

    manifest = {
        "generator_version": "1.0.0",
        "entity_counts": {},
        "file_checksums": {},
        "canonical_checksums": {},
    }

    # 1. Export JSON & CSV for each entity
    for entity_name, records in dataset.items():
        manifest["entity_counts"][entity_name] = len(records)
        manifest["canonical_checksums"][entity_name] = get_canonical_json_hash(records)

        # JSON Export
        json_path = os.path.join(json_dir, f"{entity_name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, default=str)
        with open(json_path, "rb") as f:
            manifest["file_checksums"][f"json/{entity_name}.json"] = hashlib.sha256(f.read()).hexdigest()

        # CSV Export
        if records:
            csv_path = os.path.join(csv_dir, f"{entity_name}.csv")
            fieldnames = list(records[0].keys())
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in records:
                    row_dict = {}
                    for k, v in r.items():
                        if isinstance(v, (dict, list)):
                            row_dict[k] = json.dumps(v)
                        else:
                            row_dict[k] = v
                    writer.writerow(row_dict)
            with open(csv_path, "rb") as f:
                manifest["file_checksums"][f"csv/{entity_name}.csv"] = hashlib.sha256(f.read()).hexdigest()

    # 2. Export Ground Truth Separately
    gt_json_path = os.path.join(output_base_dir, "ground_truth.json")
    with open(gt_json_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2, default=str)
    with open(gt_json_path, "rb") as f:
        manifest["file_checksums"]["ground_truth.json"] = hashlib.sha256(f.read()).hexdigest()

    if ground_truth:
        gt_csv_path = os.path.join(output_base_dir, "ground_truth.csv")
        # Collect union of all keys preserving deterministic order
        all_keys = []
        for r in ground_truth:
            for k in r.keys():
                if k not in all_keys:
                    all_keys.append(k)
        with open(gt_csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
            writer.writeheader()
            for r in ground_truth:
                row_dict = {}
                for k in all_keys:
                    v = r.get(k, "")
                    if isinstance(v, (dict, list)):
                        row_dict[k] = json.dumps(v)
                    else:
                        row_dict[k] = v
                writer.writerow(row_dict)
        with open(gt_csv_path, "rb") as f:
            manifest["file_checksums"]["ground_truth.csv"] = hashlib.sha256(f.read()).hexdigest()

    # 3. Export SQL Seed
    sql_path = os.path.join(sql_dir, "seed_data.sql")
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("-- ==============================================================================\n")
        f.write("-- ExamOps Synthetic Baseline SQL Seed Data\n")
        f.write("-- Generated deterministically with fixed seed 20261022\n")
        f.write("-- ==============================================================================\n\n")

        # Insertion order respects foreign key topological hierarchy
        ordered_entities = [
            "academic_periods",
            "students",
            "invigilators",
            "user_profiles",
            "courses",
            "course_instructors",
            "enrollments",
            "exams",
            "exam_requirements",
            "rooms",
            "room_capacities",
            "equipment_types",
            "room_equipment",
            "room_availabilities",
            "availabilities",
            "accommodations",
            "accommodation_notes",
        ]

        for ent in ordered_entities:
            records = dataset.get(ent, [])
            if not records:
                continue
            f.write(f"-- Table: {ent} ({len(records)} rows)\n")
            keys = list(records[0].keys())
            cols = ", ".join(keys)
            batch_size = 250
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                f.write(f"INSERT INTO {ent} ({cols}) VALUES\n")
                val_lines = []
                for rec in batch:
                    vals = []
                    for k in keys:
                        v = rec[k]
                        if v is None:
                            vals.append("NULL")
                        elif isinstance(v, bool):
                            vals.append("TRUE" if v else "FALSE")
                        elif isinstance(v, (int, float)):
                            vals.append(str(v))
                        elif isinstance(v, (dict, list)):
                            escaped = json.dumps(v).replace("'", "''")
                            vals.append(f"'{escaped}'::jsonb")
                        else:
                            escaped = str(v).replace("'", "''")
                            vals.append(f"'{escaped}'")
                    val_lines.append(f"  ({', '.join(vals)})")
                f.write(",\n".join(val_lines))
                f.write("\nON CONFLICT DO NOTHING;\n\n")

    with open(sql_path, "rb") as f:
        manifest["file_checksums"]["sql/seed_data.sql"] = hashlib.sha256(f.read()).hexdigest()

    # 4. Write Manifest File
    manifest_path = os.path.join(output_base_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    return manifest
