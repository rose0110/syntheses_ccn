"""
models.py — Modèles SQLAlchemy pour la base de données Elnet
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Convention(Base):
    __tablename__ = "conventions"

    id = Column(Integer, primary_key=True, index=True)
    elnet_id = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(500), nullable=False)
    url = Column(String(1000))
    pdf_url = Column(String(1000))
    idcc = Column(String(20), index=True)
    brochure = Column(String(20))
    signature_date = Column(String(30))
    extension_date = Column(String(30))
    jo_date = Column(String(30))
    revision_date = Column(String(30))
    revision_extension = Column(String(30))
    revision_jo = Column(String(30))
    header_table_html = Column(Text)
    preamble_html = Column(Text)
    raw_html = Column(Text)          # HTML brut facultatif (PATCH)
    extraction_date = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relations
    toc_entries = relationship("TocEntry", back_populates="convention",
                               cascade="all, delete-orphan")
    sections = relationship("Section", back_populates="convention",
                            cascade="all, delete-orphan")
    integrale = relationship("Integrale", back_populates="convention",
                             uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_conv_idcc", "idcc"),
        Index("ix_conv_name", "name"),
    )


class TocEntry(Base):
    __tablename__ = "toc_entries"

    id = Column(Integer, primary_key=True, index=True)
    convention_id = Column(Integer, ForeignKey("conventions.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    entry_id = Column(String(100))   # id Elnet (ex: Y5079-3)
    sgml_id = Column(String(100))
    title = Column(String(500))
    position = Column(Integer, default=0)

    convention = relationship("Convention", back_populates="toc_entries")


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    convention_id = Column(Integer, ForeignKey("conventions.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    sequence = Column(Integer, nullable=False)
    is_preamble = Column(Boolean, default=False)
    html = Column(Text)
    text = Column(Text)

    convention = relationship("Convention", back_populates="sections")

    __table_args__ = (
        Index("ix_section_conv_seq", "convention_id", "sequence"),
    )


class Integrale(Base):
    """HTML intégrale de la convention (toutes sections concaténées)."""
    __tablename__ = "integrales"

    id = Column(Integer, primary_key=True, index=True)
    convention_id = Column(Integer, ForeignKey("conventions.id", ondelete="CASCADE"),
                           unique=True, nullable=False)
    html = Column(Text)
    text = Column(Text)
    generated_at = Column(DateTime, server_default=func.now())

    convention = relationship("Convention", back_populates="integrale")
