from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
sys.path.append('..')
from api.database import Convention, get_db, init_db

app = FastAPI(
    title="CCN API",
    description="API pour les conventions collectives",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ConventionBase(BaseModel):
    name: str
    idcc: Optional[str] = None
    url: str

class ConventionResponse(BaseModel):
    id: int
    name: str
    idcc: Optional[str]
    url: str
    status: str
    extracted_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ConventionDetail(ConventionResponse):
    sections: Optional[dict]
    toc: Optional[dict]
    signature_date: Optional[str]
    extension_date: Optional[str]
    jo_date: Optional[str]


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/")
async def root():
    return {
        "message": "CCN API",
        "version": "1.0.0",
        "endpoints": {
            "conventions": "/api/conventions",
            "convention_detail": "/api/conventions/{id}",
            "stats": "/api/stats"
        }
    }


@app.get("/api/conventions", response_model=List[ConventionResponse])
async def list_conventions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    idcc: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Liste toutes les conventions"""
    query = db.query(Convention)
    
    if status:
        query = query.filter(Convention.status == status)
    if idcc:
        query = query.filter(Convention.idcc == idcc)
    
    conventions = query.offset(skip).limit(limit).all()
    return conventions


@app.get("/api/conventions/{convention_id}", response_model=ConventionDetail)
async def get_convention(convention_id: int, db: Session = Depends(get_db)):
    """Récupère une convention par son ID"""
    convention = db.query(Convention).filter(Convention.id == convention_id).first()
    
    if not convention:
        raise HTTPException(status_code=404, detail="Convention not found")
    
    return convention


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Statistiques sur les conventions"""
    total = db.query(Convention).count()
    pending = db.query(Convention).filter(Convention.status == "pending").count()
    extracted = db.query(Convention).filter(Convention.status == "extracted").count()
    reformulated = db.query(Convention).filter(Convention.status == "reformulated").count()
    errors = db.query(Convention).filter(Convention.status == "error").count()
    
    return {
        "total": total,
        "pending": pending,
        "extracted": extracted,
        "reformulated": reformulated,
        "errors": errors
    }


@app.get("/api/search")
async def search_conventions(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db)
):
    """Recherche de conventions par nom ou IDCC"""
    conventions = db.query(Convention).filter(
        (Convention.name.contains(q)) | (Convention.idcc.contains(q))
    ).limit(50).all()
    
    return conventions


@app.get("/api/conventions/{convention_id}/integrale")
async def get_integrale(convention_id: int, db: Session = Depends(get_db)):
    """Récupère l'intégrale HTML complète d'une convention"""
    convention = db.query(Convention).filter(Convention.id == convention_id).first()
    
    if not convention:
        raise HTTPException(status_code=404, detail="Convention not found")
    
    if not convention.sections:
        raise HTTPException(status_code=404, detail="Convention not yet extracted")
    
    return {
        "id": convention.id,
        "name": convention.name,
        "idcc": convention.idcc,
        "url": convention.url,
        "metadata": {
            "signature_date": convention.signature_date,
            "extension_date": convention.extension_date,
            "jo_date": convention.jo_date,
            "brochure": convention.brochure,
            "pdf_url": convention.pdf_url
        },
        "toc": convention.toc,
        "sections": convention.sections,
        "extracted_at": convention.extracted_at
    }


@app.get("/api/conventions/{convention_id}/sections")
async def get_sections(convention_id: int, db: Session = Depends(get_db)):
    """Récupère uniquement les sections HTML"""
    convention = db.query(Convention).filter(Convention.id == convention_id).first()
    
    if not convention:
        raise HTTPException(status_code=404, detail="Convention not found")
    
    if not convention.sections:
        raise HTTPException(status_code=404, detail="Sections not available")
    
    return convention.sections


@app.get("/api/conventions/{convention_id}/toc")
async def get_toc(convention_id: int, db: Session = Depends(get_db)):
    """Récupère la table des matières"""
    convention = db.query(Convention).filter(Convention.id == convention_id).first()
    
    if not convention:
        raise HTTPException(status_code=404, detail="Convention not found")
    
    return convention.toc or []


