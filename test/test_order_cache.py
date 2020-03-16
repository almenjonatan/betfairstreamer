import orjson
from betfairlightweight.resources import CurrentOrders
from hypothesis import note, settings

from betfairstreamer.betfair.enums import Side
from betfairstreamer.cache.order_cache import OrderCache


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

    co = {
        "currentOrders": [
            {
                "betId": "197366684443",
                "marketId": "1.169206844",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 6.0, "size": 50.0},
                "bspLiability": 0.0,
                "side": "BACK",
                "status": "EXECUTION_COMPLETE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-06T21:26:17.000Z",
                "matchedDate": "2020-03-06T22:48:30.000Z",
                "averagePriceMatched": 6.0,
                "sizeMatched": 42.95,
                "sizeRemaining": 0.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 7.05,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "5",
            },
            {
                "betId": "197372201089",
                "marketId": "1.169206168",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 7.0, "size": 50.0},
                "bspLiability": 0.0,
                "side": "BACK",
                "status": "EXECUTION_COMPLETE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-06T23:11:11.000Z",
                "matchedDate": "2020-03-06T23:17:01.000Z",
                "averagePriceMatched": 7.0,
                "sizeMatched": 50.0,
                "sizeRemaining": 0.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0.0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "7",
            },
            {
                "betId": "197373092455",
                "marketId": "1.169206844",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 5.6, "size": 43.0},
                "bspLiability": 0.0,
                "side": "LAY",
                "status": "EXECUTION_COMPLETE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-06T23:31:16.000Z",
                "matchedDate": "2020-03-07T08:34:48.000Z",
                "averagePriceMatched": 5.6,
                "sizeMatched": 43.0,
                "sizeRemaining": 0.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0.0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "3",
            },
            {
                "betId": "197373111010",
                "marketId": "1.169206168",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 6.6, "size": 50.0},
                "bspLiability": 0.0,
                "side": "LAY",
                "status": "EXECUTABLE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-06T23:31:40.000Z",
                "averagePriceMatched": 0.0,
                "sizeMatched": 0.0,
                "sizeRemaining": 50.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0.0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "10",
            },
            {
                "betId": "197399900519",
                "marketId": "1.169205465",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 3.95, "size": 100.0},
                "bspLiability": 0.0,
                "side": "BACK",
                "status": "EXECUTABLE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-07T07:53:15.000Z",
                "averagePriceMatched": 0.0,
                "sizeMatched": 0.0,
                "sizeRemaining": 100.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0.0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "2",
            },
            {
                "betId": "197399900922",
                "marketId": "1.169206015",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 3.2, "size": 100.0},
                "bspLiability": 0.0,
                "side": "BACK",
                "status": "EXECUTION_COMPLETE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-07T07:53:15.000Z",
                "matchedDate": "2020-03-07T08:44:34.000Z",
                "averagePriceMatched": 3.2,
                "sizeMatched": 100.0,
                "sizeRemaining": 0.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0.0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "3",
            },
            {
                "betId": "197399901349",
                "marketId": "1.169205312",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 4.5, "size": 50.0},
                "bspLiability": 0.0,
                "side": "BACK",
                "status": "EXECUTABLE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-07T07:53:16.000Z",
                "averagePriceMatched": 0.0,
                "sizeMatched": 0.0,
                "sizeRemaining": 50.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0.0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "4",
            },
            {
                "betId": "197400246227",
                "marketId": "1.169206538",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 3.9, "size": 100.0},
                "bspLiability": 0.0,
                "side": "BACK",
                "status": "EXECUTABLE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-07T08:00:52.000Z",
                "averagePriceMatched": 0.0,
                "sizeMatched": 0.0,
                "sizeRemaining": 100.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0.0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "2",
            },
            {
                "betId": "197406456374",
                "marketId": "1.169206015",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 3.05, "size": 100.0},
                "bspLiability": 0.0,
                "side": "LAY",
                "status": "EXECUTABLE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-07T09:25:39.000Z",
                "averagePriceMatched": 0.0,
                "sizeMatched": 0.0,
                "sizeRemaining": 100.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0.0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "2",
            },
            {
                "betId": "197406457133",
                "marketId": "1.169206844",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 6.0, "size": 50.0},
                "bspLiability": 0.0,
                "side": "BACK",
                "status": "EXECUTABLE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-07T09:25:39.000Z",
                "averagePriceMatched": 0.0,
                "sizeMatched": 0.0,
                "sizeRemaining": 50.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0.0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "3",
            },
        ],
        "moreAvailable": False,
    }

    current_orders = CurrentOrders(**co)

    su = [
        b'{"op":"ocm","initialClk":"DeSC9JgCDuv5s5QCDsjci5YCDdndt5kCDbbTqZcC","clk":"AAAAAAAAAAAAAA==",'
        b'"conflateMs":0,"heartbeatMs":5000,"pt":1583578555932,"ct":"SUB_IMAGE","oc":[{"id":"1.169206538",'
        b'"orc":[{"fullImage":true,"id":1221385,"uo":[{"id":"197400246227","p":3.9,"s":100,"side":"B","status":"E",'
        b'"pt":"L","ot":"L","pd":1583568052000,"sm":0,"sr":100,"sl":0,"sc":0,"sv":0,"rac":"","rc":"REG_SWE",'
        b'"rfo":"2","rfs":""}]}]},{"id":"1.169205465","orc":[{"fullImage":true,"id":1221385,'
        b'"uo":[{"id":"197399900519","p":3.95,"s":100,"side":"B","status":"E","pt":"L","ot":"L","pd":1583567595000,'
        b'"sm":0,"sr":100,"sl":0,"sc":0,"sv":0,"rac":"","rc":"REG_SWE","rfo":"2","rfs":""}]}]},{"id":"1.169205312",'
        b'"orc":[{"fullImage":true,"id":1221385,"uo":[{"id":"197399901349","p":4.5,"s":50,"side":"B","status":"E",'
        b'"pt":"L","ot":"L","pd":1583567596000,"sm":0,"sr":50,"sl":0,"sc":0,"sv":0,"rac":"","rc":"REG_SWE","rfo":"4",'
        b'"rfs":""}]}]},{"id":"1.169206168","orc":[{"fullImage":true,"id":1221385,"uo":[{"id":"197373111010","p":6.6,'
        b'"s":50,"side":"L","status":"E","pt":"L","ot":"L","pd":1583537500000,"sm":0,"sr":50,"sl":0,"sc":0,"sv":0,'
        b'"rac":"","rc":"REG_SWE","rfo":"10","rfs":""}],"mb":[[7,50]]}]},{"id":"1.169206844",'
        b'"orc":[{"fullImage":true,"id":1221385,"uo":[{"id":"197406457133","p":6,"s":50,"side":"B","status":"E",'
        b'"pt":"L","ot":"L","pd":1583573139000,"sm":0,"sr":50,"sl":0,"sc":0,"sv":0,"rac":"","rc":"REG_SWE","rfo":"3",'
        b'"rfs":""}],"mb":[[6,42.95]],"ml":[[5.6,43]]}]},{"id":"1.169206015","orc":[{"fullImage":true,"id":1221385,'
        b'"uo":[{"id":"197406456374","p":3.05,"s":100,"side":"L","status":"E","pt":"L","ot":"L","pd":1583573139000,'
        b'"sm":0,"sr":100,"sl":0,"sc":0,"sv":0,"rac":"","rc":"REG_SWE","rfo":"2","rfs":""}],"mb":[[3.2,100]]}]}]} '
    ]

    order_cache = OrderCache.from_betfair(current_orders)

    updates = order_cache.update(orjson.loads(su[0]))

    for o in updates:
        assert (
                order_cache.get_size_remaining(o.market_id, o.selection_id, o.side) == o.size_remaining
        )


