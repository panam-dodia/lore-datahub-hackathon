"""In-memory cache of GitHub evidence, keyed by the bare search term (leaf
asset name, same derivation orchestrator.py uses). Populated once by
prefetch_all_evidence() so that viewing an asset's detail is instant instead
of triggering a live GitHub search per click — the tradeoff for hackathon
scale is the same one job_store.py makes: no persistence, resets on restart.
"""

import asyncio

from agents.datahub_miner import DataHubMiner
from agents.git_miner import GitMiner
from datahub.metadata.urns import DatasetUrn

evidence_cache: dict[str, list] = {}
prefetch_started = False


def search_term_for(asset_name: str) -> str:
    return asset_name.rsplit(".", 1)[-1]


async def prefetch_all_evidence():
    """Mine GitHub once per unique asset leaf-name across the whole
    instance, concurrently, and cache the results. Safe to call more than
    once — only runs the actual work the first time.
    """
    global prefetch_started
    if prefetch_started:
        return
    prefetch_started = True

    datahub_miner = DataHubMiner()
    git_miner = GitMiner()

    urns = datahub_miner.client.get_all_datasets()
    search_terms = {search_term_for(DatasetUrn.from_string(urn).name) for urn in urns}

    async def fetch(term: str):
        evidence_cache[term] = await git_miner.mine(term)

    await asyncio.gather(*[fetch(term) for term in search_terms])
