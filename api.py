"""
api.py — API FastAPI pour les conventions collectives Elnet
=========================================================
Lancer avec : uvicorn api:app --reload
Doc Swagger : http://127.0.0.1:8000/docs
"""

import os
import json
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv

import models
import database
from database import engine, get_db

# Charger les variables d'environnement
load_dotenv()


# Créer les tables si elles n'existent pas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SDP Conventions API",
    description="""
API REST pour accéder aux données des conventions collectives françaises.

Développé par **Smart Data Pay**.

## Fonctionnalités
- Liste de toutes les conventions collectives
- Recherche par IDCC, nom, mot-clé
- Accès au contenu détaillé (sections, TOC, métadonnées)
- Filtrage par section (ex: maladie, congés, salaire)
- Synchronisation automatique des données
""",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────
# SCHÉMAS PYDANTIC (réponses)
# ──────────────────────────────────────────────────────────────

class MetadataOut(BaseModel):
    name: str
    url: Optional[str]
    pdf_url: Optional[str]
    elnet_id: str
    extraction_date: Optional[str]
    idcc: Optional[str]
    brochure: Optional[str]
    signature_date: Optional[str]
    extension_date: Optional[str]
    jo_date: Optional[str]
    revision_date: Optional[str]
    revision_extension: Optional[str]
    revision_jo: Optional[str]

    class Config:
        from_attributes = True


class TocEntryOut(BaseModel):
    id: Optional[str]       # entry_id Elnet
    sgml_id: Optional[str]
    title: Optional[str]

    class Config:
        from_attributes = True


class SectionOut(BaseModel):
    sequence: int
    is_preamble: bool
    text: Optional[str]
    html: Optional[str] = None # Sera exclu si False dans le dict de réponse

    class Config:
        from_attributes = True


class ConventionSummaryOut(BaseModel):
    elnet_id: str
    name: str
    idcc: Optional[str]
    brochure: Optional[str]
    url: Optional[str]
    sections_count: Optional[int] = None

    class Config:
        from_attributes = True


class ConventionDetailOut(BaseModel):
    metadata: MetadataOut
    toc: List[TocEntryOut] = []
    sections: List[SectionOut] = []
    status: str = "success"

    class Config:
        from_attributes = True


class StatsOut(BaseModel):
    total_conventions: int
    total_sections: int
    total_toc_entries: int
    total_integrales: int
    conventions_with_idcc: int
    last_updated: Optional[str]


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def get_convention_by_any_id_or_404(identifier: str, db: Session) -> models.Convention:
    """Recherche d'abord par IDCC, puis par ID Elnet."""
    # 1. Tentative par IDCC
    conv = db.query(models.Convention).filter(models.Convention.idcc == identifier).first()
    
    # 2. Si pas trouvé, tentative par ID Elnet (Yxxx)
    if not conv:
        # On enlève le .json si présent
        clean_id = identifier.replace(".json", "")
        conv = db.query(models.Convention).filter(models.Convention.elnet_id == clean_id).first()
        
    if not conv:
        raise HTTPException(
            status_code=404, 
            detail=f"Convention avec l'identifiant (IDCC ou Elnet ID) '{identifier}' introuvable"
        )
    return conv


# ──────────────────────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────────────────────

@app.get("/", tags=["General"])  # Public — pour le healthcheck et l'accueil
def root():
    """Page d'accueil de l'API (publique)."""
    return {
        "message": "SDP Conventions API — Elnet Edition",
        "version": "1.0.1",
        "docs": "/docs",
    }


@app.get("/conventions/", response_model=List[ConventionSummaryOut], tags=["Conventions"])
def list_conventions(
    offset: int = Query(0, ge=0, description="Offset pour la pagination"),
    limit: int = Query(500, ge=1, le=2000, description="Nombre max de résultats"),
    db: Session = Depends(get_db),
):
    """Retourne la liste résumée de toutes les conventions extraites."""
    conventions = db.query(models.Convention).offset(offset).limit(limit).all()
    result = []
    for c in conventions:
        sections_count = db.query(func.count(models.Section.id)).filter(
            models.Section.convention_id == c.id
        ).scalar()
        result.append(ConventionSummaryOut(
            elnet_id=c.elnet_id,
            name=c.name,
            idcc=c.idcc,
            brochure=c.brochure,
            url=c.url,
            sections_count=sections_count,
        ))
    return result


# ──────────────────────────────────────────────────────────────
# ROUTES IDCC SPÉCIFIQUES (déclarées AVANT {identifier} pour la priorité)
# ──────────────────────────────────────────────────────────────

@app.get("/conventions/idcc/{idcc}", response_model=ConventionDetailOut, tags=["Conventions IDCC"])
def get_by_idcc(
    idcc: str, 
    full: bool = Query(False, description="Inclure le HTML brut des sections"),
    db: Session = Depends(get_db)
):
    """Retourne une convention par son numéro IDCC."""
    conv = db.query(models.Convention).filter(models.Convention.idcc == idcc).first()
    if not conv:
        raise HTTPException(status_code=404, detail=f"IDCC '{idcc}' introuvable")
    return _build_convention_detail(conv, db, include_html=full)


