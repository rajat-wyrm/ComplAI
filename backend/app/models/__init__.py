# register all models here so Base.metadata knows about them
from app.models.database import Base
from app.models.user import User
from app.models.token import RefreshToken
from app.models.database import Document
