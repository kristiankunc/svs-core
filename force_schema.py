from svs_core.db.models import Base
from svs_core.db.client import engine


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
