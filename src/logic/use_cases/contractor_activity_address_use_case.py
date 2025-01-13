import asyncio
import time
import logging
from dataclasses import dataclass
from typing import Callable, Iterable

from src.domain.entitites.activities import ContractorActivityEntity
from src.domain.entitites.adresses import AddressEntity
from src.domain.entitites.base import BaseEntity
from src.domain.entitites.composer import ActivityAddressContractorComposer, ActivityAddressContractorWithIdComposer
from src.infra.db.sql.db import AsyncPostgresClient
from src.logic.services.activity_contractor_service import ActivityContractorService
from src.logic.services.activity_service import ActivityService
from src.logic.services.address_service import AddressService
from src.logic.services.contractor_service import ContractorService
from src.logic.services.xml_parser import XMLParserService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
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

    async def scrape_and_create(self, path_to_xml: str):
        logger.info(f"Starting to scrape and create entities from XML: {path_to_xml}")
        start_time = time.time()

        try:
            entities_list, all_activities_set = self.xml_parser_service.scrape_egrul(xml_file=path_to_xml)

            contractors = await self.bulk_create_entities(entities_list,
                                                          self.process_contractor_entity)

            await self.bulk_create_entities(contractors,
                                            self.process_activity_entity, 3)

            await self.bulk_create_entities([contractor.address for contractor in contractors],
                                            self.process_address_entity, )

            logger.info(f"Finished processing in {time.time() - start_time:.2f} seconds.")

        except Exception as e:
            logger.error(f"Error occurred during the scrape and create process: {e}")
            raise e

    async def bulk_create_entities(self, entities_list: Iterable[BaseEntity], process_func: Callable,
                                   chunk_size: int = 500) -> list[ActivityAddressContractorWithIdComposer]:
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

        return successful_results

    @staticmethod
    def filter_successful_results(results):
        successful = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error occurred: {result}")
            else:
                successful.append(result)
        return successful

    async def process_contractor_entity(self,
                                        entity: ActivityAddressContractorComposer) -> ActivityAddressContractorWithIdComposer:
        async with self.async_client.create_session() as session:
            try:
                logger.info(f"Processing contractor entity: {entity.contractor.full_name}")
                contractor_model_entity = await self.contractor_service.get_or_create(entity=entity.contractor,
                                                                                      session=session)
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
                        contractor_id=contractor_model_entity.id),
                    activity=entity.activity)

                return composer_entity
            except Exception as e:
                await session.rollback()
                logger.error(f"Error processing contractor entity: {e}")
                raise Exception(e)

    async def process_activity_entity(self, entity: ActivityAddressContractorWithIdComposer):
        async with self.async_client.create_session() as session:
            try:
                logger.info(f"Processing activity entity: {entity}")
                activities = [
                    self.activity_service.get_or_create(entity=activity, session=session) for activity in
                    entity.activity
                ]
                results = await asyncio.gather(*activities)

                contractor_activity_data = [
                    ContractorActivityEntity(contractor_id=entity.contractor.id, activity_id=activity.id) for activity
                    in results]

                await self.activity_contractor_service.bulk_create(entities=contractor_activity_data, session=session)
                await session.commit()

                return results
            except Exception as e:
                await session.rollback()
                logger.error(f"Error processing activity entity: {e}")
                raise Exception(e)

    async def process_address_entity(self, entity: AddressEntity):
        async with self.async_client.create_session() as session:
            try:
                logger.info(f"Processing address entity: {entity.street}, {entity.locality}")
                result = await self.address_service.get_or_create(entity=entity, session=session)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Error processing address entity: {e}")
                return e
