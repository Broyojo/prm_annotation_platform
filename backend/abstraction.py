from datetime import datetime
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, or_, select


class ModelBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)  # unique for each row
    record_id: Optional[int] = Field(default=None)  # same for all versions
    valid_from: datetime = Field(default_factory=datetime.now, index=True)
    valid_to: Optional[datetime] = Field(default=None, index=True)


class CRUD[T: ModelBase]:
    def __init__(self, model: type[T], session: Session):
        self.model = model
        self.session = session

    def create(self, data: T) -> T:
        db_item = self.model.model_validate(data)
        db_item.valid_from = datetime.now()
        db_item.record_id = -1
        self.session.add(db_item)
        self.session.flush()
        assert db_item.id is not None
        db_item.record_id = db_item.id  # First version's id becomes the record_id
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def read(self, record_id: int, timestamp: Optional[datetime] = None) -> Optional[T]:
        if timestamp is None:
            timestamp = datetime.now()

        query = select(self.model).where(
            self.model.record_id == record_id,
            self.model.valid_from <= timestamp,
            or_(self.model.valid_to == None, timestamp < self.model.valid_to),
        )

        result = self.session.exec(query).first()
        print("read:", result)
        return result

    def read_all(self, timestamp: Optional[datetime] = None) -> list[T]:
        if timestamp is None:
            timestamp = datetime.now()

        query = select(self.model).where(
            self.model.valid_from <= timestamp,
            self.model.valid_to is None or timestamp < self.model.valid_to,
        )

        result = list(self.session.exec(query).all())
        print("read all:", result)
        return result

    def update(self, record_id: int, data: T) -> Optional[T]:
        current = self.read(record_id)
        if current is None:
            return None

        now = datetime.now()

        current.valid_to = now
        self.session.add(current)

        new_data = data.model_dump(exclude_unset=True)
        new_version = self.model.model_validate(current)
        for key, value in new_data.items():
            setattr(new_version, key, value)

        new_version.id = None
        new_version.record_id = record_id
        new_version.valid_from = now
        new_version.valid_to = None

        self.session.add(new_version)
        self.session.commit()
        self.session.refresh(new_version)

        return new_version

    def delete(self, record_id: int) -> Optional[T]:
        db_item = self.read(record_id)
        if db_item is None:
            return None

        db_item.valid_to = datetime.now()
        self.session.add(db_item)
        self.session.commit()
        return db_item


class User(ModelBase, table=True):
    name: str
    permissions: str = "standard"


engine = create_engine("sqlite:///test.db")
SQLModel.metadata.create_all(engine)
import time

with Session(engine) as session:
    user = User(name="David")
    crud = CRUD(User, session)
    user = crud.create(user)

    print(list(session.exec(select(User)).all()))

    assert user.record_id is not None
    time.sleep(1)
    user.permissions = "admin"
    user = crud.update(user.record_id, user)
    print(user)
