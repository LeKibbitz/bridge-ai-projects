from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Entite(BaseModel):
    id: int
    nom: str
    adresse: Optional[str]
    code_postal: Optional[str]
    ville: Optional[str]
    telephone: Optional[str]
    email: Optional[str]
    region: str
    departement: str
    created_at: datetime
    updated_at: datetime

class Licensee(BaseModel):
    id: int
    nom: str
    prenom: str
    numero_licence: str
    date_naissance: Optional[datetime]
    email: Optional[str]
    telephone: Optional[str]
    adresse: Optional[str]
    code_postal: Optional[str]
    ville: Optional[str]
    besoin_special: Optional[bool]
    club_id: int
    statut: str  # licencié, sympathisant, bénévole, etc.
    saison: str
    created_at: datetime
    updated_at: datetime 