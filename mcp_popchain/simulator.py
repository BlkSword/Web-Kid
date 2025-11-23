from .models import PayloadSpec, SimulationEvent, SimulationReport


def simulate_unserialize(spec: PayloadSpec) -> SimulationReport:
    events = []
    events.append(SimulationEvent(step="unserialize", detail=spec.class_name))
    events.append(SimulationEvent(step="__wakeup", detail=spec.class_name))
    events.append(SimulationEvent(step="__destruct", detail=spec.class_name))
    return SimulationReport(events=events, reached_sink=False)
