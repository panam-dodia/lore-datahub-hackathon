from api.routes import _to_lineage_node


def test_dataset_urn_extracts_platform_and_name():
    urn = "urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)"
    node = _to_lineage_node(urn)
    assert node.platform == "snowflake"
    assert node.name == "db.schema.table"


def test_non_dataset_urn_falls_back_gracefully():
    # Regression: lineage edges can point at pipeline tasks, dashboards,
    # etc, not just other datasets — this used to raise InvalidUrnError
    # and 500 the whole endpoint.
    urn = "urn:li:dataJob:(urn:li:dataFlow:(airflow,my_dag,PROD),my_task)"
    node = _to_lineage_node(urn)
    assert node.platform == "dataJob"
    assert node.name == "my_task"
