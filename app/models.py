from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON, DateTime, func


Base = declarative_base()


class Character(Base):
	__tablename__ = 'characters'
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False, index=True)
	status = Column(String, nullable=True)
	species = Column(String, nullable=True)
	type = Column(String, nullable=True)
	gender = Column(String, nullable=True)
	origin = Column(String, nullable=True)
	location = Column(String, nullable=True)
	image = Column(String, nullable=True)
	raw = Column(JSON, nullable=True)
	updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
