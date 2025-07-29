from typing import Optional
from pydantic import BaseModel, Field

class Cni(BaseModel):
    """
    Représente les informations extraites d'une carte d'identité.
    """
    is_recto:bool=Field(default=True)
    first_name: Optional[str] = Field(default=None, description="Prénom")
    last_name: Optional[str] = Field(default=None, description="Nom de famille")
    date_of_birth: Optional[str] = Field(default=None, description="Date de naissance (format JJ/MM/AAAA)")
    id_number: Optional[str] = Field(default=None, description="Numéro d'identité")
    address: Optional[str] = Field(default=None, description="Adresse")
    issue_date: Optional[str] = Field(default=None, description="Date d'émission (format JJ/MM/AAAA)")
    expiry_date: Optional[str] = Field(default=None, description="Date d'expiration (format JJ/MM/AAAA)")
    gender: Optional[str] = Field(default=None, description="Genre (M/F)")
    mrz:Optional[str]=Field(default=None,description="Zone MRZ")

