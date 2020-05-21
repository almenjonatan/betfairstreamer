from __future__ import annotations

import functools
import json
import time
from datetime import datetime
from itertools import chain
from typing import Any, Dict, Union, Optional

import attr
import requests

from betfairstreamer.models.betfair_api import BetfairCancelOrder, BetfairPlaceOrder, CurrentOrderSummaryReport


def session_header(f):
    @functools.wraps(f)
    def session_wrapper(self: BetfairHTTPClient, *args, **kwargs):
        session_token = self.get_session_token()

        h = {"X-Application": self.app_key, "X-Authentication": session_token, "content-type": "application/json"}

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


@attr.s(auto_attribs=True, slots=True)
class BetfairHTTPClient:
    username: str
    password: str
    app_key: str
    cert_crt_path: str
    cert_key_path: str
    session_token: str = None
    locale: str = ""
    session: requests.Session = attr.Factory(requests.Session)
    session_fetched_date: datetime = attr.Factory(lambda: datetime(year=1970, month=1, day=1))

    cert_endpoints = {
        "SE": "https://identitysso-cert.betfair.se/api/certlogin",
        "RO": "https://identitysso-cert.betfair.ro/api/certlogin",
        "ES": "https://identitysso-cert.betfair.es/api/certlogin",
        "IT": "https://identitysso-cert.betfair.it/api/certlogin",
        "DEFAULT": "https://identitysso-cert.betfair.com/api/certlogin",
    }

    def login(self) -> Optional[str]:

        endpoint = self.cert_endpoints.get(self.locale, "DEFAULT")

        payload = {"username": self.username, "password": self.password}

        headers = {"X-Application": self.app_key, "Content-Type": "application/x-www-form-urlencoded"}

        resp = self.session.post(endpoint, data=payload, cert=(self.cert_crt_path, self.cert_key_path), headers=headers)

        if resp.status_code == 200:
            res = resp.json()

            if res["loginStatus"] == "SUCCESS":
                self.session_token = res["sessionToken"]
                self.session_fetched_date = datetime.now()

                return self.session_token

    @session_header
    def send(self, operation: str, payload: Dict[str, Any], header: str) -> None:
        response = requests.post(operation, data=json.dumps(payload), headers=header)
        return response.json()

    def valid_session_token(self) -> bool:
        return (datetime.now() - self.session_fetched_date).total_seconds() < 3600 * 7 + 1800

    def get_session_token(self) -> Optional[str]:
        if self.valid_session_token():
            return self.session_token

        return self.login()


@attr.s(auto_attribs=True, slots=True)
class BetfairNGClient:
    betfair_http_client: BetfairHTTPClient

    endpoints = {
        "BETTING": "https://api.betfair.com/exchange/betting/rest/v1.0/",
        "ACCOUNT": "https://api.betfair.com/exchange/account/rest/v1.0/",
    }

    def list_current_orders(self, order_filter):
        operation = self.endpoints["BETTING"] + "listCurrentOrders/"
        return self.betfair_http_client.send(operation, order_filter)

    def get_account_statement(self, account_statement_filter):
        operation = self.endpoints["ACCOUNT"] + "getAccountStatement/"
        return self.betfair_http_client.send(operation, account_statement_filter)

    def get_session_token(self):
        return self.betfair_http_client.get_session_token()


@attr.s(auto_attribs=True, slots=True)
class BetfairAPIClient:
    api_ng: BetfairNGClient

    def get_session_token(self) -> str:
        return self.api_ng.get_session_token()

    def get_current_orders_generator(self, start_index=0, page_size=3, order_filter: Optional[dict] = None):
        if order_filter is None:
            order_filter = {}

        if not 0 < page_size <= 1000:
            raise ValueError("maximum page size = 100")

        for order_summary in create_generator_for_records(
                self.api_ng.list_current_orders, order_filter, start_index=start_index, page_size=page_size
        ):
            yield order_summary["currentOrders"]

    def get_account_statement_generator(self, start_index=0, page_size=3,
                                        account_statement_filter: Optional[dict] = None):

        if not 0 < page_size <= 100:
            raise ValueError("min page size 1, max page size = 100")

        if account_statement_filter is None:
            account_statement_filter = {}

        for account_statements in create_generator_for_records(
                self.api_ng.get_account_statement, account_statement_filter, start_index=start_index,
                page_size=page_size
        ):
            yield [
                json.loads(statement["itemClassData"]["unknownStatementItem"])
                for statement in account_statements["accountStatement"]
            ]

    def get_current_orders(self, start_index=0, page_size=1000, order_filter: Optional[dict] = None):

        if order_filter is None:
            order_filter = {}

        orders = []

        for order_summary in self.get_current_orders_generator(start_index, page_size, order_filter):
            for order in order_summary:
                ps = order["priceSize"]
                order.pop("priceSize")

                orders.append({**order, **ps})

        return orders

    def get_account_statements(self, start_index=0, page_size=100, account_statement_filter: Optional[dict] = None):
        if account_statement_filter is None:
            account_statement_filter = {}

        statements = []

        for account_statements in self.get_account_statement_generator(
                start_index=start_index, page_size=page_size, account_statement_filter=account_statement_filter
        ):
            statements = chain(statements, account_statements)
            time.sleep(1)

        return list(statements)

    @classmethod
    def from_requests_backend(
            cls, username: str, password: str, app_key: str, cert_crt_path: str, cert_key_path: str, locale: str
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
class RequestTradeClient:
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
            cls, username: str, password: str, app_key: str, cert_crt_path: str, cert_key_path: str, locale: str
    ) -> RequestTradeClient:

        http_client = BetfairHTTPClient(
            username=username,
            password=password,
            app_key=app_key,
            cert_crt_path=cert_crt_path,
            cert_key_path=cert_key_path,
            locale=locale,
        )

        return cls(http_client)
