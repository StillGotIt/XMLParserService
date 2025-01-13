import pytest
from unittest import mock
from src.logic.services.xml_parser import XMLParserService


def test_scrape_contractor_entity(mock_upload_file, contractor_element):
    contractor_element.get = mock.Mock(
        side_effect=lambda key: {
            "ОГРН": "1234567890123",
            "ИНН": "1234567890",
            "КПП": "987654321",
        }.get(key)
    )
    full_name_element = mock.Mock()
    full_name_element.get = mock.Mock(return_value="Test Contractor")
    contractor_element.find = mock.Mock(return_value=full_name_element)

    with mock.patch("src.logic.services.xml_parser.logger.error") as mock_error:
        contractor = XMLParserService.scrape_contractor_entity(contractor_element)

        assert contractor.full_name == "Test Contractor"
        assert contractor.inn == "1234567890"
        assert contractor.ogrn == "1234567890123"
        assert contractor.kpp == "987654321"
        mock_error.assert_not_called()


def test_scrape_activities(mock_upload_file, contractor_element):
    activities = [
        mock.Mock(
            get=mock.Mock(
                side_effect=lambda key: {
                    "КодОКВЭД": "01",
                    "НаимОКВЭД": "Agriculture",
                }.get(key)
            )
        )
    ]
    contractor_element.findall = mock.Mock(return_value=activities)

    activities_entities = XMLParserService.scrape_activities(contractor_element)

    assert isinstance(activities_entities, list)
    assert len(activities_entities) == 1
    assert activities_entities[0].code == "01"
    assert activities_entities[0].name == "Agriculture"


@pytest.mark.asyncio
async def test_scrape_egrul(mock_upload_file):
    xml_file = mock_upload_file
    contractor_element = mock.Mock(tag="СвЮЛ")
    activities_set = set()

    with mock.patch(
        "src.logic.services.xml_parser.XMLParserService.scrape_contractor_composer"
    ) as mock_scrape_composer:
        mock_scrape_composer.return_value = (contractor_element, activities_set)
        with mock.patch("xml.etree.ElementTree.iterparse") as mock_iterparse:
            mock_iterparse.return_value = [("end", contractor_element)]

            (
                parsed_contractors,
                parsed_activities,
            ) = await XMLParserService().scrape_egrul(xml_file)

            mock_scrape_composer.assert_called_once()
            assert len(parsed_contractors) == 1
            assert len(parsed_activities) == 0


def test_scrape_address_address_case_with_valid_values(
    mock_upload_file, contractor_element
):
    contractor_element.find = mock.Mock()
    contractor_element.find.return_value.get = mock.Mock(
        side_effect=lambda attr: {
            "НаимРегион": "Region",
            "Наим": "Municipality",
            "НаимУлица": "Street",
            "Индекс": "12345",
            "Дом": "Building",
            "Корпус": None,
        }.get(attr)
    )

    address = XMLParserService()._scrape_address_address_case(contractor_element)

    assert address.region == "Region"
    assert address.municipality == "Municipality"
    assert address.street == "Street"
    assert address.building == "Building"
    assert address.postal_code == "12345"


def test_scrape_address_address_case_with_missing_region(
    mock_upload_file, contractor_element
):
    contractor_element.find = mock.Mock()
    contractor_element.find.return_value.get = mock.Mock(
        side_effect=lambda attr: {
            "Наим": "Municipality",
            "НаимУлица": "Street",
            "Индекс": "12345",
            "Дом": "Building",
        }.get(attr)
    )

    address = XMLParserService()._scrape_address_address_case(contractor_element)

    assert address.region is None
    assert address.municipality == "Municipality"
    assert address.locality == "Municipality"
    assert address.street == "Street"
    assert address.building == "Building"
    assert address.postal_code == "12345"


def test_scrape_address_address_case_with_missing_address_data(
    mock_upload_file, contractor_element
):
    contractor_element.find = mock.Mock()
    contractor_element.find.return_value.get = mock.Mock(
        side_effect=lambda attr: {
            "НаимРегион": None,
            "Наим": None,
            "НаимУлица": None,
            "Индекс": None,
            "Дом": None,
            "Корпус": None,
        }.get(attr)
    )

    address = XMLParserService()._scrape_address_address_case(contractor_element)

    assert address.region is None
    assert address.municipality is None
    assert address.locality is None
    assert address.street is None
    assert address.building is None
    assert address.postal_code is None


def test_scrape_address_address_case_with_fallbacks(
    mock_upload_file, contractor_element
):
    contractor_element.find = mock.Mock()
    contractor_element.find.return_value.get = mock.Mock(
        side_effect=lambda attr: {
            "НаимРегион": "Region",
            "Наим": "Municipality",
            "НаимУлица": "Street",
            "Индекс": "12345",
            "Дом": None,
            "Корпус": "Corp",
        }.get(attr)
    )

    address = XMLParserService()._scrape_address_address_case(contractor_element)

    assert address.region == "Region"
    assert address.municipality == "Municipality"
    assert address.locality == "Municipality"
    assert address.street == "Street"
    assert address.building == "Corp"
    assert address.postal_code == "12345"
