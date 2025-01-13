from fastapi import FastAPI, UploadFile, File
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_200_OK

from src.api.lifespan import run_migrations
from src.infra.db.sql.db import AsyncPostgresClient
from src.infra.repos.activities import ActivityRepository
from src.infra.repos.activities_contractors import ActivityContractorRepository
from src.infra.repos.adresses import AddressRepository
from src.infra.repos.contractors import ContractorRepository
from src.logic.services.activity_contractor_service import ActivityContractorService
from src.logic.services.activity_service import ActivityService
from src.logic.services.address_service import AddressService
from src.logic.services.contractor_service import ContractorService
from src.logic.services.xml_parser import XMLParserService
from src.logic.use_cases.contractor_activity_address_use_case import (
    AddContractorActivityAddressUseCase,
)


def get_app():
    app = FastAPI(
        title="API",
        description="API for parsing xml and generating summary with gpt",
    )

    @app.on_event("startup")
    async def on_startup():
        await run_migrations()

    @app.get("/")
    async def healthcheck() -> dict[str, bool]:
        return {"Success": True}

    @app.post("/upload/")
    async def upload_file(file: UploadFile = File(...)):
        if not bool(file.filename.lower().endswith("xml")):
            raise HTTPException(
                status_code=400, detail="Файлы только форматом xml могут быть приняты"
            )
        try:
            scrape_and_create_use_case = AddContractorActivityAddressUseCase(
                contractor_service=ContractorService(ContractorRepository()),
                activity_service=ActivityService(ActivityRepository()),
                address_service=AddressService(AddressRepository()),
                activity_contractor_service=ActivityContractorService(
                    ActivityContractorRepository()
                ),
                async_client=AsyncPostgresClient(),
                xml_parser_service=XMLParserService(),
            )
            await scrape_and_create_use_case.scrape_and_create(file=file)
            return HTTP_200_OK
        except ValueError:
            raise HTTPException(status_code=400, detail="Файл неверной структуры")

    return app
