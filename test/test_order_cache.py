from betfairstreamer.resources.order_cache import OrderCache, Side, Order


def test_insert_order():
    order_update = {
        "op": "ocm",
        "clk": "AIsMAIEOAIsPAM0PAPkL",
        "pt": 1583502407146,
        "oc": [
            {
                "id": "1.169205465",
                "orc": [
                    {
                        "id": 1221385,
                        "uo": [
                            {
                                "id": "197304122303",
                                "p": 10,
                                "s": 30,
                                "side": "B",
                                "status": "E",
                                "pt": "L",
                                "ot": "L",
                                "pd": 1583502407000,
                                "sm": 0,
                                "sr": 30,
                                "sl": 0,
                                "sc": 0,
                                "sv": 0,
                                "rac": "",
                                "rc": "REG_SWE",
                                "rfo": "",
                                "rfs": "",
                            }
                        ],
                    }
                ],
            }
        ],
    }

    order_update2 = {
        "op": "ocm",
        "clk": "AIsMAIEOAIsPAM0PAPkL",
        "pt": 1583502407146,
        "oc": [
            {
                "id": "1.169205465",
                "orc": [
                    {
                        "id": 1221385,
                        "uo": [
                            {
                                "id": "197304122303",
                                "p": 10,
                                "s": 30,
                                "side": "B",
                                "status": "E",
                                "pt": "L",
                                "ot": "L",
                                "pd": 1583502407000,
                                "sm": 10,
                                "sr": 20,
                                "sl": 0,
                                "sc": 0,
                                "sv": 0,
                                "rac": "",
                                "rc": "REG_SWE",
                                "rfo": "",
                                "rfs": "",
                            }
                        ],
                    }
                ],
            }
        ],
    }

    order_update3 = {
        "op": "ocm",
        "clk": "AIsMAIEOAIsPAM0PAPkL",
        "pt": 1583502407146,
        "oc": [
            {
                "id": "1.169205465",
                "orc": [
                    {
                        "id": 1221385,
                        "uo": [
                            {
                                "id": "197304122303",
                                "p": 10,
                                "s": 30,
                                "side": "B",
                                "status": "E",
                                "pt": "L",
                                "ot": "L",
                                "pd": 1583502407000,
                                "sm": 10,
                                "sr": 0,
                                "sl": 0,
                                "sc": 20,
                                "sv": 0,
                                "rac": "",
                                "rc": "REG_SWE",
                                "rfo": "",
                                "rfs": "",
                            }
                        ],
                    }
                ],
            }
        ],
    }

    order_cache = OrderCache()
    order_cache(order_update)
    assert order_cache.get_size_remaining("1.169205465", 1221385, Side.BACK) == 30
    assert order_cache.get_size_matched("1.169205465", 1221385, Side.BACK) == 0

    order_cache(order_update2)
    assert order_cache.get_size_remaining("1.169205465", 1221385, Side.BACK) == 20
    assert order_cache.get_size_matched("1.169205465", 1221385, Side.BACK) == 10

    order_cache(order_update3)

    assert order_cache.get_size_cancelled("1.169205465", 1221385, Side.BACK) == 20
    assert order_cache.get_size_matched("1.169205465", 1221385, Side.BACK) == 10


def test_list_current_orders_insert():

    order_cache = OrderCache()

    initial_image = {
        "currentOrders": [
            {
                "betId": "197304122303",
                "marketId": "1.169205465",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 10.0, "size": 30.0},
                "bspLiability": 0.0,
                "side": "BACK",
                "status": "EXECUTABLE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-06T13:46:47.000Z",
                "averagePriceMatched": 0.0,
                "sizeMatched": 0.0,
                "sizeRemaining": 30.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0.0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
            }
        ],
        "moreAvailable": False,
    }

    order_update3 = {
        "op": "ocm",
        "clk": "AIsMAIEOAIsPAM0PAPkL",
        "pt": 1583502407146,
        "oc": [
            {
                "id": "1.169205465",
                "orc": [
                    {
                        "id": 1221385,
                        "uo": [
                            {
                                "id": "197304122303",
                                "p": 10,
                                "s": 30,
                                "side": "B",
                                "status": "E",
                                "pt": "L",
                                "ot": "L",
                                "pd": 1583502407000,
                                "sm": 10,
                                "sr": 0,
                                "sl": 0,
                                "sc": 20,
                                "sv": 0,
                                "rac": "",
                                "rc": "REG_SWE",
                                "rfo": "",
                                "rfs": "",
                            }
                        ],
                    }
                ],
            }
        ],
    }

    for o in initial_image["currentOrders"]:
        order_cache.update_order(Order.from_betfair_rest_api(o))

    assert order_cache.get_size_remaining("1.169205465", 1221385, Side.BACK) == 30
    assert order_cache.get_size_matched("1.169205465", 1221385, Side.BACK) == 0

    order_cache(order_update3)

    assert order_cache.get_size_cancelled("1.169205465", 1221385, Side.BACK) == 20
    assert order_cache.get_size_matched("1.169205465", 1221385, Side.BACK) == 10
