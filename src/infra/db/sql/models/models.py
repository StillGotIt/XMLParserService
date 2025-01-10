from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.infra.db.sql.models.base import BaseSQLModel

Base = declarative_base()


class Contractor(BaseSQLModel):
    __tablename__ = 'contractors'  # noqa
    full_name = Column(Text, nullable=False)
    short_name = Column(Text)
    inn = Column(String(12), unique=True, nullable=False)
    kpp = Column(String(9))
    ogrn = Column(String(15), unique=True, nullable=False)  # noqa
    addresses = relationship("Address", back_populates="contractor")
    activities = relationship("Activity", back_populates="contractor")


class Address(BaseSQLModel):
    __tablename__ = 'addresses'  # noqa
    contractor_id = Column(Integer, ForeignKey('contractors.id'), nullable=False)
    region = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    street = Column(Text)
    house = Column(Text)
    postal_code = Column(String(6))
    contractor = relationship("Contractor", back_populates="addresses")


class Activity(BaseSQLModel):
    __tablename__ = 'activities'  # noqa
    contractor_id = Column(Integer, ForeignKey('contractors.id'), nullable=False)
    code = Column(String(10), nullable=False)
    name = Column(Text, nullable=False)
    is_main = Column(Boolean, default=False, nullable=False)
    contractor = relationship("Contractor", back_populates="activities")
