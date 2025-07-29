# Keycloak Admin Model Representation Pydantic v2 Bindings

This project contains *ONLY* the pydantic v2 bindings for [Keycloak](https://www.keycloak.org/) model representations for use in Python based projects utilizing Keycloak admin APIs. 

For APIs, I recommend [Mantelo](https://mantelo.readthedocs.io/en/latest/). Since this library itself doesn't offer any model representation bindings, projects can use both these libraries together for a complete pydantic compliant experience.

## Caveats

1. Transform model representations to python dictionaries using pydantic `model_dump()`. *Mantelo* client expects python dictionaries for write operations. Keycloak API semantics expect that all **unset** attributes are excluded.

    ```python
    class TenantAdapter:
        @classmethod
        def model_new(cls, schema: TenantReqSchema) -> OrganizationRepresentation:
            """Convert `TenantReqSchema` to `OrganizationRepresentation`."""
            return OrganizationRepresentation(
                name=schema.name,
                alias=schema.name.replace(" ", "_"),
                domains=[OrganizationDomainRepresentation(name=f"{schema.name.replace(' ', '-').lower()}.org", verified=False)],
                enabled=schema.active,
                attributes={"tax_id": [schema.tax_id], "address": [schema.address]},
            ).model_dump(exclude_unset=True)
    ```

2. Models use `snake-case` attribute names for applications; but for Keycloak APIs, users should **aliases** to ensure actual Keyclock API attribute names are used.

    ```python
    class TenantAdapter:
        @classmethod
        def model_new(cls, schema: TenantReqSchema) -> Any:
            """Convert `TenantReqSchema` to `Serializable`."""
            return OrganizationRepresentation(
                name=schema.name,
                alias=schema.name.replace(" ", "_"),
                domains=[OrganizationDomainRepresentation(name=f"{schema.name.replace(' ', '-').lower()}.org", verified=False)],
                enabled=schema.active,
                attributes={"tax_id": [schema.tax_id], "address": [schema.address]},
            ).model_dump(exclude_unset=True, use_alias=True)
    ```

3. Transform python dictionaries to model representations using python dictionary unpacking operator `**`. *Mantelo* client returns python dictionaries for read operations.

    ```python
    class TenantAdapter:
        @classmethod
        def schema(cls, data: Any | None) -> TenantResSchema | None:
            """Convert `Dict` to `TenantResSchema`."""
            if data is None:
                return None

            # Coerse data dict to `OrganizationRepresentation`
            #
            representation = OrganizationRepresentation(**data)
            return TenantResSchema(
                id=representation.id,
                name=representation.name,
                address=representation.attributes["address"][0],
                tax_id=representation.attributes["tax_id"][0],
                active=representation.enabled,
            )
    ```

## Versioning

I intend to keep the library versioning synced with the latest stable **Keycloak** release.

## Installing

* `pip install keycloak-admin-client`
* `poetry add keycloak-admin-client`

