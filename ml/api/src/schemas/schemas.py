from pydantic import BaseModel

class LeftoverSchema(BaseModel):
    state: str
    dataframe: dict | None
    plot_image: str


class RegularitySchema(BaseModel):
    is_regular: bool


class DebitCreditSchema(BaseModel):
    state: str
    credit: dict | None
    debit: dict | None
    plot_image: str


class PurchasesSchema(BaseModel):
    state: str
    dataframe: dict | None
    plot_image: str


class ForecastSchema(BaseModel):
    state: str
    prediction: float
    plot_image: str


class UserPickSchema(BaseModel):
    STE: str
    SPGZ_code: str | None
    SPGZ_name: str | None


class ExcelSchema(BaseModel):
    file: str

class AudioSchema(BaseModel):
    audio: str