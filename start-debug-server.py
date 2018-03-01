import os
from werkzeug.serving import run_simple

from brochure_wsgi.brochure_wsgi_application import get_brochure_wsgi_application


def main():
    application = get_brochure_wsgi_application()
    os.environ["BROCHURE_COVER_SECTION"] = '{"title": "Cover Section", "body": "Body text"}'
    os.environ["BROCHURE_ENTERPRISE"] = '{"name": "Example Enterprise"}'
    os.environ["BROCHURE_CONTACT_METHOD"] = '{"contact_method_type": "email", "value": "ejemplo@example.com"}'

    run_simple(hostname="localhost",
               port=8000,
               application=application,
               use_debugger=True,
               use_reloader=True)


if __name__ == "__main__":
    main()
