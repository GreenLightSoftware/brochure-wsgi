from brochure.values.enterprise import Enterprise

from brochure_wsgi.deserializers.json_deserializer import JSONDeserializer
from brochure_wsgi.value_fetchers.environment_variable_fetcher import EnvironmentVariableFetcher

enterprise_json_deserializer = JSONDeserializer(deserializer=lambda eo: Enterprise(**eo))
environment_enterprise_fetcher = EnvironmentVariableFetcher(key="BROCHURE_ENTERPRISE",
                                                            deserializer=enterprise_json_deserializer)
