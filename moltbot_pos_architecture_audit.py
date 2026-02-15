import argparse
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Dict, Any, Tuple


# --- CONFIG (VERSIONED OUTPUT CONTRACT) ---

SCHEMA_VERSION = "1.0.0"
PROJECT_NAME = "Moltbot_PoS_Architecture_Audit_001"
OPERATIONAL_INTENT = "Transition from uncontrolled narration to precise protocol (PoS) and data logic."

MOLTBOT_SCRIPTS = {
    "PoS Test Agent": "moltbot_silence_test.py (PoS Agent)",
    "Auto-Summary Auditor": "moltbot_auto_summary.py (Data Auditor)",
}

DEFAULT_OUT_DIR = "./out"


# --- UTILITIES ---

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def file_sha256(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


# --- CORE GENERATORS (CONTENT) ---

def generate_system_report(date_generated: str) -> str:
    report_template = f"""\n# System Systemowy Moltbot - Raport Audytu Architektonicznego

**Projekt:** {PROJECT_NAME}
**Wersja Schemy:** {SCHEMA_VERSION}
**Data Raportu (UTC):** {date_generated}
**Kierunek Operacyjny:** {OPERATIONAL_INTENT}

---

## I. Status Modułów i Wdrożenia

| Moduł | Cel | Status Wdrożenia |
| :--- | :--- | :--- |
| **PoS Test Agent** | Test Protokołu Milczenia (PoS) i komunikacji nienarracyjnej. | Gotowy skrypt `{MOLTBOT_SCRIPTS['PoS Test Agent']}` |
| **Auto-Summary** | Audyt i analiza statystyczna danych wejściowych (XLSX/CSV). | Gotowy skrypt `{MOLTBOT_SCRIPTS['Auto-Summary Auditor']}` |

## II. Podsumowanie Wniosków Operacyjnych

Seria działań zakończona pełnym wdrożeniem dwóch krytycznych modułów agentów. Głównym celem było utworzenie formalnych ram dla interakcji AI oraz eliminacja szumu (halucynacji/narracji) na rzecz precyzyjnego protokołu i logiki.

### Zrealizowane Punkty Techniczne:

1.  **Definicja Zadania:** Pełen JSON task dla PoS_Moltbook_Test_001.
2.  **Protokół PoS:** Zaprojektowanie i wdrożenie kodu testowego PoS.
3.  **Narzędzie Analityczne:** Implementacja pełnego modułu audytowego (Moltbot Auto-Summary) ze statystykami opisowymi i analizą braków danych.
4.  **Zgodność Systemowa:** Utrzymano zgodność z logiką PoS i protokołami bezpieczeństwa.

## III. Obecny Stan Systemu (Moltbot Subsystem)

Infrastruktura kodowa jest gotowa do integracji na wyższym poziomie (M2M, AI005_GlobalDeck). Moduły są autonomiczne i spełniają funkcje: Agenta Testowego oraz Modułu Audytowego.

### Gotowość do Integracji:
*   **M2M/AI005:** Wysoka (Moduły są zorientowane na JSON/plikowe IO).
*   **Weryfikacja Danych:** Wbudowany mechanizm audytu statystycznego.

---
"""
    return report_template


def generate_mermaid_code() -> str:
    # Czysty Mermaid (bez Markdown), aby UI/pipeline mógł to renderować jak chce.
    return """\ngraph TD
    subgraph Core_System_Interface
        A[AI005/Marian/M2M Core]
    end

    subgraph Moltbot_Subsystem
        B(Moltbot Agent)
        C{{Protokół PoS: MILCZENIE | LOGIKA}}
        D[moltbot_silence_test.py]
    end

    subgraph Auditing_Layer
        E[Dane Wejściowe XLSX/CSV]
        F[moltbot_auto_summary.py]
    end

    % 1. Agent Execution Flow
    B -->|Zadanie PoS_001| D
    D -->|Adherencja| C
    C -- Protokół Wynikowy (JSON) --> A

    % 2. Audit and Reporting Flow
    E -->|Input Data| F
    F -->|Raport Analityczny| A

    % 3. Core Interaction
    A -->|Polecenia/Konfiguracja| B

    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#ccf,stroke:#000
    style A fill:#aaffaa
    style F fill:#ffffcc
"""


def wrap_mermaid_in_markdown(mermaid_code: str) -> str:
    return f"""\n# DIAGRAM ARCHITEKTURY SYSTEMU (Mermaid)

```mermaid
{mermaid_code}```
"""


def propose_architecture_step() -> str:
    step_proposal = {
        "Kategoria": "Integracja Krytyczna (A)",
        "Cel": "Wprowadzenie zaprojektowanych modułów do aktywnego środowiska.",
        "Uzasadnienie": (
            "Moduły testowe i audytowe są gotowe. Najwyższy priorytet ma włączenie Moltbota i "
            "Auto-Summary do nadrzędnego systemu (AI005/M2M) w celu rozpoczęcia operacyjnych testów "
            "Proof-of-Silence i audytów higieny danych. Zapewni to szybką walidację koncepcji PoS "
            "w realistycznym środowisku M2M."
        ),
        "Akcja": "Integracja Moltbota z AI005_GlobalDeck i uruchomienie Auto-Summary jako modułu weryfikacyjnego danych przed zasileniem agentów.",
    }

    return f"""\n## IV. Propozycja Następnego Kroku Architektury

### Wybrana Strategia: {step_proposal['Kategoria']}

**Cel Architektoniczny:** {step_proposal['Cel']}
**Uzasadnienie:** {step_proposal['Uzasadnienie']}
**Akcja Operacyjna:** {step_proposal['Akcja']}

"""


# --- MANIFEST (JSON-FIRST) ---

@dataclass
class ArtifactRef:
    name: str
    filename: str
    sha256: str
    bytes: int
    content_type: str


@dataclass
class Manifest:
    schema_version: str
    project_name: str
    generated_at_utc: str
    operational_intent: str
    scripts: Dict[str, str]
    artifacts: Dict[str, ArtifactRef]

    def to_json(self) -> str:
        obj = asdict(self)
        # ArtifactRef jest dataclass -> już spłaszczone w asdict
        return json.dumps(obj, ensure_ascii=False, indent=2)


def write_artifact(out_dir: Path, filename: str, content: str, content_type: str) -> Tuple[Path, ArtifactRef]:
    path = out_dir / filename
    path.write_text(content, encoding="utf-8")
    ref = ArtifactRef(
        name=filename,
        filename=filename,
        sha256=file_sha256(path),
        bytes=path.stat().st_size,
        content_type=content_type,
    )
    return path, ref


# --- RUNNER ---

def run_full_system_audit(out_dir: str, stdout_only: bool = False) -> Dict[str, Any]:
    generated_at = now_utc_iso()
    report_md = generate_system_report(generated_at)
    mermaid = generate_mermaid_code()
    diagram_md = wrap_mermaid_in_markdown(mermaid)
    proposal_md = propose_architecture_step()

    if stdout_only:
        print(report_md)
        print("-" * 80)
        print("MERMAID (RAW)")
        print(mermaid)
        print("-" * 80)
        print(proposal_md)
        return {
            "schema_version": SCHEMA_VERSION,
            "generated_at_utc": generated_at,
            "stdout_only": True,
        }

    out = Path(out_dir)
    ensure_dir(out)

    _, report_ref = write_artifact(out, "report.md", report_md, "text/markdown; charset=utf-8")
    _, mermaid_ref = write_artifact(out, "diagram.mmd", mermaid, "text/plain; charset=utf-8")
    _, diagram_md_ref = write_artifact(out, "diagram.md", diagram_md, "text/markdown; charset=utf-8")
    _, proposal_ref = write_artifact(out, "proposal.md", proposal_md, "text/markdown; charset=utf-8")

    manifest = Manifest(
        schema_version=SCHEMA_VERSION,
        project_name=PROJECT_NAME,
        generated_at_utc=generated_at,
        operational_intent=OPERATIONAL_INTENT,
        scripts=MOLTBOT_SCRIPTS,
        artifacts={
            "report_md": report_ref,
            "diagram_mermaid": mermaid_ref,
            "diagram_md": diagram_md_ref,
            "proposal_md": proposal_ref,
        },
    )

    manifest_path = out / "manifest.json"
    manifest_path.write_text(manifest.to_json(), encoding="utf-8")

    result = {
        "schema_version": SCHEMA_VERSION,
        "project_name": PROJECT_NAME,
        "generated_at_utc": generated_at,
        "out_dir": str(out.resolve()),
        "manifest": str(manifest_path.resolve()),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Moltbot PoS Architecture Audit (pipeline-ready)")
    p.add_argument("--out", default=DEFAULT_OUT_DIR, help="Output directory for artifacts (default: ./out)")
    p.add_argument("--stdout-only", action="store_true", help="Print artifacts to stdout only (no files)")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_full_system_audit(out_dir=args.out, stdout_only=args.stdout_only)
