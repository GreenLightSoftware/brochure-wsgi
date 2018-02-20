from typing import Optional

from brochure.values.contact_method import ContactMethod, ContactMethodType

from brochure_wsgi.deserializers.json_deserializer import JSONDeserializer
from brochure_wsgi.value_fetchers.environment_variable_fetcher import EnvironmentVariableFetcher


def contact_method_deserializer(contact_method) -> Optional[ContactMethod]:
    return ContactMethod(contact_method_type=ContactMethodType.EMAIL,
                         value=contact_method["value"]) if contact_method["contact_method_type"] == "email" else None


contact_method_json_deserializer = JSONDeserializer(deserializer=contact_method_deserializer)
environment_contact_method_fetcher = EnvironmentVariableFetcher(key="BROCHURE_CONTACT_METHOD",
                                                                deserializer=contact_method_json_deserializer)
