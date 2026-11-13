from fastapi.responses import JSONResponse

PROBLEM_BASE_URL = "https://competencehub.donner-partner.de/problems"


def problem_response(
    *,
    status: int,
    code: str,
    title: str,
    field_errors: list[dict[str, str]] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type": f"{PROBLEM_BASE_URL}/{code.replace('_', '-')}",
            "title": title,
            "status": status,
            "code": code,
            **({"field_errors": field_errors} if field_errors is not None else {}),
        },
        media_type="application/problem+json",
    )
