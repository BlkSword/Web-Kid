from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from .models import (
    AnalysisSummary,
    MagicMethodInfo,
    GadgetCandidates,
    Chains,
    PayloadSpec,
    PayloadResult,
    SimulationReport,
    EnvHints,
    ConstraintIssue,
    ConstraintReport,
    KBMatches,
    SinkSpec,
    SourceSpec,
    ClassInfo,
)
from .analyzer import analyze_php_repo, find_classes_ast, find_classes, PHPFile
from .gadgets import sniff_trampolines
from .solver import build_chain as build_chain_impl, build_trampoline_chain as build_trampoline_chain_impl
from .payload import php_serialize_object, generate_payload_script
from .simulator import simulate_unserialize as simulate_impl
from .knowledge_base import kb_search as kb_search_impl, kb_match_by_packages as kb_match_by_packages_impl


mcp = FastMCP("CTFPopChain")


@mcp.tool()
def analyze_php_repo_tool(rootPath: str, includes: List[str] | None = None) -> AnalysisSummary:
    inc = includes or []
    return analyze_php_repo(rootPath, inc)


@mcp.tool()
def list_magic_methods_tool(summary: AnalysisSummary) -> List[MagicMethodInfo]:
    items: List[MagicMethodInfo] = []
    for c in summary.classes:
        items.extend(c.methods)
    return items


@mcp.tool()
def find_gadgets_tool(summary: AnalysisSummary, targetSink: str) -> GadgetCandidates:
    items = []
    for c in summary.classes:
        for m in c.methods:
            if targetSink in m.calls:
                score = 1.0
                items.append(
                    {
                        "name": f"{c.name}:{m.name}",
                        "class_name": c.name,
                        "method": m.name,
                        "sink": targetSink,
                        "file": c.file,
                        "line": m.line,
                        "score": score,
                    }
                )
    return GadgetCandidates(items=items)


@mcp.tool()
def build_chain_tool(summary: AnalysisSummary, sources: SourceSpec, sink: SinkSpec) -> Chains:
    return build_chain_impl(summary.classes, sources, sink)


@mcp.tool()
def generate_payload_tool(className: str, properties: Dict[str, Any]) -> PayloadResult:
    s = php_serialize_object(className, properties)
    return PayloadResult(serialized=s, structure={"class": className, "properties": properties})


@mcp.tool()
def simulate_unserialize_tool(spec: PayloadSpec) -> SimulationReport:
    return simulate_impl(spec)


@mcp.tool()
def check_constraints_tool(env: EnvHints) -> ConstraintReport:
    issues: List[ConstraintIssue] = []
    if env.php_version and env.php_version.startswith("5."):
        issues.append(ConstraintIssue(name="old_php", severity="medium", detail="legacy"))
    if env.autoload is False:
        issues.append(ConstraintIssue(name="autoload_disabled", severity="high", detail="classes_may_not_load"))
    return ConstraintReport(issues=issues)


@mcp.tool()
def kb_search_tool(keyword: str, version: str | None = None) -> KBMatches:
    return kb_search_impl(keyword, version)


@mcp.prompt(title="审计入口点")
def prompt_entry(name: str) -> str:
    return name


@mcp.prompt(title="链拼接助手")
def prompt_chain(name: str) -> str:
    return name


def run():
    mcp.run()


def run_http():
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    run()
@mcp.tool()
def kb_match_by_packages_tool(summary: AnalysisSummary) -> KBMatches:
    return kb_match_by_packages_impl(summary)
@mcp.tool()
def parse_code_structure_tool(code: str) -> List[ClassInfo]:
    f = PHPFile(path="snippet.php", text=code)
    cs = find_classes_ast(f)
    if not cs:
        cs = find_classes(f)
    return cs
@mcp.tool()
def sniff_trampolines_tool(summary: AnalysisSummary) -> GadgetCandidates:
    return sniff_trampolines(summary.classes)
@mcp.tool()
def generate_payload_script_tool(className: str, properties: Dict[str, Any]) -> str:
    return generate_payload_script(className, properties)
@mcp.tool()
def build_trampoline_chain_tool(summary: AnalysisSummary) -> Chains:
    return build_trampoline_chain_impl(summary.classes)