def test_order_on_selection():
    co = {
        "currentOrders": [
            {
                "betId": "197366684443",
                "marketId": "1.169206844",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 6.0, "size": 50.0},
                "bspLiability": 0.0,
                "side": "BACK",
                "status": "EXECUTABLE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-06T21:26:17.000Z",
                "matchedDate": "2020-03-06T22:48:30.000Z",
                "averagePriceMatched": 0.0,
                "sizeMatched": 0.0,
                "sizeRemaining": 50.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "5",
            },
            {
                "betId": "197372201089",
                "marketId": "1.169206844",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 7.0, "size": 60.0},
                "bspLiability": 0.0,
                "side": "BACK",
                "status": "EXECUTABLE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-06T23:11:11.000Z",
                "matchedDate": "2020-03-06T23:17:01.000Z",
                "averagePriceMatched": 0.0,
                "sizeMatched": 0.0,
                "sizeRemaining": 60.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0.0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "7",
            },
        ],
        "moreAvailable": False,
    }

    order_cache = OrderCache.from_betfair(CurrentOrders(**co))

    assert (
            len(
                order_cache.get_orders_on_selection(
                    market_id="1.169206844", selection_id=1221385, side=Side.BACK
                )
            )
            == 2
    )


def test_out_of_band_order():
    co = {
        "currentOrders": [
            {
                "betId": "197366684443",
                "marketId": "1.169206844",
                "selectionId": 1221385,
                "handicap": 0.0,
                "priceSize": {"price": 6.0, "size": 50.0},
                "bspLiability": 0.0,
                "side": "BACK",
                "status": "EXECUTABLE",
                "persistenceType": "LAPSE",
                "orderType": "LIMIT",
                "placedDate": "2020-03-06T21:26:17.000Z",
                "matchedDate": "2020-03-06T22:48:30.000Z",
                "averagePriceMatched": 0.0,
                "sizeMatched": 10.0,
                "sizeRemaining": 40.0,
                "sizeLapsed": 0.0,
                "sizeCancelled": 0,
                "sizeVoided": 0.0,
                "regulatorCode": "SWEDISH GAMBLING AUTHORITY",
                "customerOrderRef": "5",
            }],
        "moreAvailable": False,
    }

    order_cache = OrderCache.from_betfair(CurrentOrders(**co))

    o = {
        "op": "ocm",
        "initialClk": "asdfasdfas",
        "clk": "asdfwefa",
        "conflateMs": 0,
        "heartbeatMs": 5000,
        "pt": 10,
        "ct": "SUB_IMAGE",
        "oc": [{
            "id": "1.169206844",
            "orc": [
                {"fullImage": True,
                 "id": 1221385,
                 "uo": [
                     {"id": "197366684443",
                      "p": 6.0,
                      "s": 50,
                      "side": "B",
                      "status": "E",
                      "pt": "L",
                      "ot": "L",
                      "pd": 1583568052000,
                      "sm": 5,
                      "sr": 45,
                      "sl": 0,
                      "sc": 0,
                      "sv": 0,
                      "rac": "",
                      "rc": "REG_SWE",
                      "rfo": "2",
                      "rfs": ""}
                 ]}
            ]
        }], "mb": [[]]
    }

    order_cache(o)

    assert order_cache.orders["197366684443"].size_remaining == 40