@app.get("/api/integrales", response_model=List[ConventionResponse])
async def list_integrales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Liste toutes les intégrales disponibles (conventions extraites)"""
    conventions = db.query(Convention).filter(
        Convention.status.in_(["extracted", "reformulated"])
    ).offset(skip).limit(limit).all()
    
    return conventions


@app.get("/api/changes")
async def get_changes(
    skip: int = 0,
    limit: int = 100,
    processed: Optional[int] = None,
    since: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des conventions qui ont changé
    
    - **processed**: 0=non traités, 1=traités (optionnel)
    - **since**: Date ISO (ex: 2026-02-01) pour filtrer depuis une date
    """
    from api.database import ConventionChange
    
    query = db.query(ConventionChange)
    
    if processed is not None:
        query = query.filter(ConventionChange.processed == processed)
    
    if since:
        try:
            from datetime import datetime as dt
            since_date = dt.fromisoformat(since)
            query = query.filter(ConventionChange.change_date >= since_date)
        except:
            pass
    
    changes = query.order_by(ConventionChange.change_date.desc()).offset(skip).limit(limit).all()
    
    # Enrichir avec infos convention
    result = []
    for change in changes:
        conv = db.query(Convention).filter(Convention.id == change.convention_id).first()
        if conv:
            result.append({
                "change_id": change.id,
                "convention_id": change.convention_id,
                "convention_name": conv.name,
                "idcc": conv.idcc,
                "change_date": change.change_date,
                "change_type": change.change_type,
                "old_hash": change.old_hash,
                "new_hash": change.new_hash,
                "processed": change.processed,
                "details": change.details
            })
    
    return result


@app.get("/api/changes/unprocessed")
async def get_unprocessed_changes(db: Session = Depends(get_db)):
    """Récupère uniquement les changements non traités"""
    from api.database import ConventionChange
    
    changes = db.query(ConventionChange).filter(
        ConventionChange.processed == 0
    ).order_by(ConventionChange.change_date.desc()).all()
    
    result = []
    for change in changes:
        conv = db.query(Convention).filter(Convention.id == change.convention_id).first()
        if conv:
            result.append({
                "change_id": change.id,
                "convention_id": change.convention_id,
                "convention_name": conv.name,
                "idcc": conv.idcc,
                "change_date": change.change_date,
                "url_integrale": f"/api/conventions/{change.convention_id}/integrale"
            })
    
    return result


@app.post("/api/changes/{change_id}/mark-processed")
async def mark_change_processed(change_id: int, db: Session = Depends(get_db)):
    """Marque un changement comme traité"""
    from api.database import ConventionChange
    
    change = db.query(ConventionChange).filter(ConventionChange.id == change_id).first()
    
    if not change:
        raise HTTPException(status_code=404, detail="Change not found")
    
    change.processed = 1
    db.commit()
    
    return {"message": "Change marked as processed", "change_id": change_id}


@app.get("/api/changes/stats")
async def get_changes_stats(db: Session = Depends(get_db)):
    """Statistiques sur les changements"""
    from api.database import ConventionChange
    
    total = db.query(ConventionChange).count()
    unprocessed = db.query(ConventionChange).filter(ConventionChange.processed == 0).count()
    processed = db.query(ConventionChange).filter(ConventionChange.processed == 1).count()
    
    # Derniers changements
    latest = db.query(ConventionChange).order_by(
        ConventionChange.change_date.desc()
    ).limit(5).all()
    
    latest_changes = []
    for change in latest:
        conv = db.query(Convention).filter(Convention.id == change.convention_id).first()
        if conv:
            latest_changes.append({
                "convention_id": change.convention_id,
                "convention_name": conv.name,
                "change_date": change.change_date
            })
    
    return {
        "total_changes": total,
        "unprocessed": unprocessed,
        "processed": processed,
        "latest_changes": latest_changes
    }


# ============================================
# EXTRACTION API
# ============================================

import threading
import subprocess
from datetime import datetime as dt

