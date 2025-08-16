import pytest
import mongomock
from mongoengine import connect, disconnect

from app.crud.companies.repositories import CompanyRepository
from app.crud.companies.models import CompanyModel
from app.crud.companies.schemas import Company, UpdateCompany
from app.core.exceptions import NotFoundError


@pytest.fixture(autouse=True)
def mongo():
    connect(
        "mongoenginetest",
        host="mongodb://localhost",
        mongo_client_class=mongomock.MongoClient,
    )
    yield
    disconnect()


@pytest.mark.asyncio
async def test_create_company():
    repository = CompanyRepository()
    company = Company(
        name="ACME",
        address_line1="Street 1",
        address_line2="Apt 2",
        phone_number="9999-9999",
        ddd="11",
        email="info@acme.com",
    )
    result = await repository.create(company)
    assert result.name == "ACME"
    assert CompanyModel.objects.count() == 1


@pytest.mark.asyncio
async def test_select_by_id_found():
    doc = CompanyModel(
        name="ACME",
        address_line1="Street 1",
        address_line2="Apt 2",
        phone_number="9999-9999",
        ddd="11",
        email="info@acme.com",
    )
    doc.save()
    repository = CompanyRepository()
    res = await repository.select_by_id(doc.id)
    assert res.id == doc.id


@pytest.mark.asyncio
async def test_select_by_id_not_found():
    repository = CompanyRepository()
    with pytest.raises(NotFoundError):
        await repository.select_by_id("invalid")


@pytest.mark.asyncio
async def test_select_all():
    CompanyModel(
        name="ACME",
        address_line1="Street 1",
        address_line2="Apt 2",
        phone_number="9999-9999",
        ddd="11",
        email="info@acme.com",
    ).save()
    CompanyModel(
        name="Beta",
        address_line1="Street 2",
        address_line2="Apt 3",
        phone_number="8888-8888",
        ddd="22",
        email="beta@test.com",
    ).save()
    repository = CompanyRepository()
    res = await repository.select_all()
    assert len(res) == 2


@pytest.mark.asyncio
async def test_update_company():
    doc = CompanyModel(
        name="ACME",
        address_line1="Street 1",
        address_line2="Apt 2",
        phone_number="9999-9999",
        ddd="11",
        email="info@acme.com",
    )
    doc.save()
    repository = CompanyRepository()
    updated = await repository.update(doc.id, UpdateCompany(name="New ACME"))
    assert updated.name == "New ACME"


@pytest.mark.asyncio
async def test_update_company_not_found():
    repository = CompanyRepository()
    with pytest.raises(NotFoundError):
        await repository.update("invalid", UpdateCompany(name="New"))


@pytest.mark.asyncio
async def test_delete_company():
    doc = CompanyModel(
        name="ACME",
        address_line1="Street 1",
        address_line2="Apt 2",
        phone_number="9999-9999",
        ddd="11",
        email="info@acme.com",
    )
    doc.save()
    repository = CompanyRepository()
    result = await repository.delete_by_id(doc.id)
    assert result is True
    assert CompanyModel.objects(id=doc.id).first().is_active is False


@pytest.mark.asyncio
async def test_delete_company_not_found():
    repository = CompanyRepository()
    assert await repository.delete_by_id("invalid") is False
