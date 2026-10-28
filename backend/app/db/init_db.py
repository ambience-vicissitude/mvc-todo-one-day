"""One-shot schema creation, run before the API starts (compose `db-init`, k8s Job).

TRIMMED: no migration tool. For schema evolution adopt Alembic and replace create_all here.
Running this separately (not inside every API replica) avoids startup races when scaling out.
"""

import logging
import time

from sqlalchemy.exc import OperationalError

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import get_engine
from app.models.base import Base

logger = logging.getLogger("app.db.init")

MAX_ATTEMPTS = 30
RETRY_DELAY_SECONDS = 2


def init_db() -> None:
    engine = get_engine()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            Base.metadata.create_all(engine)
            logger.info("database schema ready")
            return
        except OperationalError:
            logger.warning("database not ready (attempt %s/%s)", attempt, MAX_ATTEMPTS)
            time.sleep(RETRY_DELAY_SECONDS)
    raise RuntimeError("database never became ready")


if __name__ == "__main__":
    configure_logging(get_settings().log_level)
    init_db()
