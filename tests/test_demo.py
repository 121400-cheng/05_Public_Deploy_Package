from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from utils import data
from utils.viz import raw_graph, core_order


@pytest.mark.parametrize("key,counts,rate", [
    ("Q1", (100, 88, 12, 0), 2.7812686413386047),
    ("Q2", (100, 97, 3, 0), 9.481003959522099),
])
def test_verified_statistics_unchanged(key, counts, rate):
    stat = data.summary(key)
    assert (stat["n"], stat["improved"], stat["tied"], stat["regressed"]) == counts
    assert stat["mean_pct"] == pytest.approx(rate, abs=1e-10)


def test_pair_data_and_public_projection():
    for key in data.SCENES:
        item = data.demo_case(key)
        assert raw_graph(item["raw"]).data
        assert core_order(item["baseline"], "优化前").data
        assert core_order(item["final"], "优化后").data
        table = data.public_table(key)
        assert table["实例"].iloc[0] == "实例 001"
        assert "source_path" not in table.columns
        assert not re.search(r"Q[12]|case_|赛题|Eval[12]", table.to_string())
    assert len(data.manifest()["files"]) == 9


def test_original_tree_unavailable(monkeypatch):
    """Deny reads outside the deployment root, without changing the original tree."""
    root = data.DEMO.resolve()
    original_text, original_bytes = Path.read_text, Path.read_bytes
    original_csv = data.pd.read_csv

    def allowed(path):
        assert Path(path).resolve().is_relative_to(root), "External data dependency"

    def read_text(path, *args, **kwargs):
        allowed(path)
        return original_text(path, *args, **kwargs)

    def read_bytes(path, *args, **kwargs):
        allowed(path)
        return original_bytes(path, *args, **kwargs)

    def read_csv(path, *args, **kwargs):
        allowed(path)
        return original_csv(path, *args, **kwargs)

    data.manifest.cache_clear()
    data.case_table.cache_clear()
    data.read_json.cache_clear()
    monkeypatch.setattr(Path, "read_text", read_text)
    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    monkeypatch.setattr(data.pd, "read_csv", read_csv)
    for key in data.SCENES:
        assert len(data.case_table(key)) == 100
        assert data.demo_case(key)["raw"]["edges"]
