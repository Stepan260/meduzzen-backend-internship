from app.repository.base_repository import BaseRepository
from app.model.company import Company


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, session):
        super().__init__(session=session, model=Company)
