import pytest

from betfairstreamer.resources.market_cache import MarketCache


def test_market_definition_missing():
    market_cache = MarketCache()

    market_update = {"op": "mcm", "pt": 10, "mc": [{"id": "1.2"}]}

    with pytest.raises(ValueError):
        market_cache(market_update)


def test_market_definition_present():
    market_update = {
        "op": "mcm",
        "pt": 10,
        "mc": [
            {
                "id": "1.2",
                "marketDefinition": {
                    "bettingType": "ODDS",
                    "numberOfActiveRunners": 2,
                    "runners": [{"id": 1, "sortPriority": 1}],
                },
            }
        ],
    }

    market_cache = MarketCache()
    market_books = market_cache(market_update)

    assert len(market_books) == 1
    assert market_books[0].market_definition.runners[0].sort_priority == 1
    assert market_books[0].market_definition.runners[0].id == 1


def test_insert_prices():
    market_update = {
        "op": "mcm",
        "pt": 10,
        "mc": [
            {
                "id": "1.2",
                "marketDefinition": {
                    "bettingType": "ODDS",
                    "numberOfActiveRunners": 2,
                    "runners": [{"id": 1, "sortPriority": 1}],
                },
                "rc": [{"id": 1, "bdatb": [[0, 1.2, 24]]}],
            }
        ],
    }

    market_cache = MarketCache()
    market_updates = market_cache.update(market_update)

    assert market_updates[0].runner_book.price_sizes[0, 0, 0, 0] == 1.2
    assert market_updates[0].runner_book.price_sizes[0, 0, 0, 1] == 24
