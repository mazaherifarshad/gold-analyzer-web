from fastapi import APIRouter

from analysis.engine import run_analysis

router = APIRouter(
    tags=["Analysis"]
)


@router.get("/analysis")
def analysis():

    return run_analysis()