@app.get("/conventions/idcc/{idcc}/toc", response_model=List[TocEntryOut], tags=["Conventions IDCC"])
def get_toc_by_idcc(idcc: str, db: Session = Depends(get_db)):
    """Retourne le sommaire d'une convention par son IDCC."""
    conv = db.query(models.Convention).filter(models.Convention.idcc == idcc).first()
    if not conv:
        raise HTTPException(status_code=404, detail=f"IDCC '{idcc}' introuvable")
    toc = db.query(models.TocEntry).filter(
        models.TocEntry.convention_id == conv.id
    ).order_by(models.TocEntry.position).all()
    return [TocEntryOut(id=t.entry_id, sgml_id=t.sgml_id, title=t.title) for t in toc]


@app.get("/conventions/idcc/{idcc}/sections", response_model=List[SectionOut], tags=["Conventions IDCC"])
def get_sections_by_idcc(
    idcc: str,
    keyword: Optional[str] = Query(None, description="Filtrer les sections par mot-clé"),
    db: Session = Depends(get_db),
):
    """Retourne les sections d'une convention par son IDCC."""
    conv = db.query(models.Convention).filter(models.Convention.idcc == idcc).first()
    if not conv:
        raise HTTPException(status_code=404, detail=f"IDCC '{idcc}' introuvable")
    query = db.query(models.Section).filter(models.Section.convention_id == conv.id)
    if keyword:
        query = query.filter(models.Section.text.ilike(f"%{keyword}%"))
    return query.order_by(models.Section.sequence).all()


@app.get("/conventions/idcc/{idcc}/metadata", response_model=MetadataOut, tags=["Conventions IDCC"])
def get_metadata_by_idcc(idcc: str, db: Session = Depends(get_db)):
    """Retourne les métadonnées d'une convention par son IDCC."""
    conv = db.query(models.Convention).filter(models.Convention.idcc == idcc).first()
    if not conv:
        raise HTTPException(status_code=404, detail=f"IDCC '{idcc}' introuvable")
    return MetadataOut.model_validate(conv)


@app.get("/conventions/file/{filename}", response_model=ConventionDetailOut, tags=["Conventions"])
def get_by_filename(
    filename: str,
    full: bool = Query(False, description="Inclure le HTML brut des sections"),
    db: Session = Depends(get_db)
):
    """Route de compatibilité pour le nom de fichier."""
    clean_id = filename.replace(".json", "")
    conv = db.query(models.Convention).filter(models.Convention.elnet_id == clean_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail=f"Fichier '{filename}' introuvable")
    return _build_convention_detail(conv, db, include_html=full)


# ──────────────────────────────────────────────────────────────
# ROUTES FLEXIBLES (identifier = IDCC ou Elnet ID)
# ──────────────────────────────────────────────────────────────

@app.get("/conventions/{identifier}", response_model=ConventionDetailOut, tags=["Conventions"])
def get_convention(
    identifier: str, 
    full: bool = Query(False, description="Inclure le HTML brut des sections"),
    db: Session = Depends(get_db)
):
    """
    Récupère une convention par son identifiant flexible.
    Accepte : Numéro IDCC (ex: 843) OU ID Elnet (ex: Y5079).
    """
    conv = get_convention_by_any_id_or_404(identifier, db)
    return _build_convention_detail(conv, db, include_html=full)


@app.get("/conventions/{identifier}/toc", response_model=List[TocEntryOut], tags=["Conventions"])
def get_toc(identifier: str, db: Session = Depends(get_db)):
    """Retourne le sommaire d'une convention (IDCC ou ID Elnet)."""
    conv = get_convention_by_any_id_or_404(identifier, db)
    toc = db.query(models.TocEntry).filter(
        models.TocEntry.convention_id == conv.id
    ).order_by(models.TocEntry.position).all()
    return [TocEntryOut(id=t.entry_id, sgml_id=t.sgml_id, title=t.title) for t in toc]


@app.get("/conventions/{identifier}/sections", response_model=List[SectionOut], tags=["Conventions"])
def get_sections(
    identifier: str,
    keyword: Optional[str] = Query(None, description="Filtrer les sections par mot-clé"),
    db: Session = Depends(get_db),
):
    """Retourne les sections d'une convention (IDCC ou ID Elnet)."""
    conv = get_convention_by_any_id_or_404(identifier, db)
    query = db.query(models.Section).filter(models.Section.convention_id == conv.id)
    if keyword:
        query = query.filter(models.Section.text.ilike(f"%{keyword}%"))
    return query.order_by(models.Section.sequence).all()


