from __future__ import annotations

"""Normalizador de Markdown para o projeto.

Regras markdownlint tratadas automaticamente:
- MD009/no-trailing-spaces
- MD022/blanks-around-headings
- MD024/no-duplicate-heading (desambiguação por sufixo)
- MD026/no-trailing-punctuation (em títulos)
- MD028/no-blanks-blockquote
- MD031/blanks-around-fences
- MD032/blanks-around-lists
- MD034/no-bare-urls (para URLs http/https)
- MD040/fenced-code-language
- MD051/link-fragments (normalização de TOC)
- MD060/table-column-style (normalização básica de pipes/espaços)

Observações:
- O script também aplica padronizações auxiliares (quebras de linha, compactação de
    linhas em branco consecutivas e normalização de blocos de tabela).

Modos de execução:
- standard (padrão): equilíbrio entre segurança e correções estruturais.
- safe: conservador, evita transformações estruturais mais agressivas.
- strict: agressivo, aplica conversões estruturais adicionais.
"""

import argparse
import re
import unicodedata
from pathlib import Path
from typing import Iterable

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
LIST_RE = re.compile(r"^\s{0,3}([-*+]|\d+[.)])\s+")
ORDERED_RE = re.compile(r"^(\s{0,3})(\d+)[.)]\s+(.*)$")
UNORDERED_RE = re.compile(r"^(\s*)([-*+])\s+(.*)$")
FENCE_RE = re.compile(r"^(```+|~~~+)\s*(.*)$")
URL_RE = re.compile(r"(?<!\()(?<!<)(https?://[^\s)>]+)")
TOC_ITEM_RE = re.compile(r"^(\s*[-*+]\s+)\[([^\]]+)\]\(#([^\)]+)\)\s*$")
LINK_ITEM_RE = re.compile(r"^(\s*[-*+]\s+)\[([^\]]+)\]\([^\)]+\)\s*$")
EMPHASIS_HEADING_RE = re.compile(r"^\*\*(\d+\..+)\*\*$")


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def normalize_table_line(line: str) -> str:
    stripped = line.strip()
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    return "| " + " | ".join(cells) + " |"


