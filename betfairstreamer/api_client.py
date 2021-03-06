from __future__ import annotations

import functools
import json
import logging
import time
from datetime import datetime
from itertools import chain
from typing import Any, Dict, List, Literal, Optional, Union

import attr
import requests

from betfairstreamer.models.betfair_api import (
    BetfairCancelOrder,
    BetfairPlaceOrder,
    CurrentOrderSummaryReport,
)

logger = logging.getLogger("betfair_api_client")


def session_header(f):
    @functools.wraps(f)
    def session_wrapper(self: BetfairHTTPClient, *args, **kwargs):
        session_token = self.get_session_token()

        h = {
            "X-Application": self.app_key,
            "X-Authentication": session_token,
            "content-type": "application/json",
            "Accept-Encoding": "gzip, deflate",
        }

        return f(self, *args, **kwargs, header=h)

    return session_wrapper


Records = Union[CurrentOrderSummaryReport]


def create_generator_for_records(lister, betfair_filter: dict, start_index: int, page_size: int):
    current_record_index = start_index
    more_available = True

    while more_available:
        betfair_filter.update({"fromRecord": current_record_index, "recordCount": page_size})

        current_record_index = current_record_index + page_size
        response = lister(betfair_filter)

        more_available = response["moreAvailable"]

        yield response


Locale = Literal["AU", "SE", "RO", "ES", "IT", "DEFAULT", ""]


