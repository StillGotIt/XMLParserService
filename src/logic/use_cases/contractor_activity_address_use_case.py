import asyncio
import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Callable, Iterable

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.domain.entitites.base import BaseEntity
from src.domain.entitites.composer import (
    ActivityAddressContractorComposer,
    ActivityAddressContractorWithIdComposer,
)
from src.infra.db.sql.db import AsyncPostgresClient
from src.infra.db.sql.models.models import Contractor, Address, Activity
from src.logic.services.xml_parser import XMLParserService, open_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass(eq=False)
class AddContractorActivityAddressUseCase:
    async_client: AsyncPostgresClient
    xml_parser_service: XMLParserService

    async def scrape_and_create(self, file_content: BytesIO):
        """Основной юзкейс агрегатор, который тригерит скрэпинг xml, а после пишет всё в БД"""
        logger.info(f"Starting to scrape and create entities from XML")

        try:
            entities_list = self.xml_parser_service.scrape_egrul(file_content=file_content)
            logger.info(f"Scraped entitites len={len(entities_list)}")
            result = await self.bulk_create_entities(entities_list=entities_list, process_func=self.bulk_create_all)
            logger.info(f"Added entitites to db")
            return result

        except Exception as e:
            logger.error(f"Error occurred during the scrape and create process: {e}")
            raise e

    async def bulk_create_entities(
            self,
            entities_list: Iterable[BaseEntity],
            process_func: Callable,
            chunk_size: int = 500,
    ) -> list[tuple[BaseException | ActivityAddressContractorWithIdComposer]]:
        """Общая структура для асинхронной вставки пачек данных в БД.
        Принимает функцию, в данном случае метод класса и тригерит его
        по достижении порога chunk'а
        """
        chunk = []
        results = []

        for entity in entities_list:
            chunk.append(process_func(entity))
            if len(chunk) == chunk_size:
                results.append(await asyncio.gather(*chunk, return_exceptions=True))
                chunk.clear()

        if chunk:
            results.append(await asyncio.gather(*chunk, return_exceptions=True))

        return results

    async def bulk_create_all(self, entity: ActivityAddressContractorComposer):
        async with self.async_client.create_session() as session:
            try:
                contractor = Contractor(**entity.contractor.to_dict())
                address = Address(**entity.address.to_dict())
                contractor.addresses.append(address)
                for activity_data in entity.activity:
                    activity = Activity(**activity_data.to_dict())
                    contractor.activities.append(activity)
                session.add(contractor)
                await session.commit()
            except IntegrityError as e:
                await session.rollback()
                raise e.detail
            except SQLAlchemyError as e:
                await session.rollback()
                raise SQLAlchemyError(f"Sqlalchemy eror occurred {e}")


def get_scrape_and_create_use_case() -> AddContractorActivityAddressUseCase:
    return AddContractorActivityAddressUseCase(
        async_client=AsyncPostgresClient(),
        xml_parser_service=XMLParserService(),
    )
