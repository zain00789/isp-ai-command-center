
from datetime import date

from fastapi import APIRouter, HTTPException

from backend.database import get_db_connection


router = APIRouter()

SUPPORTED_ISPS = ["Falcon", "Jazz", "CONNECT"]


def is_supported_isp(isp_name: str) -> bool:
    return isp_name.strip().lower() in [
        provider.lower() for provider in SUPPORTED_ISPS
    ]


def normalize_isp_name(isp_name: str) -> str:
    for provider in SUPPORTED_ISPS:
        if isp_name.strip().lower() == provider.lower():
            return provider

    return "Unknown"


def calculate_package_status(expiry_date: date) -> str:
    if expiry_date < date.today():
        return "expired"

    return "active"


def find_customer_by_id(customer_id: str):
    connection = get_db_connection()

    try:
        row = connection.execute(
            """
            SELECT
                customer_id,
                registered_phone,
                isp_provider,
                connection_status,
                plan,
                package_expiry
            FROM customers
            WHERE customer_id = ?
            """,
            (customer_id,),
        ).fetchone()

        return dict(row) if row else None

    finally:
        connection.close()


@router.get("/customers/{customer_id}/status")
def get_customer_status(customer_id: str):

    # Temporary security guard.
    # Replace with real authentication and customer verification later.
    is_verified = False

    if not is_verified:
        raise HTTPException(
            status_code=403,
            detail="Customer verification required",
        )

    customer = find_customer_by_id(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    expiry_date = date.fromisoformat(
        customer["package_expiry"]
    )

    package_status = calculate_package_status(expiry_date)

    return {
        "customer_id": customer["customer_id"],
        "registered_phone": customer["registered_phone"],
        "is_verified": is_verified,
        "isp_provider": customer["isp_provider"],
        "connection_status": customer["connection_status"],
        "plan": customer["plan"],
        "package_expiry": customer["package_expiry"],
        "package_status": package_status,
        "data_source": "sqlite",
    }


@router.get("/providers")
def get_supported_providers():
    return {
        "providers": SUPPORTED_ISPS,
        "total": len(SUPPORTED_ISPS),
    }
