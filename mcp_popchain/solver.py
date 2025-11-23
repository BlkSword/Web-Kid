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
