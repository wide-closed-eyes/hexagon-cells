from fastapi import APIRouter, HTTPException, Query, Request, Response

router = APIRouter(
    tags=["h3"],
    responses={404: {"description": "Not found"}},
)


@router.get("/hex")
async def get_hex(hex: str, request: Request):
    return await request.app.state.h3_storage.get_by_hex(hex)


@router.get("/avg")
async def get_avg(resolution: int, request: Request):
    try:
        return await request.app.state.h3_storage.get_avg(resolution)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/bbox")
async def get_bbox(
    request: Request, border: str = Query(..., description="lat/lon,lat/lon,...")
):
    try:
        points = border.split(",")
        return await request.app.state.h3_storage.get_bbox(points)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/bbox_kml")
async def get_bbox_kml(
    request: Request, border: str = Query(..., description="lat/lon,lat/lon,...")
):
    try:
        points = border.split(",")
        cells_kml = await request.app.state.h3_storage.get_bbox_kml(points)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return Response(
        content=cells_kml,
        media_type="application/vnd.google-earth.kml+xml",
        headers={
            "Content-Disposition": 'attachment; filename="bbox.kml"',
        },
    )
