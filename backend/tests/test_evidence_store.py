from api.evidence_store import search_term_for


def test_strips_only_last_segment():
    assert search_term_for("b2fd91.schema.TABLE_NAME") == "TABLE_NAME"


def test_single_segment_returned_as_is():
    assert search_term_for("just_a_name") == "just_a_name"
