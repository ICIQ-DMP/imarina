import sys
import os

from filesystem import read_file_content, read_env_var


def read_secret(secret_name):
    """Retrieve a token from predefined sources in order of priority."""
    sources = [
        lambda: read_file_content(f"/run/secrets/{secret_name}"),
        lambda: read_file_content(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "secrets",
                secret_name
            ).__str__()
        ),
        lambda: read_env_var(secret_name),
    ]

    for source in sources:
        try:
            return source()
        except Exception as e:
            continue

    print(f"Could not read {secret_name} from any source")
    sys.exit(1)
