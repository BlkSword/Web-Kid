from typing import List
from .models import GadgetCandidates, GadgetCandidate, ClassInfo


STRING_FUNCS = {"preg_match", "preg_replace", "printf", "sprintf"}


def sniff_trampolines(classes: List[ClassInfo]) -> GadgetCandidates:
    items: List[GadgetCandidate] = []
    for c in classes:
        props_set = set(c.properties or [])
        for m in c.methods:
            # __toString trampoline via string context functions
            if any(fn in STRING_FUNCS for fn in m.calls):
                items.append(
                    GadgetCandidate(
                        name=f"{c.name}:{m.name}:toString",
                        class_name=c.name,
                        method=m.name,
                        sink="__toString",
                        file=c.file,
                        line=m.line,
                        score=0.6,
                    )
                )
            # __invoke trampoline via callable property invocation
            if getattr(m, "invokes_properties", []):
                items.append(
                    GadgetCandidate(
                        name=f"{c.name}:{m.name}:invoke",
                        class_name=c.name,
                        method=m.name,
                        sink="__invoke",
                        file=c.file,
                        line=m.line,
                        score=0.7,
                    )
                )
            # __get heuristic: accessing undefined property names
            undefined_props = [p for p in m.uses_properties if p not in props_set]
            if undefined_props:
                items.append(
                    GadgetCandidate(
                        name=f"{c.name}:{m.name}:get",
                        class_name=c.name,
                        method=m.name,
                        sink="__get",
                        file=c.file,
                        line=m.line,
                        score=0.5,
                    )
                )
    items.sort(key=lambda x: x.score, reverse=True)
    return GadgetCandidates(items=items)

