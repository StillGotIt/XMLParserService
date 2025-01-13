import asyncio
import logging
from dataclasses import dataclass
from typing import Callable, Iterable

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError

from src.domain.entitites.activities import ContractorActivityEntity
from src.domain.entitites.adresses import AddressEntity
from src.domain.entitites.base import BaseEntity
from src.domain.entitites.composer import (
    ActivityAddressContractorComposer,
    ActivityAddressContractorWithIdComposer,
)
from src.infra.db.sql.db import AsyncPostgresClient
from src.logic.services.activity_contractor_service import ActivityContractorService
from src.logic.services.activity_service import ActivityService
from src.logic.services.address_service import AddressService
from src.logic.services.contractor_service import ContractorService
from src.logic.services.xml_parser import XMLParserService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass(eq=False)
class AddContractorActivityAddressUseCase:
    contractor_service: ContractorService
    activity_service: ActivityService
    address_service: AddressService
    activity_contractor_service: ActivityContractorService
    async_client: AsyncPostgresClient
    xml_parser_service: XMLParserService

    async def scrape_and_create(self, file: UploadFile):
        """Основной юзкейс агрегатор, который тригерит скрэпинг xml, а после пишет всё в БД"""
        logger.info(f"Starting to scrape and create entities from XML: {file}")

        try:
            (
                entities_list,
                all_activities_set,
            ) = await self.xml_parser_service.scrape_egrul(file=file)

            contractors = await self.bulk_create_entities(
                entities_list, self.process_contractor_entity
            )
            logger.info(
                f"Finished processing contractors entities len={len(entities_list)}"
            )

            await self.bulk_create_entities(
                contractors, self.process_activity_entity, 3
            )

            logger.info(f"Finished processing activities and contractors relations")

            await self.bulk_create_entities(
                [contractor.address for contractor in contractors],
                self.process_address_entity,
            )

            logger.info(
                f"Finished processing addresses entities len={len(contractors)}"
            )

            logger.info(f"Finished processing entities")
            return

        except Exception as e:
            logger.error(f"Error occurred during the scrape and create process: {e}")
            raise e

    async def bulk_create_entities(
        self,
        entities_list: Iterable[BaseEntity],
        process_func: Callable,
        chunk_size: int = 500,
    ) -> list[ActivityAddressContractorWithIdComposer]:
        """Общая структура для асинхронной вставки пачек данных в БД.
        Принимает функцию, в данном случае метод класса и тригерит его
        по достижении порога chunk'а
        """
        chunk = []
        successful_results = []

        for entity in entities_list:
            chunk.append(process_func(entity))
            if len(chunk) == chunk_size:
                results = await asyncio.gather(*chunk, return_exceptions=True)
                successful_results.extend(self.filter_successful_results(results))
                chunk.clear()

        if chunk:
            results = await asyncio.gather(*chunk, return_exceptions=True)
            successful_results.extend(self.filter_successful_results(results))
        logger.info(f"Finished processing entities of {len(entities_list)}")

        return successful_results

    @staticmethod
    def filter_successful_results(results):
        """Фильтрация эксепшенов от приемлимых результатов выполнения"""
        successful = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error occurred: {result}")
            else:
                successful.append(result)
        return successful

    async def process_contractor_entity(
        self, entity: ActivityAddressContractorComposer
    ) -> ActivityAddressContractorWithIdComposer:
        async with self.async_client.create_session() as session:
            try:
                contractor_model_entity = await self.contractor_service.get_or_create(
                    entity=entity.contractor, session=session
                )
                await session.commit()

                composer_entity = ActivityAddressContractorWithIdComposer(
                    contractor=contractor_model_entity,
                    address=AddressEntity(
                        region=entity.address.region,
                        municipality=entity.address.municipality,
                        locality=entity.address.locality,
                        street=entity.address.street,
                        postal_code=entity.address.postal_code,
                        building=entity.address.building,
                        contractor_id=contractor_model_entity.id,
                    ),
                    activity=entity.activity,
                )

                return composer_entity
            except SQLAlchemyError:
                await session.rollback()
                logger.error(f"Error processing contractor entity: {entity.contractor}")

    async def process_activity_entity(
        self, entity: ActivityAddressContractorWithIdComposer
    ):
        async with self.async_client.create_session() as session:
            try:
                activities = [
                    self.activity_service.get_or_create(
                        entity=activity, session=session
                    )
                    for activity in entity.activity
                ]
                results = await asyncio.gather(*activities)

                contractor_activity_data = [
                    ContractorActivityEntity(
                        contractor_id=entity.contractor.id, activity_id=activity.id
                    )
                    for activity in results
                ]

                await self.activity_contractor_service.bulk_create(
                    entities=contractor_activity_data, session=session
                )
                await session.commit()

                return results
            except SQLAlchemyError:
                await session.rollback()
                logger.error(f"Error processing activity entity")

    async def process_address_entity(self, entity: AddressEntity):
        async with self.async_client.create_session() as session:
            try:
                result = await self.address_service.get_or_create(
                    entity=entity, session=session
                )
                await session.commit()
                return result
            except SQLAlchemyError:
                await session.rollback()
                logger.error(f"Error processing activity entity")
