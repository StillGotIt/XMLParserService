import io

import pytest
from fastapi import UploadFile
from mock import mock


@pytest.fixture
def contractor_element():
    return mock.Mock()


@pytest.fixture
def mock_upload_file():
    mock_file = """<?xml version='1.0' encoding='UTF-8'?>
    <root>
        <СвЮЛ>
            <СвНаимЮЛ>
                <НаимЮЛПолн>Test Contractor</НаимЮЛПолн>
            </СвНаимЮЛ>
            <ИНН>1234567890</ИНН>
            <ОГРН>1234567890123</ОГРН>
            <КПП>987654321</КПП>
        </СвЮЛ>
    </root>""".encode(
        "utf-8"
    )
    file = io.BytesIO(mock_file)
    file.name = "test.xml"
    return UploadFile(file=file, filename="test.xml")
