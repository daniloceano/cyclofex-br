"""Build the static scientific report from the canonical Markdown sources.

Requires Pandoc at build time. Generated pages have no runtime dependency.
Run from the repository root with: python3 dashboard/build_docs.py
"""

from html import escape
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DASHBOARD = ROOT / "dashboard"
TEMPLATE = (DASHBOARD / "doc_template.tmpl").read_text(encoding="utf-8")

PUBLISHED_MEDIA = (
    ("02_exploratory_analysis", "all_tracks_by_phase.png"),
    ("02_exploratory_analysis", "wind_speed_boxplots.png"),
    ("02_exploratory_analysis", "exceedance_occurrence_by_phase.png"),
    ("02_exploratory_analysis", "exceedances_by_phase_and_quadrant.png"),
    ("02_exploratory_analysis", "max_wind_cyclone_peak_frame.png"),
    ("02_exploratory_analysis", "max_wind_cyclone_animation.mp4"),
    ("03_e001_orientation", "translation_speed_diagnostic.png"),
    ("03_e001_orientation", "orientation_comparison.png"),
    ("03_e001_orientation", "orientation_by_phase.png"),
    ("03_e001_orientation", "rotation_sanity_checks.png"),
    ("03_e001_orientation", "methodology_flow.png"),
    ("03_e001_orientation", "bin_grid_real_state.png"),
    ("03_e001_orientation", "coordinate_frames_example.png"),
    ("03_e001_orientation", "binning_entropy_example.png"),
    ("03_e001_orientation", "concentration_area_example.png"),
    ("03_e001_orientation", "rms_vector_geometry.png"),
    ("03_e001_orientation", "geometric_metrics_example.png"),
    ("03_e001_orientation", "bootstrap_scheme.png"),
    ("04_e002_weighting", "methodology_flow.png"),
    ("04_e002_weighting", "weighting_hierarchy_example.png"),
    ("04_e002_weighting", "positive_states_per_cyclone.png"),
    ("04_e002_weighting", "cumulative_cyclone_contribution.png"),
    ("04_e002_weighting", "centered_weighting_comparison.png"),
    ("04_e002_weighting", "motion_weighting_comparison.png"),
    ("04_e002_weighting", "representation_equal_cyclone.png"),
    ("04_e002_weighting", "metric_differences_bootstrap.png"),
)

PAGES = {
    "index.md": ("index.html", "Visão geral", "Projeto científico", "Problema, estratégia, evidências e próximo passo."),
    "scientific_plan.md": ("scientific_plan.html", "Plano científico", "Projeto", "O que foi proposto, adotado, testado ou permanece em aberto."),
    "data.md": ("data.html", "Dados", "Base científica", "Origem, significado, cobertura e unidades da base empírica."),
    "data_preparation.md": ("data_preparation.html", "Preparação dos dados", "Base científica", "Como foi construída e validada a amostra de estados ciclone–tempo."),
    "exploratory_analysis.md": ("exploratory_analysis.html", "Análise exploratória", "Análises", "Perguntas, método descritivo, resultados, interpretação e limites."),
    "e001_orientation.md": ("e001_orientation.html", "E-001 · Orientação", "Experimento", "Comparação formal entre quadrantes fixos e rotacionados pelo movimento."),
    "e002_weighting.md": ("e002_weighting.html", "E-002 · Weighting", "Experimento", "Sensibilidade a peso por estado versus por ciclone."),
    "experiments.md": ("experiments.html", "Experimentos", "Análises", "Caderno estruturado de testes planejados, executados e negativos."),
    "methodology.md": ("methodology.html", "Metodologia atual", "Síntese", "Procedimentos efetivamente adotados e alcance das conclusões."),
    "results.md": ("results.html", "Resultados e evidências", "Síntese", "O que foi observado, o que significa e o que ainda não demonstra."),
    "limitations.md": ("limitations.html", "Limitações", "Síntese", "Restrições dos dados, do suporte, da seleção e dos métodos atuais."),
    "open_questions.md": ("open_questions.html", "Questões abertas", "Síntese", "Conhecimento disponível, lacunas, evidência necessária e dependências."),
    "decisions.md": ("decisions.html", "Decisões", "Auditoria", "Registro persistente das escolhas e condições de revisão."),
    "assumptions.md": ("assumptions.html", "Pressupostos", "Auditoria", "Hipóteses inferenciais em uso e regras para seu registro."),
    "reproducibility.md": ("reproducibility.html", "Proveniência e reprodutibilidade", "Auditoria", "Linhagem, versões, produtos, código e comandos."),
    "documentation_guidelines.md": ("internal/documentation_guidelines.html", "Padrão documental", "Referência técnica", "Instrução permanente para manter o relatório científico."),
    "internal/README.md": ("internal/index.html", "Referência técnica", "Documentação interna", "Execução, manutenção, contratos e arquitetura do repositório."),
    "internal/repository_structure.md": ("internal/repository_structure.html", "Estrutura do repositório", "Documentação interna", "Responsabilidades, diretórios e convenções."),
    "internal/computational_workflows.md": ("internal/computational_workflows.html", "Fluxos computacionais", "Documentação interna", "Ambiente, comandos, cache, produtos e geração do dashboard."),
    "internal/data_reference.md": ("internal/data_reference.html", "Referência dos dados", "Documentação interna", "Schemas, campos, arquivos, hashes e contratos."),
    "internal/q002_q003_provenance.md": ("internal/q002_q003_provenance.html", "Investigação de Q-002 e Q-003", "Documentação interna", "Reconstrução detalhada do código e das convenções herdadas."),
    "internal/human_audit.md": ("internal/human_audit.html", "Auditoria humana simulada", "Documentação interna", "Verificação do relatório pela perspectiva de um pesquisador externo."),
}

