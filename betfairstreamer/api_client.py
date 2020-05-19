import json
import time
from itertools import chain
from typing import List

import attr
import requests

from betfairstreamer.models.betfair_api import CurrentOrderSummary


@attr.s(auto_attribs=True, slots=True)
class BetfairRequester:
    username: str
    password: str
    app_key: str
    cert_crt_path: str
    cert_key_path: str
    session_token: str = None
    locale: str = None

    cert_endpoints = {
        "SE": "https://identitysso-cert.betfair.se/api/certlogin",
        "RO": "https://identitysso-cert.betfair.ro/api/certlogin",
        "ES": "https://identitysso-cert.betfair.es/api/certlogin",
        "IT": "https://identitysso-cert.betfair.it/api/certlogin",
        "DEFAULT": "https://identitysso-cert.betfair.com/api/certlogin"
    }

    endpoints = {
        "BETTING": "https://api.betfair.com/exchange/betting/rest/v1.0/",
        "ACCOUNT": "https://api.betfair.com/exchange/account/rest/v1.0/"
    }

    def login(self):

        if self.locale is None:
            endpoint = self.cert_endpoints["DEFAULT"]
        else:
            endpoint = self.cert_endpoints[self.locale]

        payload = {
            "username": self.username,
            "password": self.password
        }

        headers = {'X-Application': self.app_key, 'Content-Type': 'application/x-www-form-urlencoded'}

        resp = requests.post(endpoint, data=payload, cert=(self.cert_crt_path, self.cert_key_path), headers=headers)

        if resp.status_code == 200:
            res = resp.json()

            if res["loginStatus"] == "SUCCESS":
                self.session_token = res["sessionToken"]

        return self.session_token

    def list_current_orders(self, order_filter):
        header = {'X-Application': self.app_key, 'X-Authentication': self.session_token,
                  'content-type': 'application/json'}
        endpoint = self.endpoints["BETTING"] + "listCurrentOrders/"

        response = requests.post(endpoint, data=json.dumps(order_filter), headers=header)
        response = response.json()

        return response

    def get_account_statement(self, account_statement_filter):
        header = {'X-Application': self.app_key, 'X-Authentication': self.session_token,
                  'content-type': 'application/json'}
        endpoint = self.endpoints["ACCOUNT"] + "getAccountStatement/"

        response = requests.post(endpoint, data=json.dumps(account_statement_filter), headers=header)
        response = response.json()

        return response


def create_generator_for_records(lister, betfair_filter, start_index=0, page_size=3):
    current_record_index = start_index
    more_available = True

    while more_available:
        betfair_filter.update({
            "fromRecord": current_record_index,
            "recordCount": page_size
        })

        current_record_index = current_record_index + page_size
        response = lister(betfair_filter)
        more_available = response["moreAvailable"]

        yield response


@attr.s(auto_attribs=True, slots=True)
class BetfairAPIClient:
    requester: BetfairRequester

    def get_session_token(self) -> str:
        return self.requester.login()

    def get_current_orders_generator(self, start_index=0, page_size=3, order_filter=None):
        if order_filter is None:
            order_filter = {}

        if not 0 < page_size <= 1000:
            raise ValueError("maximum page size = 100")

        for order_summary in create_generator_for_records(
                self.requester.list_current_orders,
                order_filter,
                start_index=start_index,
                page_size=page_size):

            yield order_summary["currentOrders"]

    def get_account_statement_generator(self, start_index=0, page_size=3, account_statement_filter=None):

        if not 0 < page_size <= 100:
            raise ValueError("min page size 1, max page size = 100")

        if account_statement_filter is None:
            account_statement_filter = {}

        for account_statement in create_generator_for_records(
                self.requester.get_account_statement,
                account_statement_filter, start_index=start_index,
                page_size=page_size):

            yield account_statement["accountStatement"]

    def get_current_orders(self, start_index=0, page_size=1000, order_filter=None) -> List[CurrentOrderSummary]:

        if order_filter is None:
            order_filter = {}

        return [order
                for order_summary in self.get_current_orders_generator(start_index, page_size, order_filter)
                for order in order_summary]

    def get_account_statements(self, start_index=0, page_size=100, account_statement_filter=None):
        if account_statement_filter is None:
            account_statement_filter = {}

        statements = []

        for account_statements in self.get_account_statement_generator(
                start_index=start_index,
                page_size=page_size,
                account_statement_filter=account_statement_filter
        ):
            statements = chain(statements, [statement["itemClassData"]["unknownStatementItem"] for statement in account_statements])
            time.sleep(1)

        return list(map(json.loads, statements))

    @classmethod
    def from_requests_backend(
            cls,
            username: str,
            password: str,
            app_key: str,
            cert_crt_path: str,
            cert_key_path: str,
            locale: str
    ):
        return cls(
            BetfairRequester(
                username=username,
                password=password,
                app_key=app_key,
                cert_crt_path=cert_crt_path,
                cert_key_path=cert_key_path,
                locale=locale
            ))
