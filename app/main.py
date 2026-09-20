from pathlib import Path

from app.extraction.fact_extractor import FactExtractor
from app.extraction.schemas import CaseAnalysis
from app.generation.demand_generator import DemandGenerator
from app.ingestion.document_processor import DocumentProcessor
from app.retrieval.chunker import DocumentChunker
from app.retrieval.retriever import MedicalRecordRetriever
from app.validation.conflict_detector import ConflictDetector
from app.validation.grounding import GroundingValidator


class MedicalRecordAnalyzer:

    RETRIEVAL_QUERY = (
        "patient incident injuries diagnoses providers treatments "
        "pain sleep work mobility hobbies daily activities"
    )

    def analyze(
        self,
        file_path: str | Path,
    ) -> CaseAnalysis:

        print("[1/7] Processing medical record...")

        pages = DocumentProcessor().process(
            file_path
        )

        print(
            f"      Loaded {len(pages)} pages."
        )

        print("[2/7] Creating document chunks...")

        chunks = DocumentChunker().chunk_pages(
            pages
        )

        print(
            f"      Created {len(chunks)} chunks."
        )

        print("[3/7] Building retrieval index...")

        retriever = MedicalRecordRetriever()
        retriever.build_index(chunks)

        results = retriever.search(
            self.RETRIEVAL_QUERY,
            top_k=min(12, len(chunks)),
        )

        print(
            f"      Retrieved {len(results)} relevant chunks."
        )

        print("[4/7] Extracting structured facts...")

        facts = FactExtractor().extract(
            results
        )

        print("[5/7] Validating source grounding...")

        grounding_validator = GroundingValidator()

        grounding = grounding_validator.validate_case_facts(
            facts,
            pages,
        )

        print(
            "      Grounding: "
            f"{grounding['valid_citations']}/"
            f"{grounding['total_citations']} "
            "citations valid."
        )

        rejected_count = grounding["invalid_citations"]

        if rejected_count > 0:
            facts = grounding_validator.filter_invalid_facts(
                facts,
                pages,
            )
            print(
                f"      Excluded {rejected_count} unverified "
                "claim(s) from the narrative."
            )

        print("[6/7] Detecting conflicts...")

        conflicts = ConflictDetector().detect(
            facts,
            pages,
        )

        facts.conflicts = conflicts

        print(
            f"      Found {len(conflicts)} conflict(s)."
        )

        print("[7/7] Generating demand narrative...")

        demand = DemandGenerator().generate(
            facts
        )

        return CaseAnalysis(
            facts=facts,
            demand_narrative=demand,
            grounding_report=grounding,
        )