@app.get("/conventions/{identifier}/metadata", response_model=MetadataOut, tags=["Conventions"])
def get_metadata(identifier: str, db: Session = Depends(get_db)):
    """Retourne uniquement les métadonnées d'une convention (IDCC ou ID Elnet)."""
    conv = get_convention_by_any_id_or_404(identifier, db)
    return MetadataOut.model_validate(conv)


@app.get("/search/", tags=["Recherche"])
def search_conventions(
    q: str = Query(..., min_length=1, description="Terme de recherche (nom ou IDCC)"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Recherche dans les noms, IDCC et ID Elnet."""
    search = f"%{q}%"
    results = db.query(models.Convention).filter(
        or_(
            models.Convention.name.ilike(search),
            models.Convention.idcc.ilike(search),
            models.Convention.brochure.ilike(search),
            models.Convention.elnet_id.ilike(search),
        )
    ).limit(limit).all()

    return [
        {
            "elnet_id": c.elnet_id,
            "name": c.name,
            "idcc": c.idcc,
            "brochure": c.brochure,
        }
        for c in results
    ]


@app.get("/search/section", tags=["Recherche"])
def search_in_sections(
    keyword: str = Query(..., min_length=2, description="Mot-clé à chercher dans les sections"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Recherche un mot-clé dans le contenu des sections de toutes les conventions."""
    results = (
        db.query(models.Section, models.Convention)
        .join(models.Convention, models.Section.convention_id == models.Convention.id)
        .filter(models.Section.text.ilike(f"%{keyword}%"))
        .limit(limit)
        .all()
    )

    return [
        {
            "convention_name": conv.name,
            "elnet_id": conv.elnet_id,
            "idcc": conv.idcc,
            "sequence": sec.sequence,
            "text_preview": (sec.text[:200] + "...") if sec.text and len(sec.text) > 200 else sec.text,
        }
        for sec, conv in results
    ]


@app.get("/stats", response_model=StatsOut, tags=["General"])
def get_stats(db: Session = Depends(get_db)):
    """Retourne les statistiques globales des données."""
    total_conventions = db.query(func.count(models.Convention.id)).scalar()
    total_sections = db.query(func.count(models.Section.id)).scalar()
    total_toc = db.query(func.count(models.TocEntry.id)).scalar()
    total_integrales = db.query(func.count(models.Integrale.id)).scalar()
    with_idcc = db.query(func.count(models.Convention.id)).filter(
        models.Convention.idcc != None, models.Convention.idcc != ""
    ).scalar()

    last = db.query(models.Convention.extraction_date).order_by(
        models.Convention.created_at.desc()
    ).first()

    return StatsOut(
        total_conventions=total_conventions or 0,
        total_sections=total_sections or 0,
        total_toc_entries=total_toc or 0,
        total_integrales=total_integrales or 0,
        conventions_with_idcc=with_idcc or 0,
        last_updated=last[0] if last else None,
    )


@app.post("/sync", tags=["Administration"])
def sync_data():
    """Synchronise les données (MOCK)."""
    return {"message": "Synchronisation démarrée", "status": "success"}


@app.post("/reload", tags=["Administration"])
def reload_data():
    """Recharge les données (MOCK)."""
    return {"message": "Rechargement des données terminé", "status": "success"}


@app.get("/list", tags=["General"])
def get_conventions_list():
    """Retourne la liste brute des conventions (depuis conventions_list.json)."""
    list_path = "conventions_list.json"
    if os.path.exists(list_path):
        with open(list_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# ──────────────────────────────────────────────────────────────
# HELPERS INTERNES
# ──────────────────────────────────────────────────────────────

def _build_convention_detail(conv: models.Convention, db: Session, include_html: bool = False) -> ConventionDetailOut:
    toc = db.query(models.TocEntry).filter(
        models.TocEntry.convention_id == conv.id
    ).order_by(models.TocEntry.position).all()

    sections = db.query(models.Section).filter(
        models.Section.convention_id == conv.id
    ).order_by(models.Section.sequence).all()

    meta = MetadataOut(
        name=conv.name,
        url=conv.url,
        pdf_url=conv.pdf_url,
        elnet_id=conv.elnet_id,
        extraction_date=conv.extraction_date,
        idcc=conv.idcc,
        brochure=conv.brochure,
        signature_date=conv.signature_date,
        extension_date=conv.extension_date,
        jo_date=conv.jo_date,
        revision_date=conv.revision_date,
        revision_extension=conv.revision_extension,
        revision_jo=conv.revision_jo,
    )

    # Construction de la liste des sections avec filtrage HTML
    sec_list = []
    for s in sections:
        sec_data = {
            "sequence": s.sequence,
            "is_preamble": s.is_preamble,
            "text": s.text,
        }
        if include_html:
            sec_data["html"] = s.html
        sec_list.append(SectionOut(**sec_data))

    return ConventionDetailOut(
        metadata=meta,
        toc=[TocEntryOut(
            id=t.entry_id, # On mappe entry_id vers id
            sgml_id=t.sgml_id,
            title=t.title
        ) for t in toc],
        sections=sec_list,
        status="success"
    )
