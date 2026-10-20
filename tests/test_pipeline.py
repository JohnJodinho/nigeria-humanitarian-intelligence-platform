import inspect

from src.pipeline.orchestrator import PipelineOrchestrator
from src.transformation.transformer import DataTransformer


def test_orchestrator_uses_existing_humanitarian_needs_transformer():
    source = inspect.getsource(PipelineOrchestrator.run_all)

    assert callable(DataTransformer.transform_humanitarian_needs)
    assert "DataTransformer.transform_humanitarian_needs" in source
    assert "DataTransformer.transform_needs" not in source
