"""Company CRUD exports.

This module exposes the public classes and schemas used throughout the
application when dealing with companies.  The tests expect the
``UpdateCompanySubscription`` schema to be available from this package, but
it was not being imported previously which resulted in an ``ImportError``
when the API routers attempted to import it.  By exporting the missing
schema here we keep the package interface consistent and avoid the import
failure during test collection.
"""

from .schemas import (
    Company,
    CompanyInDB,
    UpdateCompany,
    CompanyMember,
    UpdateCompanySubscription,
)

# ``CompanyServices`` is intentionally not imported here to avoid circular
# dependencies during module initialisation.  Modules requiring the service
# should import it directly from ``app.crud.companies.services``.
