from unittest.mock import MagicMock

from agents.datahub_miner import DataHubMiner

SAMPLE_URN = "urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)"


def _miner_with_mock_client(downstream_count, has_doc, owners):
    client = MagicMock()
    client.get_asset_lineage.return_value = {
        "downstreamEntities": ["x"] * downstream_count,
        "upstreamEntities": [],
    }
    client.get_asset_documentation.return_value = "some docs" if has_doc else None
    client.get_asset_ownership.return_value = owners

    miner = DataHubMiner.__new__(DataHubMiner)  # skip __init__: avoids a real DataHub connection
    miner.client = client
    return miner


def test_undocumented_sole_owner_high_downstream_is_at_risk():
    miner = _miner_with_mock_client(downstream_count=8, has_doc=False, owners=["alice"])
    risk = miner.compute_risk_for_urn(SAMPLE_URN)

    assert risk.risk_level in ("AT_RISK", "CRITICAL")
    assert "No documentation on file" in risk.risk_reasons
    assert any("Single owner" in r for r in risk.risk_reasons)


def test_well_documented_shared_ownership_low_downstream_is_safe():
    miner = _miner_with_mock_client(downstream_count=1, has_doc=True, owners=["alice", "bob"])
    risk = miner.compute_risk_for_urn(SAMPLE_URN)

    assert risk.risk_level == "SAFE"
    assert risk.risk_reasons == []


def test_no_owner_is_flagged():
    miner = _miner_with_mock_client(downstream_count=0, has_doc=True, owners=[])
    risk = miner.compute_risk_for_urn(SAMPLE_URN)

    assert "No registered owner" in risk.risk_reasons


def test_platform_and_name_parsed_from_urn():
    miner = _miner_with_mock_client(downstream_count=0, has_doc=True, owners=["alice"])
    risk = miner.compute_risk_for_urn(SAMPLE_URN)

    assert risk.platform == "snowflake"
    assert risk.asset_name == "db.schema.table"
