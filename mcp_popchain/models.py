from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class SinkInfo(BaseModel):
    name: str
    file: str
    line: int


class MagicMethodInfo(BaseModel):
    name: str
    file: str
    line: int
    sinks: List[SinkInfo]
    calls: List[str]
    uses_properties: List[str] = []


class ClassInfo(BaseModel):
    name: str
    file: str
    methods: List[MagicMethodInfo]
    properties: List[str]


class ComposerPackage(BaseModel):
    name: str
    version: Optional[str] = None


class AnalysisSummary(BaseModel):
    classes: List[ClassInfo]
    sinks: List[SinkInfo]
    files_scanned: int
    packages: List[ComposerPackage] = []


class ConstraintInput(BaseModel):
    php_version: Optional[str] = None
    autoload: Optional[bool] = None
    allow_url_include: Optional[bool] = None
    extensions: Optional[List[str]] = None


class GadgetCandidate(BaseModel):
    name: str
    class_name: str
    method: str
    sink: str
    file: str
    line: int
    score: float


class GadgetCandidates(BaseModel):
    items: List[GadgetCandidate]


class SourceSpec(BaseModel):
    entry: str
    controllable_properties: Dict[str, Any]


class SinkSpec(BaseModel):
    name: str


class ChainStep(BaseModel):
    class_name: str
    method: str
    note: Optional[str] = None


class ChainCandidate(BaseModel):
    id: str
    steps: List[ChainStep]
    sink: str
    score: float


class Chains(BaseModel):
    items: List[ChainCandidate]


class PayloadSpec(BaseModel):
    class_name: str
    properties: Dict[str, Any]


class PayloadResult(BaseModel):
    serialized: str
    structure: Dict[str, Any]


class SimulationEvent(BaseModel):
    step: str
    detail: str


class SimulationReport(BaseModel):
    events: List[SimulationEvent]
    reached_sink: bool


class EnvHints(BaseModel):
    php_version: Optional[str] = None
    autoload: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class ConstraintIssue(BaseModel):
    name: str
    severity: str
    detail: str


class ConstraintReport(BaseModel):
    issues: List[ConstraintIssue]


class KBItem(BaseModel):
    framework: str
    version: Optional[str] = None
    name: str
    sink: str
    note: Optional[str] = None


class KBMatches(BaseModel):
    items: List[KBItem]
