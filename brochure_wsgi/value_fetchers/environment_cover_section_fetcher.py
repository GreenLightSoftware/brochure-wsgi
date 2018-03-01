from brochure.values.section import Section

from brochure_wsgi.deserializers.json_deserializer import JSONDeserializer
from brochure_wsgi.value_fetchers.environment_variable_fetcher import EnvironmentVariableFetcher

section_json_deserializer = JSONDeserializer(deserializer=lambda section: Section(**section))
environment_cover_section_fetcher = EnvironmentVariableFetcher(key="BROCHURE_COVER_SECTION",
                                                               deserializer=section_json_deserializer)
