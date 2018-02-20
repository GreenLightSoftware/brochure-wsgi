from unittest import TestCase

import os
from brochure.value_fetchers.contact_method_fetcher_interface import ContactMethodFetcherInterface
from brochure.values.contact_method import ContactMethodType
from brochure_contract_tests.contact_method_fetcher_contract import ContactMethodFetcherContract

from brochure_wsgi.value_fetchers.environment_contact_method_fetcher import environment_contact_method_fetcher


class TestReferenceContactMethodFetcher(TestCase, ContactMethodFetcherContract):

    def get_subject(self, contact_method_type: ContactMethodType, value: str) -> ContactMethodFetcherInterface:
        contact_method_type = "email" if contact_method_type == ContactMethodType.EMAIL else ""
        brochure_enterprise = '{"contact_method_type": "%s", "value": "%s"}' % (contact_method_type, value)
        os.environ["BROCHURE_CONTACT_METHOD"] = brochure_enterprise
        return environment_contact_method_fetcher

    def get_testcase(self) -> TestCase:
        return self
