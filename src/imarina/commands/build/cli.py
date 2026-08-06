from pathlib import Path

import typer

from imarina.core.defines import NOW, PROJECT_DIR, REQUIRED_INPUT_FILES
from imarina.core.imarina_excel import build_upload_excel
from imarina.core.log_utils import get_logger

logger = get_logger(__name__)

INPUT_DIR = PROJECT_DIR / "input"


def build_controller(
        ctx: typer.Context,
        countries_dict: Path = typer.Option(
            INPUT_DIR / REQUIRED_INPUT_FILES["countries"],
            help="Path of the countries dictionary file(.xlsx)"
        ),
        jobs_dict: Path = typer.Option(
            INPUT_DIR / REQUIRED_INPUT_FILES["jobs"],
            help="Path of the jobs dictionary file(.xlsx)"
        ),
        imarina_input: Path = typer.Option(
            INPUT_DIR / REQUIRED_INPUT_FILES["imarina"],
            help="Path of the iMarina input file(.xlsx)"
        ),
        a3_input: Path = typer.Option(
            INPUT_DIR / REQUIRED_INPUT_FILES["a3"],
            help="Path to A3 input file(.xlsx)"
        ),
        output_path: Path = typer.Option(
            PROJECT_DIR / "output" / f"iMarina_upload_{NOW}.xlsx"
        ),
        personal_web_path: Path | None = typer.Option(
            INPUT_DIR / REQUIRED_INPUT_FILES["personal_web"]
        ),
        unit_group_path: Path | None = typer.Option(
            INPUT_DIR / REQUIRED_INPUT_FILES["unit_group"]
        ),
        entity_type_path: Path | None = typer.Option(
            INPUT_DIR / REQUIRED_INPUT_FILES["unit_type"]
        ),
        job_description_entity_path: Path | None = typer.Option(
            INPUT_DIR / REQUIRED_INPUT_FILES["job_description_entity"]
        )
) -> None:
    build_upload_excel(
        output_path,
        countries_dict,
        jobs_dict,
        imarina_input,
        a3_input,
        personal_web_path,
        unit_group_path,
        entity_type_path,
        job_description_entity_path
    )

