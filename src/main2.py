from fastapi import FastAPI

from src import presentation
from src.infrastructure.application import configure_logger
from src.infrastructure.application import create as application_factory
from src.infrastructure.application import settings

# Adjust the logging
# -------------------------------
configure_logger()


# Adjust the application
# -------------------------------
app: FastAPI = application_factory(
    debug=settings.debug,
    rest_routers=(
        presentation.authentication.rest.router,
        presentation.products.rest.router,
        presentation.orders.rest.router,
        presentation.users.rest.router,
    ),
    startup_tasks=[],
    shutdown_tasks=[],
    startup_processes=[],
)
