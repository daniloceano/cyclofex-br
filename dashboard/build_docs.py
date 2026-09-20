"""Build the dashboard's static HTML pages from the canonical Markdown docs.

Requires Pandoc at build time. The generated pages have no runtime dependencies.
Run: python3 dashboard/build_docs.py
"""

from html import escape
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard"
TEMPLATE = (DASHBOARD / "doc_template.tmpl").read_text(encoding="utf-8")
DOCUMENTS = {
    "open_questions": "Questões abertas",
    "experiments": "Experimentos",
    "decisions": "Decisões",
    "methodology": "Metodologia",
    "assumptions": "Pressupostos",
    "data_dictionary": "Dicionário de dados",
    "solicitacao_agente_q002_q003": "Respostas sobre Q-002 e Q-003",
}


def local_html_link(match: re.Match[str]) -> str:
    """Keep links between docs inside the dashboard instead of opening Markdown."""
    return f'href="{match.group(1)}.html{match.group(2) or ""}"'


def main() -> None:
    for stem, title in DOCUMENTS.items():
        source = ROOT / "docs" / f"{stem}.md"
        try:
            converted = subprocess.run(
                ["pandoc", "--from=gfm", "--to=html5", "--wrap=none", str(source)],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        except FileNotFoundError as error:
            raise SystemExit("Pandoc é necessário para atualizar as páginas HTML.") from error

        body = re.sub(r'href="([a-z0-9_]+)\.md(#[^"]*)?"', local_html_link, converted)
        page = (
            TEMPLATE.replace("{{TITLE}}", escape(title))
            .replace("{{BODY}}", body)
            .replace("{{SOURCE}}", f"../docs/{stem}.md")
        )
        target = DASHBOARD / f"{stem}.html"
        target.write_text(page, encoding="utf-8")
        print(f"Wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
