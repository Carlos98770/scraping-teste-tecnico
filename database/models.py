from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from database.database import Base


class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True)

    part_number = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(String)

    brand_name = Column(String)

    category = Column(String)

    type = Column(String)

    product_url = Column(String)

    photo_url = Column(String)

    warranty = Column(String)

    material = Column(String)

    price = Column(Float)

    gross_weight = Column(Float)

    width = Column(Float)

    length = Column(Float)

    stock_quantity = Column(Integer)

    applications = Column(Text)