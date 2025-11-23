import os
import re
from typing import List
from .php_ast import analyze as ast_analyze
from .models import AnalysisSummary, ClassInfo, MagicMethodInfo, SinkInfo, ComposerPackage
import json


MAGIC_METHODS = {"__wakeup", "__destruct", "__toString", "__call", "__invoke"}
SINKS = [
    "system",
    "exec",
    "passthru",
    "shell_exec",
    "popen",
    "proc_open",
    "pcntl_exec",
    "eval",
    "assert",
    "include",
    "include_once",
    "require",
    "require_once",
    "file_put_contents",
]


class PHPFile:
    def __init__(self, path: str, text: str):
        self.path = path
        self.text = text


def read_php_files(root: str, includes: List[str]) -> List[PHPFile]:
    files: List[PHPFile] = []
    for base, _, names in os.walk(root):
        for n in names:
            if not n.lower().endswith(".php"):
                continue
            p = os.path.join(base, n)
            if includes and not any(inc in p for inc in includes):
                continue
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    files.append(PHPFile(p, f.read()))
            except Exception:
                pass
    return files


def find_classes(file: PHPFile) -> List[ClassInfo]:
    classes: List[ClassInfo] = []
    class_pattern = re.compile(r"class\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)
    method_pattern = re.compile(r"function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)
    prop_pattern = re.compile(r"public\s+\$([A-Za-z_][A-Za-z0-9_]*)|protected\s+\$([A-Za-z_][A-Za-z0-9_]*)|private\s+\$([A-Za-z_][A-Za-z0-9_]*)")
    sink_patterns = [(s, re.compile(r"\b" + re.escape(s) + r"\s*\(", re.IGNORECASE)) for s in SINKS]
    for m in class_pattern.finditer(file.text):
        cname = m.group(1)
        methods: List[MagicMethodInfo] = []
        properties: List[str] = []
        for pm in prop_pattern.finditer(file.text):
            for g in pm.groups():
                if g:
                    properties.append(g)
        for mm in method_pattern.finditer(file.text):
            mname = mm.group(1)
            if mname in MAGIC_METHODS:
                line = file.text.count("\n", 0, mm.start()) + 1
                sinks: List[SinkInfo] = []
                calls: List[str] = []
                for sname, sp in sink_patterns:
                    for sm in sp.finditer(file.text):
                        sline = file.text.count("\n", 0, sm.start()) + 1
                        sinks.append(SinkInfo(name=sname, file=file.path, line=sline))
                        calls.append(sname)
                methods.append(
                    MagicMethodInfo(
                        name=mname,
                        file=file.path,
                        line=line,
                        sinks=sinks,
                        calls=list(sorted(set(calls))),
                    )
                )
        classes.append(ClassInfo(name=cname, file=file.path, methods=methods, properties=properties))
    return classes


def find_classes_ast(file: PHPFile) -> List[ClassInfo]:
    res = ast_analyze(file.text)
    if res is None:
        return []
    out: List[ClassInfo] = []
    for c in res:
        methods: List[MagicMethodInfo] = []
        for m in c["methods"]:
            mname = m["name"]
            if mname in MAGIC_METHODS:
                calls = [x for x in m.get("calls", []) if x.lower() in {s.lower() for s in SINKS}]
                sinks = [SinkInfo(name=x, file=file.path, line=m["line"]) for x in calls]
                methods.append(MagicMethodInfo(name=mname, file=file.path, line=m["line"], sinks=sinks, calls=list(sorted(set(calls))), uses_properties=m.get("uses", [])))
        out.append(ClassInfo(name=c["name"], file=file.path, methods=methods, properties=c.get("properties", [])))
    return out


def analyze_php_repo(root: str, includes: List[str]) -> AnalysisSummary:
    files = read_php_files(root, includes)
    classes: List[ClassInfo] = []
    sinks: List[SinkInfo] = []
    packages: List[ComposerPackage] = []
    for f in files:
        cs = find_classes_ast(f)
        if not cs:
            cs = find_classes(f)
        classes.extend(cs)
        for c in cs:
            for mm in c.methods:
                sinks.extend(mm.sinks)
    comp_path = os.path.join(root, "composer.json")
    if os.path.exists(comp_path):
        try:
            with open(comp_path, "r", encoding="utf-8", errors="ignore") as cf:
                data = json.load(cf)
                for sec in ("require", "require-dev"):
                    for name, ver in (data.get(sec) or {}).items():
                        packages.append(ComposerPackage(name=name, version=str(ver)))
        except Exception:
            pass
    installed_json = os.path.join(root, "vendor", "composer", "installed.json")
    if os.path.exists(installed_json):
        try:
            with open(installed_json, "r", encoding="utf-8", errors="ignore") as ij:
                data = json.load(ij)
                pkgs = data.get("packages") if isinstance(data, dict) else data
                if isinstance(pkgs, list):
                    for p in pkgs:
                        name = p.get("name")
                        ver = p.get("version") or p.get("pretty_version")
                        if name:
                            packages.append(ComposerPackage(name=name, version=ver))
        except Exception:
            pass
    return AnalysisSummary(classes=classes, sinks=sinks, files_scanned=len(files), packages=packages)
