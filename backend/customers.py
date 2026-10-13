
from datetime import date
from fastapi import APIRouter, HTTPException

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

@router.get("/customers/{customer_id}/status")
def get_customer_status(customer_id: str):


    is_verified = False

    if not is_verified:
        raise HTTPException(
            status_code=403,
            detail="Customer verification required"
        )

    expiry_date = date.fromisoformat("2026-10-31")
    package_status = calculate_package_status(expiry_date)

    return {
        "customer_id": customer_id,
        "registered_phone": "03000000000",
        "is_verified": False,
        "isp_provider": "Falcon",
        "connection_status": "online",
        "plan": "Fiber 20 Mbps",
        "package_expiry": "2026-10-31",
        "package_status": package_status,
        "data_source": "mock"
    }


@router.get("/providers")
def get_supported_providers():
    return {
        "providers": SUPPORTED_ISPS,
        "total": len(SUPPORTED_ISPS)
    }
