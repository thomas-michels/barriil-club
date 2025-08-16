import pytest
import mongomock
from mongoengine import connect, disconnect

from app.crud.extractors.repositories import ExtractorRepository
from app.crud.extractors.models import ExtractorModel
from app.crud.extractors.schemas import Extractor, UpdateExtractor
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
async def test_create_extractor():
    repository = ExtractorRepository()
    extractor = Extractor(brand="BrandX")
    result = await repository.create(extractor)
    assert result.brand == "BrandX"
    assert ExtractorModel.objects.count() == 1


@pytest.mark.asyncio
async def test_select_by_id_found():
    doc = ExtractorModel(brand="BrandY")
    doc.save()
    repository = ExtractorRepository()
    res = await repository.select_by_id(doc.id)
    assert res.id == doc.id


@pytest.mark.asyncio
async def test_select_by_id_not_found():
    repository = ExtractorRepository()
    with pytest.raises(NotFoundError):
        await repository.select_by_id("invalid")


@pytest.mark.asyncio
async def test_select_all():
    ExtractorModel(brand="A").save()
    ExtractorModel(brand="B").save()
    repository = ExtractorRepository()
    res = await repository.select_all()
    assert len(res) == 2


@pytest.mark.asyncio
async def test_update_extractor():
    doc = ExtractorModel(brand="Old")
    doc.save()
    repository = ExtractorRepository()
    updated = await repository.update(doc.id, UpdateExtractor(brand="New"))
    assert updated.brand == "New"


@pytest.mark.asyncio
async def test_update_extractor_not_found():
    repository = ExtractorRepository()
    with pytest.raises(NotFoundError):
        await repository.update("invalid", UpdateExtractor(brand="New"))


@pytest.mark.asyncio
async def test_delete_extractor():
    doc = ExtractorModel(brand="Del")
    doc.save()
    repository = ExtractorRepository()
    result = await repository.delete_by_id(doc.id)
    assert result is True
    assert ExtractorModel.objects(id=doc.id).first().is_active is False


@pytest.mark.asyncio
async def test_delete_extractor_not_found():
    repository = ExtractorRepository()
    assert await repository.delete_by_id("invalid") is False
