from pydantic import BaseModel, Field


class LanguageI18n(BaseModel):
    zh: dict = Field(description="response code中文集合")
    en: dict = Field(description="response code英文集合")
