from typing import List
from .models import KBItem, KBMatches, AnalysisSummary


KB: List[KBItem] = [
    KBItem(framework="Laravel", version=None, name="MonologHandler", sink="system"),
    KBItem(framework="Symfony", version=None, name="YamlParse", sink="eval"),
    KBItem(framework="ThinkPHP", version=None, name="LogGadget", sink="file_put_contents"),
]

PKG_MAP = {
    "laravel/framework": "Laravel",
    "symfony/yaml": "Symfony",
    "topthink/framework": "ThinkPHP",
}


def kb_search(keyword: str, version: str | None) -> KBMatches:
    items = []
    for it in KB:
        if keyword.lower() in it.framework.lower() or keyword.lower() in it.name.lower():
            if version is None or it.version == version:
                items.append(it)
    return KBMatches(items=items)


def kb_match_by_packages(summary: AnalysisSummary) -> KBMatches:
    items = []
    seen = set()
    for p in summary.packages:
        fw = PKG_MAP.get(p.name)
        if not fw:
            continue
        for it in KB:
            if it.framework == fw:
                key = (it.framework, it.name, it.version)
                if key in seen:
                    continue
                if it.version is None or p.version == it.version:
                    items.append(it)
                    seen.add(key)
    return KBMatches(items=items)
