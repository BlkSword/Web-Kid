from typing import List
from .models import Chains, ChainCandidate, ChainStep, SinkSpec, SourceSpec, ClassInfo


def build_chain(classes: List[ClassInfo], sources: SourceSpec, sink: SinkSpec) -> Chains:
    items: List[ChainCandidate] = []
    for c in classes:
        for m in c.methods:
            if sink.name in m.calls:
                base_score = 1.0
                if m.name == "__wakeup":
                    base_score += 0.5
                if m.name == "__destruct":
                    base_score += 0.2
                if c.properties:
                    base_score += 0.1
                steps = [ChainStep(class_name=c.name, method=m.name)]
                items.append(
                    ChainCandidate(
                        id=f"{c.name}:{m.name}:{sink.name}",
                        steps=steps,
                        sink=sink.name,
                        score=base_score,
                    )
                )
    items.sort(key=lambda x: x.score, reverse=True)
    return Chains(items=items)


def build_trampoline_chain(classes: List[ClassInfo]) -> Chains:
    items: List[ChainCandidate] = []
    str_funcs = {"preg_match", "preg_replace", "printf", "sprintf"}
    for c in classes:
        steps: List[ChainStep] = []
        score = 0.0
        by_name = {m.name: m for m in c.methods}
        wakeup = by_name.get("__wakeup")
        tostr = by_name.get("__toString")
        getm = by_name.get("__get")
        invoke = by_name.get("__invoke")
        if wakeup and any(fn in str_funcs for fn in wakeup.calls):
            steps.append(ChainStep(class_name=c.name, method="__wakeup", note="string_context"))
            score += 0.3
        if tostr:
            undefined = [p for p in tostr.uses_properties if p not in set(c.properties or [])]
            if undefined:
                steps.append(ChainStep(class_name=c.name, method="__toString", note="access_undefined_property"))
                score += 0.3
        if getm and getattr(getm, "invokes_properties", []):
            steps.append(ChainStep(class_name=c.name, method="__get", note="returns_callable_property"))
            score += 0.2
        if invoke:
            steps.append(ChainStep(class_name=c.name, method="__invoke"))
            score += 0.2
        if steps:
            items.append(
                ChainCandidate(
                    id=f"{c.name}:trampoline",
                    steps=steps,
                    sink="__invoke",
                    score=score,
                )
            )
    items.sort(key=lambda x: x.score, reverse=True)
    return Chains(items=items)
