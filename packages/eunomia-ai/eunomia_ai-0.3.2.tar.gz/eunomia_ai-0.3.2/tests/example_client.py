from eunomia_core import schemas
from eunomia_sdk_python import EunomiaClient

client = EunomiaClient()

client.check(
    principal_attributes={"role": "admin"},
    resource_attributes={"type": "document"},
    action="read",
)

client.check(principal_uri="user:alice", resource_uri="doc:confidential", action="read")

client.bulk_check(
    [
        {
            "principal": {"attributes": {"role": "admin"}},
            "resource": {"attributes": {"type": "document"}},
            "action": "read",
        },
        {
            "principal": {"attributes": {"role": "user"}},
            "resource": {"attributes": {"type": "document"}},
            "action": "write",
        },
    ]
)

client.bulk_check(
    [
        schemas.CheckRequest(
            principal=schemas.PrincipalCheck(uri="user:alice"),
            resource=schemas.ResourceCheck(uri="doc:confidential"),
            action="read",
        ),
        schemas.CheckRequest(
            principal=schemas.PrincipalCheck(uri="user:bob"),
            resource=schemas.ResourceCheck(uri="doc:confidential"),
            action="write",
        ),
    ]
)
