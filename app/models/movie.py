"""Movie models for catalog."""
import uuid
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Table, DECIMAL, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


# Association tables
movie_genres = Table(
    'movie_genres',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)

movie_directors = Table(
    'movie_directors',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('director_id', Integer, ForeignKey('directors.id'), primary_key=True)
)

movie_stars = Table(
    'movie_stars',
    Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('star_id', Integer, ForeignKey('stars.id'), primary_key=True)
)


class Genre(Base):
    """Genres table."""
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")


class Star(Base):
    """Stars (actors) table."""
    __tablename__ = "stars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    movies = relationship("Movie", secondary=movie_stars, back_populates="stars")


class Director(Base):
    """Directors table."""
    __tablename__ = "directors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    movies = relationship("Movie", secondary=movie_directors, back_populates="directors")


class Certification(Base):
    """Certifications table."""
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    movies = relationship("Movie", back_populates="certification")


class Movie(Base):
    """Movies table."""
    __tablename__ = "movies"
    __table_args__ = (
        UniqueConstraint('name', 'year', 'time', name='uq_movie_name_year_time'),
    )

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    name = Column(String(250), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    time = Column(Integer, nullable=False)
    imdb = Column(Float, nullable=False)
    votes = Column(Integer, nullable=False)
    meta_score = Column(Float, nullable=True)
    gross = Column(Float, nullable=True)
    description = Column(Text, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=True)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    
    certification = relationship("Certification", back_populates="movies")
    genres = relationship("Genre", secondary=movie_genres, back_populates="movies")
    directors = relationship("Director", secondary=movie_directors, back_populates="movies")
    stars = relationship("Star", secondary=movie_stars, back_populates="movies")
