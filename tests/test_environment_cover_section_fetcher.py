import os
from unittest import TestCase

from brochure.value_fetchers.cover_section_fetcher_interface import CoverSectionFetcherInterface
from brochure_contract_tests.cover_section_fetcher_contract import CoverSectionFetcherContract

from brochure_wsgi.value_fetchers.environment_cover_section_fetcher import environment_cover_section_fetcher


class TestEnvironmentCoverSectionFetcher(TestCase, CoverSectionFetcherContract):
    def get_subject(self, title: str, body: str) -> CoverSectionFetcherInterface:
        brochure_cover_section = '{"title": "%s", "body": "%s"}' % (title, body)
        os.environ["BROCHURE_COVER_SECTION"] = brochure_cover_section

        return environment_cover_section_fetcher

    def get_testcase(self) -> TestCase:
        return self
