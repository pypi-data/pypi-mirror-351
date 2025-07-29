import pathlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mktestdocs import check_md_file

from any_agent.evaluation import TraceEvaluationResult


# Note the use of `str`, makes for pretty output
@pytest.mark.parametrize("fpath", pathlib.Path("docs").glob("**/*.md"), ids=str)
def test_files_all(fpath: pathlib.Path) -> None:
    mock_agent = MagicMock()
    mock_create = MagicMock(return_value=mock_agent)
    mock_eval = MagicMock()
    mock_eval.return_value = MagicMock(spec=TraceEvaluationResult)

    mock_create_async = AsyncMock()
    with (
        patch("builtins.open", new_callable=MagicMock),
        patch("any_agent.AnyAgent.create", mock_create),
        patch("any_agent.evaluation.evaluate", mock_eval),
        patch("any_agent.AnyAgent.create_async", mock_create_async),
    ):
        check_md_file(fpath=fpath, memory=True)