def slugify(title: str) -> str:
    value = title.strip()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.lower()
    value = re.sub(r"[`*_~]", "", value)
    value = re.sub(r"[\s]+", "-", value)
    value = re.sub(r"[^\w\-]", "", value, flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def normalize_toc_section(lines: list[str]) -> list[str]:
    """
    Remove links frágeis do bloco de índice/TOC, mantendo apenas os itens textuais.
    """
    normalized = list(lines)
    index = 0

    while index < len(normalized):
        line = normalized[index]
        heading_match = HEADING_RE.match(line)
        if not heading_match:
            index += 1
            continue

        heading_level = len(heading_match.group(1))
        heading_text = heading_match.group(2).strip().lower()
        if "índice" not in heading_text and "indice" not in heading_text:
            index += 1
            continue

        cursor = index + 1
        while cursor < len(normalized):
            next_heading = HEADING_RE.match(normalized[cursor])
            if next_heading and len(next_heading.group(1)) <= heading_level:
                break

            link_item = LINK_ITEM_RE.match(normalized[cursor])
            if link_item:
                prefix, text_label = link_item.group(1), link_item.group(2)
                normalized[cursor] = f"{prefix}{text_label}"

            cursor += 1

        index = cursor

    return normalized


def normalize_blockquote_blanks(lines: list[str]) -> list[str]:
    normalized: list[str] = []
    total = len(lines)
    for index, line in enumerate(lines):
        if line.strip() != "":
            normalized.append(line)
            continue

        prev_is_quote = bool(normalized) and normalized[-1].lstrip().startswith(">")
        next_is_quote = index + 1 < total and lines[index + 1].lstrip().startswith(">")
        if prev_is_quote and next_is_quote:
            continue

        normalized.append(line)
    return normalized


def normalize_content(text: str, mode: str = "standard") -> str:
    lines = text.replace("\r\n", "\n").split("\n")

    lines = [re.sub(r"[ \t]+$", "", line) for line in lines]
    lines = [URL_RE.sub(r"<\1>", line) for line in lines]
    lines = [normalize_table_line(line) if is_table_line(line) else line for line in lines]

    out: list[str] = []
    in_fence = False
    fence_char = ""
    for line in lines:
        match = FENCE_RE.match(line)
        if match:
            token, info = match.group(1), match.group(2).strip()
            if not in_fence:
                in_fence = True
                fence_char = token[0]
                if info == "":
                    info = "text"
            else:
                if token[0] == fence_char:
                    in_fence = False
                    fence_char = ""
            out.append(token + (f" {info}" if info else ""))
        else:
            out.append(line)
    lines = out

    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match:
            title = re.sub(r"[:：]\s*$", "", match.group(2).strip())
            lines[index] = f"{match.group(1)} {title}".rstrip()

    if mode == "strict":
        for index, line in enumerate(lines):
            match = EMPHASIS_HEADING_RE.match(line.strip())
            if not match:
                continue
            content = match.group(1).strip()
            if content:
                lines[index] = f"### {content}"

    if mode in {"standard", "strict"}:
        lines = normalize_toc_section(lines)

    seen: dict[tuple[int, str], int] = {}
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if not match:
            continue
        hashes, title = match.group(1), match.group(2).strip()
        key = (len(hashes), title.lower())
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 1:
            lines[index] = f"{hashes} {title} ({seen[key]})"

    heading_titles = [match.group(2).strip() for line in lines if (match := HEADING_RE.match(line))]
    heading_slugs = {slugify(title) for title in heading_titles}

    if mode != "safe":
        normalized_toc: list[str] = []
        for line in lines:
            match = TOC_ITEM_RE.match(line)
            if not match:
                normalized_toc.append(line)
                continue
            prefix, text_label = match.group(1), match.group(2)
            target = slugify(text_label)
            if target in heading_slugs:
                normalized_toc.append(f"{prefix}[{text_label}](#{target})")
            else:
                normalized_toc.append(f"{prefix}{text_label}")
        lines = normalized_toc

    in_fence = False
    fence_char = ""
    for index, line in enumerate(lines):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            token = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_char = token[0]
            elif token[0] == fence_char:
                in_fence = False
                fence_char = ""
            continue

        if in_fence:
            continue

        if mode in {"standard", "strict"}:
            ordered_match = ORDERED_RE.match(line)
            if ordered_match:
                indent, _, content = ordered_match.groups()
                lines[index] = f"{indent}1. {content}"
                continue

            unordered_match = UNORDERED_RE.match(line)
            if unordered_match:
                indent, _, content = unordered_match.groups()
                prev_non_blank = ""
                prev_index = index - 1
                while prev_index >= 0:
                    if lines[prev_index].strip():
                        prev_non_blank = lines[prev_index]
                        break
                    prev_index -= 1

                if len(indent) >= 2:
                    if ORDERED_RE.match(prev_non_blank):
                        lines[index] = f"   - {content}"
                    else:
                        lines[index] = f"- {content}"
                    continue

                prev_unordered = UNORDERED_RE.match(prev_non_blank)
                if prev_unordered and len(prev_unordered.group(1)) >= 2:
                    lines[index] = f"   - {content}"
                    continue

                lines[index] = f"- {content}"

    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match:
            title = re.sub(r"[:：.!?]\s*$", "", match.group(2).strip())
            lines[index] = f"{match.group(1)} {title}".rstrip()

    changed = True
    while changed:
        changed = False
        index = 0
        while index < len(lines):
            line = lines[index]
            if HEADING_RE.match(line):
                if index > 0 and lines[index - 1].strip() != "":
                    lines.insert(index, "")
                    changed = True
                    index += 1
                if index + 1 < len(lines) and lines[index + 1].strip() != "":
                    lines.insert(index + 1, "")
                    changed = True
                index += 1
                continue
            if FENCE_RE.match(line):
                if index > 0 and lines[index - 1].strip() != "":
                    lines.insert(index, "")
                    changed = True
                    index += 1
                if index + 1 < len(lines) and lines[index + 1].strip() != "":
                    lines.insert(index + 1, "")
                    changed = True
                index += 1
                continue
            if LIST_RE.match(line):
                if index > 0 and lines[index - 1].strip() != "" and not LIST_RE.match(lines[index - 1]):
                    lines.insert(index, "")
                    changed = True
                    index += 1
                list_end = index
                while list_end + 1 < len(lines) and LIST_RE.match(lines[list_end + 1]):
                    list_end += 1
                if list_end + 1 < len(lines) and lines[list_end + 1].strip() != "":
                    lines.insert(list_end + 1, "")
                    changed = True
                index = list_end + 1
                continue
            index += 1

            lines = normalize_blockquote_blanks(lines)

    final_lines: list[str] = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 1:
                final_lines.append("")
        else:
            blank_count = 0
            final_lines.append(line)

    return "\n".join(final_lines).rstrip("\n") + "\n"


def collect_markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def resolve_paths(root: Path, raw_paths: Iterable[str]) -> set[Path]:
    resolved: set[Path] = set()
    for value in raw_paths:
        path = Path(value)
        if not path.is_absolute():
            path = root / path
        resolved.add(path.resolve())
    return resolved


def run_fix(root: Path, files: list[Path], check: bool, mode: str) -> int:
    changed_files: list[Path] = []
    for file_path in files:
        original = file_path.read_text(encoding="utf-8", errors="replace")
        normalized = normalize_content(original, mode=mode)
        if normalized != original:
            changed_files.append(file_path)
            if not check:
                file_path.write_text(normalized, encoding="utf-8")

    if check:
        if changed_files:
            print("Arquivos que precisariam de ajuste:")
            for file_path in changed_files:
                print(f"- {file_path.relative_to(root)}")
            return 1
        print("Nenhum ajuste necessário.")
        return 0

    if changed_files:
        print("Arquivos atualizados:")
        for file_path in changed_files:
            print(f"- {file_path.relative_to(root)}")
    else:
        print("Nenhum arquivo precisou de alteração.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Padroniza arquivos Markdown do projeto.")
    parser.add_argument("--root", default=".", help="Diretório raiz do projeto (padrão: diretório atual).")
    parser.add_argument("--check", action="store_true", help="Somente verifica; não altera arquivos.")
    parser.add_argument("--all", action="store_true", help="Processa todos os arquivos .md encontrados no root.")
    parser.add_argument(
        "--files",
        nargs="*",
        default=[],
        help="Lista de arquivos .md específicos (caminho absoluto ou relativo ao root).",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Arquivos a excluir do processamento (caminho absoluto ou relativo ao root).",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--safe",
        action="store_true",
        help="Modo conservador: evita alterações estruturais mais agressivas.",
    )
    mode_group.add_argument(
        "--strict",
        action="store_true",
        help="Modo agressivo: aplica conversões estruturais adicionais.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Root inválido: {root}")
        return 2

    if args.all:
        files = collect_markdown_files(root)
    elif args.files:
        files = sorted(resolve_paths(root, args.files))
    else:
        default_targets = [
            root / "README.md",
            root / "docs/README_automatizar_issues.md",
            root / "docs/README_gerar_lista_itens_geral_projeto.md",
            root / "docs/README_gerar_lista_itens_sprint_review.md",
            root / "docs/README_gerar_relatorios_completos.md",
            root / "docs/README_jira_utils.md",
            root / "issues/QUICK_START.md",
            root / "issues/README_TEMPLATE.md",
            root / "tests/README_TESTS.md",
        ]
        files = [path.resolve() for path in default_targets if path.exists()]

    excluded = resolve_paths(root, args.exclude)
    files = [path for path in files if path not in excluded and path.exists() and path.suffix.lower() == ".md"]

    if not files:
        print("Nenhum arquivo Markdown selecionado.")
        return 0

    mode = "strict" if args.strict else "safe" if args.safe else "standard"
    print(f"Modo de normalização: {mode}")

    return run_fix(root, files, args.check, mode=mode)


if __name__ == "__main__":
    raise SystemExit(main())