@attr.s(auto_attribs=True, slots=True)
class BetfairHTTPClient:
    username: str
    password: str
    app_key: str
    cert_crt_path: str
    cert_key_path: str
    session_token: str = None
    locale: Locale = ""
    session: requests.Session = attr.Factory(requests.Session)
    session_fetched_date: datetime = attr.Factory(lambda: datetime(year=1970, month=1, day=1))

    keep_alive_endpoints = {
        "AU": "https://identitysso.betfair.au/api/keepAlive",
        "SE": "https://identitysso.betfair.se/api/keepAlive",
        "RO": "https://identitysso.betfair.ro/api/keepAlive",
        "ES": "https://identitysso.betfair.es/api/keepAlive",
        "IT": "https://identitysso.betfair.it/api/keepAlive",
        "DEFAULT": "https://identitysso.betfair.com/api/keepAlive",
    }

    cert_endpoints = {
        "AU": "https://identitysso-cert.betfair.au/api/certlogin",
        "SE": "https://identitysso-cert.betfair.se/api/certlogin",
        "RO": "https://identitysso-cert.betfair.ro/api/certlogin",
        "ES": "https://identitysso-cert.betfair.es/api/certlogin",
        "IT": "https://identitysso-cert.betfair.it/api/certlogin",
        "DEFAULT": "https://identitysso-cert.betfair.com/api/certlogin",
    }

    def login(self) -> Optional[str]:

        endpoint = self.cert_endpoints.get(self.locale, self.cert_endpoints["DEFAULT"])

        payload = {"username": self.username, "password": self.password}

        headers = {
            "X-Application": self.app_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        resp = self.session.post(
            endpoint, data=payload, cert=(self.cert_crt_path, self.cert_key_path), headers=headers,
        )

        if resp.status_code == 200:
            res = resp.json()

            if res["loginStatus"] != "SUCCESS":
                raise ConnectionError("Could not login to betfair due to, " + res["loginStatus"])

            self.session_token = res["sessionToken"]
            self.session_fetched_date = datetime.now()
            logger.info("Logged in successfully!")

            return self.session_token

        raise ConnectionError(
            "Could not connect to betfair servers, status code: " + str(resp.status_code)
        )

    def send_keep_alive(self):
        endpoint = self.keep_alive_endpoints[self.locale]

        header = {
            "X-Application": self.app_key,
            "X-Authentication": self.get_session_token(),
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
        }

        res = self.session.post(
            endpoint, cert=(self.cert_crt_path, self.cert_key_path), headers=header
        )

        if res.status_code == 200:
            res = res.json()

            if res["status"] == "FAIL":
                raise ConnectionError(res["error"])

            self.set_session_token(res["token"])

            logger.info("Keep alive sent successfully!")

        else:
            raise ConnectionError(res.status_code)

    @session_header
    def send(self, operation: str, payload: Dict[str, Any], header: dict):
        response = requests.post(operation, data=json.dumps(payload), headers=header)
        return response.json()

    def valid_session_token(self) -> bool:
        return (datetime.now() - self.session_fetched_date).total_seconds() < 3600 * 7 + 1800

    def get_session_token(self) -> Optional[str]:
        if self.valid_session_token():
            if (datetime.now() - self.session_fetched_date).total_seconds() > 3 * 3600:
                self.send_keep_alive()

            return self.session_token

        return self.login()

    def set_session_token(self, session_token):
        self.session_fetched_date = datetime.now()
        self.session_token = session_token


@attr.s(auto_attribs=True, slots=True)
class BetfairNGClient:
    betfair_http_client: BetfairHTTPClient

    endpoints = {
        "BETTING": "https://api.betfair.com/exchange/betting/rest/v1.0/",
        "ACCOUNT": "https://api.betfair.com/exchange/account/rest/v1.0/",
    }

    def list_event_types(self, params):
        operation = self.endpoints["BETTING"] + "listEventTypes/"
        return self.betfair_http_client.send(operation, params)

    def list_competitions(self, params):
        operation = self.endpoints["BETTING"] + "listCompetitions/"
        return self.betfair_http_client.send(operation, params)

    def list_time_ranges(self, params):
        operation = self.endpoints["BETTING"] + "listTimeRanges/"
        return self.betfair_http_client.send(operation, params)

    def list_events(self, params):
        operation = self.endpoints["BETTING"] + "listEvents/"
        return self.betfair_http_client.send(operation, params)

    def list_market_types(self, params):
        operation = self.endpoints["BETTING"] + "listMarketTypes/"
        return self.betfair_http_client.send(operation, params)

    def list_countries(self, params):
        operation = self.endpoints["BETTING"] + "listCountries/"
        return self.betfair_http_client.send(operation, params)

    def list_venues(self, params):
        operation = self.endpoints["BETTING"] + "listVenues/"
        return self.betfair_http_client.send(operation, params)

    def list_market_catalogue(self, params):
        operation = self.endpoints["BETTING"] + "listMarketCatalogue/"
        return self.betfair_http_client.send(operation, params)

    def list_market_book(self, params):
        operation = self.endpoints["BETTING"] + "listMarketBook>/"
        return self.betfair_http_client.send(operation, params)

    def list_runner_book(self, params):
        operation = self.endpoints["BETTING"] + "listRunnerBook/"
        return self.betfair_http_client.send(operation, params)

    def list_market_profit_and_loss(self, params):
        operation = self.endpoints["BETTING"] + "listMarketProfitAndLoss/"
        return self.betfair_http_client.send(operation, params)

    def list_current_orders(self, params):
        operation = self.endpoints["BETTING"] + "listCurrentOrders/"
        return self.betfair_http_client.send(operation, params)

    def list_cleared_orders(self, params):
        operation = self.endpoints["BETTING"] + "listClearedOrders/"
        return self.betfair_http_client.send(operation, params)

    def create_developer_app_keys(self, params):
        operation = self.endpoints["ACCOUNT"] + "createDeveloperAppKeys/"
        return self.betfair_http_client.send(operation, params)

    def get_developer_app_keys(self, params):
        operation = self.endpoints["ACCOUNT"] + "getDeveloperAppKeys/"
        return self.betfair_http_client.send(operation, params)

    def get_account_funds(self, params):
        operation = self.endpoints["ACCOUNT"] + "getAccountFunds/"
        return self.betfair_http_client.send(operation, params)

    def transfer_funds(self, params):
        operation = self.endpoints["ACCOUNT"] + "transferFunds/"
        return self.betfair_http_client.send(operation, params)

    def get_account_details(self, params):
        operation = self.endpoints["ACCOUNT"] + "getAccountDetails/"
        return self.betfair_http_client.send(operation, params)

    def get_account_statement(self, params):
        operation = self.endpoints["ACCOUNT"] + "getAccountStatement/"
        return self.betfair_http_client.send(operation, params)

    def list_currency_rates(self, params) -> List:
        operation = self.endpoints["ACCOUNT"] + "listCurrencyRates/"
        return self.betfair_http_client.send(operation, params)

    def get_session_token(self):
        return self.betfair_http_client.get_session_token()


@attr.s(auto_attribs=True, slots=True)
class BetfairAPIClient:
    api_ng: BetfairNGClient

    def get_session_token(self) -> str:
        return self.api_ng.get_session_token()

    def get_current_orders_generator(
        self, start_index=0, page_size=3, params: Optional[dict] = None
    ):
        if params is None:
            params = {}

        if not 0 < page_size <= 1000:
            raise ValueError("maximum page size = 100")

        for order_summary in create_generator_for_records(
            self.api_ng.list_current_orders, params, start_index=start_index, page_size=page_size,
        ):
            yield order_summary["currentOrders"]

    def get_account_statement_generator(
        self, start_index=0, page_size=3, params: Optional[dict] = None,
    ):

        if not 0 < page_size <= 100:
            raise ValueError("min page size 1, max page size = 100")

        if params is None:
            params = {}

        for account_statements in create_generator_for_records(
            self.api_ng.get_account_statement, params, start_index=start_index, page_size=page_size,
        ):
            yield [
                json.loads(statement["itemClassData"]["unknownStatementItem"])
                for statement in account_statements["accountStatement"]
            ]

    def get_cleared_orders_generator(
        self, start_index=0, page_size=3, params: Optional[dict] = None,
    ):

        if not 0 < page_size <= 1000:
            raise ValueError("min page size 1, max page size = 100")

        if params is None:
            params = {"betStatus": "SETTLED"}

        for cleared_orders in create_generator_for_records(
            self.api_ng.list_cleared_orders, params, start_index=start_index, page_size=page_size,
        ):
            yield cleared_orders

    def get_current_orders(self, start_index=0, page_size=1000, params: Optional[dict] = None):

        if params is None:
            params = {}

        orders = []

        for order_summary in self.get_current_orders_generator(start_index, page_size, params):
            for order in order_summary:
                ps = order["priceSize"]
                order.pop("priceSize")

                orders.append({**order, **ps})

        return orders

    def get_cleared_orders(self, start_index=0, page_size=1000, params: Optional[dict] = None):

        if params is None:
            params = {"betStatus": "SETTLED"}

        orders = []

        for cleared_orders in self.get_cleared_orders_generator(start_index, page_size, params):
            for order in cleared_orders["clearedOrders"]:
                orders.append(order)

        return orders

    def get_account_statements(
        self,
        start_index=0,
        page_size=100,
        params: Optional[dict] = None,
        delay_between_page_fetch=0.5,
    ):
        if params is None:
            params = {}

        statements = []

        for account_statements in self.get_account_statement_generator(
            start_index=start_index, page_size=page_size, params=params,
        ):
            statements = chain(statements, account_statements)
            time.sleep(delay_between_page_fetch)

        return list(statements)

    def get_currency_rate(self, currency_code: str):
        currencies = list(
            filter(
                lambda c: c["currencyCode"] == currency_code, self.api_ng.list_currency_rates({})
            )
        )

        if currencies:
            return currencies[0]["rate"]

        return []

    @classmethod
    def from_requests_backend(
        cls,
        username: str,
        password: str,
        app_key: str,
        cert_crt_path: str,
        cert_key_path: str,
        locale: Locale = "",
    ) -> BetfairAPIClient:

        http_client = BetfairHTTPClient(
            username=username,
            password=password,
            app_key=app_key,
            cert_crt_path=cert_crt_path,
            cert_key_path=cert_key_path,
            locale=locale,
        )

        api_ng = BetfairNGClient(http_client)
        return cls(api_ng)


@attr.s(auto_attribs=True, slots=True)
class TradeClient:
    http_client: BetfairHTTPClient

    operations = {
        "PLACE": "https://api.betfair.com/exchange/betting/rest/v1.0/placeOrders/",
        "CANCEL": "https://api.betfair.com/exchange/betting/rest/v1.0/cancelOrders/",
    }

    def execute(self, order: Union[BetfairCancelOrder, BetfairPlaceOrder]):
        if order is None:
            return

        if order["instructions"] and "orderType" in order["instructions"][0]:
            return self.http_client.send(self.operations["PLACE"], order)

        return self.http_client.send(self.operations["CANCEL"], order)

    @classmethod
    def from_requests_backend(
        cls,
        username: str,
        password: str,
        app_key: str,
        cert_crt_path: str,
        cert_key_path: str,
        locale: Locale = "",
    ) -> TradeClient:

        http_client = BetfairHTTPClient(
            username=username,
            password=password,
            app_key=app_key,
            cert_crt_path=cert_crt_path,
            cert_key_path=cert_key_path,
            locale=locale,
        )

        return cls(http_client)
