from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_200_OK

from src.api.lifespan import run_migrations
from src.logic.services.xml_parser import open_file
from src.logic.use_cases.contractor_activity_address_use_case import (
    AddContractorActivityAddressUseCase, get_scrape_and_create_use_case,
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
    async def upload_file(
            file: UploadFile = File(...),
            scrape_and_create_use_case: AddContractorActivityAddressUseCase = Depends(get_scrape_and_create_use_case)
    ):
        if not bool(file.filename.lower().endswith("xml")):
            raise HTTPException(
                status_code=400, detail="Only xml files can be processed"
            )
        file_content = await open_file(file=file)
        try:

            await scrape_and_create_use_case.scrape_and_create(file_content=file_content)
            return HTTP_200_OK
        except ValueError:
            raise HTTPException(status_code=400, detail="Wrong file structure")

    return app
