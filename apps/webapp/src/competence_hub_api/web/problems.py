from fastapi.responses import JSONResponse

PROBLEM_BASE_URL = "https://competencehub.donner-partner.de/problems"


def problem_response(
    *,
    status: int,
    code: str,
    title: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type": f"{PROBLEM_BASE_URL}/{code.replace('_', '-')}",
            "title": title,
            "status": status,
            "code": code,
        },
        media_type="application/problem+json",
    )
