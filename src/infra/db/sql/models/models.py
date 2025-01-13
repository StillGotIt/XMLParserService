from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.infra.db.sql.models.base import BaseSQLModel, Base


class Contractor(BaseSQLModel):
    __tablename__ = "contractors"  # noqa
    full_name = Column(Text, nullable=False)
    short_name = Column(Text, nullable=True)
    inn = Column(String(12), unique=True, nullable=False)
    kpp = Column(String(9))
    ogrn = Column(String(15), unique=True, nullable=False)  # noqa

    activities = relationship(
        "Activity",
        secondary="activities_contractors",
        back_populates="contractors",
        cascade="all, delete",
    )
    addresses = relationship(
        "Address", back_populates="contractor", cascade="all, delete-orphan"
    )


class Address(BaseSQLModel):
    __tablename__ = "addresses"  # noqa
    contractor_id = Column(
        Integer, ForeignKey("contractors.id", ondelete="CASCADE"), nullable=False
    )
    region = Column(Text, nullable=True)
    locality = Column(Text)
    municipality = Column(Text, nullable=True)
    street = Column(Text, nullable=True)
    building = Column(Text, nullable=True)
    postal_code = Column(String(6), nullable=True)

    contractor = relationship("Contractor", back_populates="addresses")


class Activity(BaseSQLModel):
    __tablename__ = "activities"  # noqa
    code = Column(String(10), nullable=True)
    name = Column(Text, nullable=True)

    contractors = relationship(
        "Contractor",
        secondary="activities_contractors",
        back_populates="activities",
        cascade="all, delete",
    )


class ActivityContractor(Base):
    __tablename__ = "activities_contractors"  # noqa
    contractor_id = Column(
        Integer, ForeignKey("contractors.id", ondelete="CASCADE"), primary_key=True
    )
    activity_id = Column(
        Integer, ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True
    )
