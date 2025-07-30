from pathlib import Path
from cyclopts import App
import logfire
from loguru import logger
from pydantic import DirectoryPath

from stadt_bonn_oparl.config import OPARL_BASE_URL, OPARL_PAPERS_ENDPOINT
from stadt_bonn_oparl.processors import download_oparl_pdfs


download = App(name="download", help="Download OPARL artifacts")


@download.command(name="paper")
def download_paper(
    data_path: DirectoryPath,
    start_page: int = 1,
    max_pages: int = 2,
    state_file: Path | None = None,
) -> bool:
    """
    Process OParl data and download PDFs.

    Parameters
    ----------
    data_path: DirectoryPath
        Path to the directory where OParl data will be saved.
    start_page: int
        The page number to start downloading from.
    max_pages: int
        The maximum number of pages to download.
    state_file: Path | None
        Optional path to a state file.
    """
    logger.info("Starting OParl data processing...")

    oparl_url = f"{OPARL_BASE_URL}{OPARL_PAPERS_ENDPOINT}"

    logger.debug(
        f"Downloading OParl data from {oparl_url}, starting at page {start_page} and ending after {max_pages} pages at {start_page+max_pages}..."
    )
    with logfire.span(f"downloading OParl data from {oparl_url}"):
        total_downloads, actual_pdfs, html_pages = download_oparl_pdfs(
            oparl_url,
            start_page=start_page,
            max_pages=max_pages,
            data_path=data_path,
            state_file=state_file,
        )

    logger.info(
        f"OParl processing finished. Downloaded {total_downloads} files: "
        f"{actual_pdfs} actual PDFs, {html_pages} HTML pages"
    )

    if html_pages > 0 and actual_pdfs == 0:
        logger.warning(
            "No actual PDFs were downloaded. The documents appear to be behind an authentication wall. "
            "You may need to obtain access credentials to download the actual PDFs."
        )

    return True
