import os
from mcp_popchain.analyzer import analyze_php_repo
from mcp_popchain.models import SinkSpec, SourceSpec
from mcp_popchain.solver import build_chain
from mcp_popchain.payload import php_serialize_object


def test_analyze():
    root = os.path.join(os.path.dirname(__file__), "..", "fixtures", "php")
    summary = analyze_php_repo(root, [])
    assert summary.files_scanned >= 1
    assert any(c.name == "A" for c in summary.classes)
    assert any(s.name == "system" for s in summary.sinks)


def test_chain():
    root = os.path.join(os.path.dirname(__file__), "..", "fixtures", "php")
    summary = analyze_php_repo(root, [])
    chains = build_chain(summary.classes, SourceSpec(entry="unserialize", controllable_properties={}), SinkSpec(name="system"))
    assert len(chains.items) >= 1


def test_payload():
    s = php_serialize_object("A", {"x": "id"})
    assert s.startswith("O:")
