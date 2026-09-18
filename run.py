import json
import sys
from pathlib import Path

from app.main import MedicalRecordAnalyzer


def main():

    if len(sys.argv) < 2:
        print(
            "Usage: python run.py "
            "<medical_record.pdf>"
        )
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(
            f"Error: File not found: {input_path}"
        )
        sys.exit(1)

    if input_path.suffix.lower() != ".pdf":
        print(
            "Error: Input file must be a PDF."
        )
        sys.exit(1)

    print()
    print("======================================")
    print(" Lawdie Medical Record Analyzer")
    print("======================================")
    print()

    analyzer = MedicalRecordAnalyzer()

    analysis = analyzer.analyze(
        input_path
    )

    output_dir = Path("data/output")
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    stem = input_path.stem

    json_path = output_dir / (
        f"{stem}_analysis.json"
    )

    narrative_path = output_dir / (
        f"{stem}_demand.txt"
    )

    with json_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            analysis.model_dump(),
            file,
            indent=2,
            ensure_ascii=False,
        )

    narrative = (
        analysis.demand_narrative.narrative
        if analysis.demand_narrative
        else ""
    )

    with narrative_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        file.write(narrative)

    print()
    print("======================================")
    print(" Analysis Complete")
    print("======================================")

    print(
        f"Patient: "
        f"{analysis.facts.patient_name or 'Unknown'}"
    )

    print(
        f"Injuries: "
        f"{len(analysis.facts.injuries)}"
    )

    print(
        f"Diagnoses: "
        f"{len(analysis.facts.diagnoses)}"
    )

    print(
        f"Treatments: "
        f"{len(analysis.facts.treatments)}"
    )

    print(
        f"Pain / functional impacts: "
        f"{len(analysis.facts.pain_and_suffering)}"
    )

    print(
        f"Conflicts: "
        f"{len(analysis.facts.conflicts)}"
    )

    print()
    print(
        f"Structured analysis saved to: "
        f"{json_path}"
    )

    print(
        f"Demand narrative saved to: "
        f"{narrative_path}"
    )


if __name__ == "__main__":
    main()