NAVIGATION = [
    ("Projeto", [("index.md", "Visão geral"), ("scientific_plan.md", "Plano científico")]),
    ("Base científica", [("data.md", "Dados"), ("data_preparation.md", "Preparação dos dados")]),
    ("Análises", [("exploratory_analysis.md", "Análise exploratória"), ("e001_orientation.md", "E-001 · Orientação"), ("e002_weighting.md", "E-002 · Weighting"), ("experiments.md", "Experimentos")]),
    ("Síntese", [
        ("methodology.md", "Metodologia atual"),
        ("results.md", "Resultados e evidências"),
        ("limitations.md", "Limitações"),
        ("open_questions.md", "Questões abertas"),
    ]),
    ("Auditoria", [
        ("decisions.md", "Decisões"),
        ("reproducibility.md", "Proveniência e reprodução"),
        ("internal/README.md", "Referência técnica"),
    ]),
]

MD_LINK = re.compile(r'href="([^"]+\.md)(#[^"]*)?"')


class SectionParser(HTMLParser):
    """Collect second-level headings and their Pandoc-generated anchors."""

    def __init__(self) -> None:
        super().__init__()
        self.sections: list[tuple[str, str]] = []
        self._heading_id: str | None = None
        self._heading_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "h2":
            return
        heading_id = dict(attrs).get("id")
        if heading_id:
            self._heading_id = heading_id
            self._heading_text = []

    def handle_data(self, data: str) -> None:
        if self._heading_id is not None:
            self._heading_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "h2" or self._heading_id is None:
            return
        title = " ".join("".join(self._heading_text).split())
        if title:
            self.sections.append((self._heading_id, title))
        self._heading_id = None
        self._heading_text = []


def page_sections(html: str) -> list[tuple[str, str]]:
    """Return the main sections shown in the contextual sidebar summary."""
    parser = SectionParser()
    parser.feed(html)
    return parser.sections


def section_navigation(sections: list[tuple[str, str]]) -> str:
    """Render links to the sections of the current page only."""
    section_links = "".join(
        f'<a class="page-toc-link" href="#{escape(section_id, quote=True)}">'
        f"{escape(section_title)}</a>"
        for section_id, section_title in sections
    )
    return (
        '<nav class="page-toc" aria-label="Seções desta página">'
        '<p class="page-toc-label">Nesta página</p>'
        f"{section_links}"
        "</nav>"
    )


def relative_output(current_output: str, target_source: str) -> str:
    """Return a link from one generated page to another generated page."""
    target_output = PAGES[target_source][0]
    start = str(PurePosixPath(current_output).parent)
    if start == ".":
        start = ""
    return posixpath.relpath(target_output, start or ".")


