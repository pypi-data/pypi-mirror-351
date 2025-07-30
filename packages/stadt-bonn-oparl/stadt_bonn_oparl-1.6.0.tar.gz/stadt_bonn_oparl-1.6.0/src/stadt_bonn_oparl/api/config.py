from pydantic_settings import BaseSettings

import stadt_bonn_oparl


class Settings(BaseSettings):
    title: str = "Stadt Bonn OParl (partial) caching read-only-API"
    description: str = (
        "A search and cache for the Stadt Bonn OParl API to speed up access and reduce load on the original API."
    )
    version: str = stadt_bonn_oparl.__version__
    contact: dict = {
        "name": "Mach! Den! Staat!",
        "url": "https://machdenstaat.de",
    }


settings = Settings()