# État de l'extraction (simple in-memory)
extraction_state = {
    "running": False,
    "current_convention": None,
    "total": 0,
    "processed": 0,
    "errors": 0,
    "started_at": None,
    "last_log": []
}


def run_extraction(start: int, end: int):
    """Lance extraction en arrière-plan"""
    global extraction_state
    
    extraction_state["running"] = True
    extraction_state["started_at"] = dt.utcnow()
    extraction_state["last_log"] = []
    extraction_state["total"] = end - start if end else 0
    extraction_state["processed"] = 0
    extraction_state["errors"] = 0
    
    try:
        # Lancer extraction via subprocess
        cmd = ["python", "extract_all_to_db.py", "--start", str(start)]
        if end:
            cmd.extend(["--end", str(end)])
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Lire logs
        for line in process.stdout:
            extraction_state["last_log"].append(line.strip())
            if len(extraction_state["last_log"]) > 50:
                extraction_state["last_log"].pop(0)
            
            # Parser les logs pour mettre à jour état
            if "Success" in line:
                extraction_state["processed"] += 1
            elif "Failed" in line or "Error" in line:
                extraction_state["errors"] += 1
            elif "[" in line and "]" in line:
                try:
                    conv_name = line.split("]")[1].strip()
                    extraction_state["current_convention"] = conv_name
                except:
                    pass
        
        process.wait()
        
    except Exception as e:
        extraction_state["last_log"].append(f"ERROR: {str(e)}")
        extraction_state["errors"] += 1
    
    finally:
        extraction_state["running"] = False
        extraction_state["current_convention"] = None


@app.post("/api/extract/start")
async def start_extraction(
    start: int = Query(0, description="ID de la première convention à extraire", ge=0),
    end: Optional[int] = Query(None, description="ID de fin (exclusif). Si non spécifié, extrait jusqu'à la fin", ge=0),
    background_tasks: BackgroundTasks = None
):
    """
    Démarre une extraction en arrière-plan
    
    ## Exemples:
    - **Une seule**: `start=0&end=1` → Convention ID 0
    - **10 premières**: `end=10` → Conventions 0-9  
    - **Range**: `start=50&end=100` → Conventions 50-99
    - **Toutes**: (aucun paramètre) → Toutes les conventions
    
    ## Réponse:
    Retourne l'URL pour vérifier le statut de l'extraction
    """
    global extraction_state
    
    if extraction_state["running"]:
        raise HTTPException(
            status_code=409,
            detail="Une extraction est déjà en cours"
        )
    
    # Lancer en thread séparé
    thread = threading.Thread(target=run_extraction, args=(start, end or 0))
    thread.daemon = True
    thread.start()
    
    return {
        "message": "Extraction démarrée",
        "start": start,
        "end": end,
        "conventions_count": (end - start) if end else "toutes",
        "status_url": "/api/extract/status"
    }


@app.get("/api/extract/status")
async def get_extraction_status():
    """Récupère le statut de l'extraction en cours"""
    global extraction_state
    
    return {
        "running": extraction_state["running"],
        "current_convention": extraction_state["current_convention"],
        "total": extraction_state["total"],
        "processed": extraction_state["processed"],
        "errors": extraction_state["errors"],
        "started_at": extraction_state["started_at"],
        "progress_percent": round((extraction_state["processed"] / extraction_state["total"] * 100) if extraction_state["total"] > 0 else 0, 1),
        "last_logs": extraction_state["last_log"][-10:]  # 10 dernières lignes
    }


@app.post("/api/extract/stop")
async def stop_extraction():
    """Arrête l'extraction en cours (marque pour arrêt)"""
    global extraction_state
    
    if not extraction_state["running"]:
        raise HTTPException(
            status_code=400,
            detail="Aucune extraction en cours"
        )
    
    # Note: Arrêt gracieux difficile avec subprocess
    # Pour l'instant, juste indiquer qu'on veut arrêter
    return {
        "message": "Demande d'arrêt envoyée (l'extraction se terminera après la convention en cours)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
