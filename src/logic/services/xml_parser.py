import logging
from typing import Optional

import xml.etree.ElementTree as Et

from src.domain.entitites.activities import ActivityEntity
from src.domain.entitites.adresses import AddressEntity
from src.domain.entitites.composer import ActivityAddressContractorComposer
from src.domain.entitites.contractors import ContractorEntity

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class XMLParserService:
    @staticmethod
    def _get_first_existing_value(
            element: Et.Element,
            paths: list[str],
            attribute: Optional[str] = None) -> Optional[str]:
        for path in paths:
            found_element = element.find(path)
            if found_element is not None:
                value = found_element.get(attribute) if attribute else found_element.text
                return value
        return None

    def _scrape_address_address_case(self, contractor_element: Et.Element) -> AddressEntity:
        region = self._get_first_existing_value(
            contractor_element,
            paths=[".//НаимРегион", ".//Регион"],
            attribute="НаимРегион"
        )
        municipality = self._get_first_existing_value(
            contractor_element,
            paths=[".//МуниципРайон"],
            attribute="Наим"
        )
        locality = self._get_first_existing_value(
            contractor_element,
            paths=[".//НаселенПункт", ".//ГородСелПоселен", ".//Город"],
            attribute="Наим"
        ) or region

        street = self._get_first_existing_value(
            contractor_element,
            paths=[".//Улица"],
            attribute="НаимУлица"
        )

        building = self._get_first_existing_value(
            contractor_element,
            paths=[".//АдресРФ"],
            attribute="Дом"
        ) or self._get_first_existing_value(
            contractor_element,
            paths=[".//АдресРФ"],
            attribute="Корпус"
        )

        postal_code = self._get_first_existing_value(
            contractor_element,
            paths=[".//АдресРФ"],
            attribute="Индекс"
        )

        return AddressEntity(
            region=region,
            municipality=municipality,
            locality=locality,
            street=street,
            postal_code=postal_code,
            building=building,
        )

    def _scrape_address_no_address_case(self, contractor_element: Et.Element) -> AddressEntity:
        postal_code = self._get_first_existing_value(
            contractor_element,
            paths=[".//СвАдрЮЛФИАС"],
            attribute="Индекс"
        )
        region = self._get_first_existing_value(
            contractor_element,
            paths=[".//НаимРегион"]
        )
        municipality = self._get_first_existing_value(
            contractor_element,
            paths=[".//МуниципРайон"],
            attribute="Наим"
        )
        locality = self._get_first_existing_value(
            contractor_element,
            paths=[".//НаселенПункт", ".//ГородСелПоселен"],
            attribute="Наим"
        ) or region

        street = self._get_first_existing_value(
            contractor_element,
            paths=[".//ЭлУлДорСети"],
            attribute="Наим"
        )
        building = self._get_first_existing_value(
            contractor_element,
            paths=[".//Здание"],
            attribute="Номер"
        )

        return AddressEntity(
            region=region,
            municipality=municipality,
            locality=locality,
            street=street,
            postal_code=postal_code,
            building=building,
        )

    @staticmethod
    def scrape_contractor_entity(contractor_element) -> ContractorEntity:
        try:
            full_name_element = contractor_element.find(".//СвНаимЮЛ")
            short_name_element = contractor_element.find(".//СвНаимЮЛСокр")

            contractor_info = {
                "ogrn": contractor_element.get("ОГРН"),
                "inn": contractor_element.get("ИНН"),
                "kpp": contractor_element.get("КПП"),
                "full_name": full_name_element.get("НаимЮЛПолн") if full_name_element is not None else None,
                "short_name": short_name_element.get("НаимСокр") if short_name_element is not None else None,
            }

            return ContractorEntity(
                full_name=contractor_info["full_name"],
                short_name=contractor_info["short_name"],
                kpp=contractor_info["kpp"],
                inn=contractor_info["inn"],
                ogrn=contractor_info["ogrn"],
            )
        except Exception as e:
            logger.error(f"Error parsing contractor entity: {e}")
            raise ValueError(f"Error parsing contractor entity: {e}")

    def scrape_address_entity(self, contractor_element) -> Optional[AddressEntity]:
        if contractor_element.find(".//АдресРФ") is not None:
            return self._scrape_address_address_case(contractor_element)
        return self._scrape_address_no_address_case(contractor_element)

    @staticmethod
    def scrape_activities(contractor_element) -> list[ActivityEntity]:
        try:
            activities = contractor_element.findall(".//СвОКВЭД/")
            activity_entities = []

            for activity in activities:
                code = activity.get("КодОКВЭД")
                name = activity.get("НаимОКВЭД")

                activity_entities.append(
                    ActivityEntity(
                        code=code,
                        name=name))

            return activity_entities
        except Exception as e:
            logger.error(f"Error parsing activities: {e}")
            raise ValueError(f"Error parsing activities: {e}")

    def scrape_contractor_composer(self, contractor_element) -> tuple[ActivityAddressContractorComposer, set]:
        contractor = self.scrape_contractor_entity(contractor_element)
        activities = self.scrape_activities(contractor_element)
        activities_set = set(activities)
        address = self.scrape_address_entity(contractor_element.find(".//СвАдресЮЛ"))

        return ActivityAddressContractorComposer(
            contractor=contractor,
            address=address,
            activity=activities,
        ), activities_set

    def scrape_egrul(self, xml_file: str) -> tuple[list[ActivityAddressContractorComposer], set]:
        logger.info(f"Starting to scrape EGRUL file: {xml_file}")
        try:
            scraped_contractors = []
            _all_activities_set = set()

            try:
                for event, contractor_element in Et.iterparse(xml_file, events=("end",)):
                    if contractor_element.tag == "СвЮЛ":
                        composer_entity, activities_set = self.scrape_contractor_composer(contractor_element)
                        scraped_contractors.append(composer_entity)
                        _all_activities_set |= activities_set
                        contractor_element.clear()
                logger.info(f"Finished scraping xml file total_contractors={len(scraped_contractors)}")
                return scraped_contractors, _all_activities_set
            except Et.ParseError as e:
                logger.error(f"Invalid XML format in file {xml_file}: {e}")
                raise ValueError(f"Invalid XML format in file {xml_file}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during parsing: {e}")
            raise RuntimeError(f"Unexpected error during parsing: {e}")
