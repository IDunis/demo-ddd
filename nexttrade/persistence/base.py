
from sqlalchemy.orm import DeclarativeBase, Session, scoped_session


SessionType = scoped_session[Session]

# Assuming that you have a function to initialize the session
def init_session() -> SessionType:
    # Initialize and return your scoped session
    return scoped_session(Session)

class ModelBase(DeclarativeBase):
    pass
