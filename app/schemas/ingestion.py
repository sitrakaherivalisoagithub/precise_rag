from pydantic import BaseModel, Field

class PdfIngestion(BaseModel):
    refresh: bool = Field(False, description="Set to true to delete all existing vectors before ingesting.")
