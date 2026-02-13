#import sys
import os

from imarina.core.filesystem import read_file_content, read_env_var
from imarina.core.log_utils import get_logger
from typing import Callable, List

logger = get_logger(__name__)


def read_secret(secret_name : str) -> str:
    """Retrieve a token from predefined sources in order of priority."""
    sources: List[Callable[[], str]] = [
        lambda: read_file_content(f"/run/secrets/{secret_name}"),
        lambda: read_file_content(
            os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    )
                ),
                "secrets",
                secret_name,
            )
        ),
        lambda: read_env_var(secret_name),
    ]

    for source in sources:
        try:
            value = source()
            if value:
                return value
        except Exception:
            continue
    raise RuntimeError(f"Could not read {secret_name} from any source")

    # print(f"Could not read {secret_name} from any source")
    # sys.exit(1)
