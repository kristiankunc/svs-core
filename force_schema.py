from svs_core.db.client import engine
from svs_core.db.models import Base

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
