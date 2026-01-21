from pathlib import Path
from typing import Optional

import typer

from imarina.core.defines import PROJECT_DIR, NOW
from imarina.core.imarina_excel import build_upload_excel
from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


def build_controller(
        ctx: typer.Context,
        countries_dict: Path = typer.Option(
            PROJECT_DIR / "input" / "countries.xlsx",
            help="Path of the countries dictionary file(.xlsx)"
        ),
        jobs_dict: Path = typer.Option(
            PROJECT_DIR / "input" / "Job_Descriptions.xlsx",
            help="Path of the jobs dictionary file(.xlsx)"
        ),
        imarina_input: Path = typer.Option(
            PROJECT_DIR / "input" / "iMarina.xlsx",
            help="Path of the iMarina input file(.xlsx)"
        ),
        a3_input: Path = typer.Option(
            PROJECT_DIR / "input" / "A3.xlsx",
            help="Path to A3 input file(.xlsx)"
        ),
        output_path: Optional[Path] = typer.Option(
            PROJECT_DIR / "output" / f"iMarina_upload_{NOW}.xlsx"
        ),
        personal_web_path: Optional[Path] = typer.Option(
            PROJECT_DIR / "input" / "Personal_web.xlsx"
        )

) -> None:
    build_upload_excel(
        output_path,
        countries_dict,
        jobs_dict,
        imarina_input,
        a3_input,
        personal_web_path
    )

