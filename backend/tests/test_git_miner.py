from unittest.mock import MagicMock

from agents.git_miner import GitMiner


def _miner_with_mock_repo():
    miner = GitMiner.__new__(GitMiner)  # skip __init__: avoids a real GitHub connection
    miner.repo = MagicMock()
    miner._code_files_cache = None
    return miner


def _make_commit(message, author="alice"):
    commit = MagicMock()
    commit.commit.message = message
    commit.commit.author.name = author
    commit.commit.author.date = None
    commit.html_url = "https://example.com/commit"
    return commit


def test_mine_commits_matches_case_insensitively():
    miner = _miner_with_mock_repo()
    miner.repo.get_commits.return_value = [
        _make_commit("Fix ORDER_DETAILS refresh timeout"),
        _make_commit("Unrelated change to another table"),
    ]
    results = miner._mine_commits("order_details")
    assert len(results) == 1
    assert results[0].type == "commit_message"


def test_mine_commits_requires_literal_substring():
    # "orders" is conceptually related but is not a literal substring of
    # "order_details" — the miner has no semantic understanding, only
    # string matching, and tests should reflect that honestly.
    miner = _miner_with_mock_repo()
    miner.repo.get_commits.return_value = [_make_commit("Fix broken join in the orders table")]
    results = miner._mine_commits("order_details")
    assert results == []


def test_mine_code_comments_extracts_matching_line_comment():
    miner = _miner_with_mock_repo()
    miner._code_files_cache = [
        ("models/orders.sql", "-- order_details dataset\nSELECT * FROM orders"),
        ("models/unrelated.sql", "-- nothing relevant here\nSELECT 1"),
    ]
    results = miner._mine_code_comments("order_details")
    assert len(results) == 1
    assert results[0].type == "code_comment"
    assert "order_details dataset" in results[0].raw_excerpt