def rewrite_doc_links(html: str, source_name: str, output_name: str) -> str:
    """Rewrite Markdown-source links only when their targets are generated docs."""
    source_parent = str(PurePosixPath(source_name).parent)

    def replace(match: re.Match[str]) -> str:
        raw_target, anchor = match.group(1), match.group(2) or ""
        resolved = posixpath.normpath(posixpath.join(source_parent, raw_target))
        if resolved not in PAGES:
            return match.group(0)
        return f'href="{relative_output(output_name, resolved)}{anchor}"'

    return MD_LINK.sub(replace, html)


def publish_media_assets() -> None:
    """Mirror browser-visible outputs inside the self-contained dashboard."""
    for directory, filename in PUBLISHED_MEDIA:
        source = ROOT / "outputs" / directory / filename
        target = DASHBOARD / "assets" / directory / filename
        if not source.is_file():
            raise SystemExit(f"Produto visual ausente: {source.relative_to(ROOT)}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def rewrite_media_links(html: str, output_name: str) -> str:
    """Point generated HTML to assets that remain inside dashboard/."""
    output_parent = str(PurePosixPath(output_name).parent)
    if output_parent == ".":
        output_parent = ""

    for directory, filename in PUBLISHED_MEDIA:
        canonical = f"../outputs/{directory}/{filename}"
        published = posixpath.relpath(
            f"assets/{directory}/{filename}",
            output_parent or ".",
        )
        html = html.replace(f'"{canonical}"', f'"{published}"')
    return html


def navigation(
    current_source: str,
    current_output: str,
    sections: list[tuple[str, str]],
) -> str:
    groups = []
    current_page_in_navigation = False
    for label, items in NAVIGATION:
        links = []
        contains_current_page = False
        for source_name, title in items:
            active = source_name == current_source
            contains_current_page = contains_current_page or active
            current_page_in_navigation = current_page_in_navigation or active
            attrs = ' class="active" aria-current="page"' if active else ""
            href = relative_output(current_output, source_name)
            links.append(f'<a href="{escape(href)}"{attrs}>{escape(title)}</a>')
            if active and sections:
                links.append(section_navigation(sections))
        group_class = "nav-group has-page-toc" if contains_current_page and sections else "nav-group"
        groups.append(
            f'<div class="{group_class}">'
            f'<p class="side-label">{escape(label)}</p>'
            + "".join(links)
            + "</div>"
        )
    if sections and not current_page_in_navigation:
        current_title = PAGES[current_source][1]
        current_href = relative_output(current_output, current_source)
        groups.insert(
            0,
            '<div class="nav-group has-page-toc">'
            '<p class="side-label">Página atual</p>'
            f'<a href="{escape(current_href)}" class="active" aria-current="page">'
            f"{escape(current_title)}</a>"
            f"{section_navigation(sections)}"
            "</div>",
        )
    return "".join(groups)


def build_page(source_name: str, config: tuple[str, str, str, str]) -> None:
    output_name, title, eyebrow, note = config
    source = DOCS / source_name
    target = DASHBOARD / output_name
    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        converted = subprocess.run(
            ["pandoc", "--from=gfm", "--to=html5", "--mathml", "--wrap=none", str(source)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except FileNotFoundError as error:
        raise SystemExit("Pandoc é necessário para atualizar as páginas HTML.") from error

    body = rewrite_doc_links(converted, source_name, output_name)
    body = rewrite_media_links(body, output_name)
    output_parent = str(PurePosixPath(output_name).parent)
    if output_parent == ".":
        output_parent = ""
    asset_prefix = posixpath.relpath(".", output_parent or ".")
    if asset_prefix == ".":
        asset_prefix = ""
    else:
        asset_prefix += "/"
    source_href = posixpath.relpath(f"docs/{source_name}", posixpath.join("dashboard", output_parent))
    home_href = relative_output(output_name, "index.md")

    page = (
        TEMPLATE.replace("{{TITLE}}", escape(title))
        .replace("{{EYEBROW}}", escape(eyebrow))
        .replace("{{NOTE}}", escape(note))
        .replace("{{BODY}}", body)
        .replace("{{NAVIGATION}}", navigation(source_name, output_name, page_sections(body)))
        .replace("{{SOURCE}}", escape(source_href))
        .replace("{{HOME}}", escape(home_href))
        .replace("{{ASSET_PREFIX}}", asset_prefix)
    )
    target.write_text(page, encoding="utf-8")
    print(f"Wrote {target.relative_to(ROOT)}")


def main() -> None:
    publish_media_assets()
    for source_name, config in PAGES.items():
        build_page(source_name, config)


if __name__ == "__main__":
    main()
