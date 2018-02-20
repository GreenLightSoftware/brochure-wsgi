import os
from unittest import TestCase

from brochure.value_fetchers.enterprise_fetcher_interface import EnterpriseFetcherInterface
from brochure_contract_tests.enterprise_fetcher_contract import EnterpriseFetcherContract

from brochure_wsgi.value_fetchers.environment_enterprise_fetcher import environment_enterprise_fetcher


class TestEnvironmentEnterpriseFetcher(TestCase, EnterpriseFetcherContract):
    def get_subject(self, name: str) -> EnterpriseFetcherInterface:
        brochure_enterprise = '{"name": "%s"}' % name
        os.environ["BROCHURE_ENTERPRISE"] = brochure_enterprise
        return environment_enterprise_fetcher

    def get_testcase(self) -> TestCase:
        return self
