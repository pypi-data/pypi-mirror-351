from pathlib import Path
from typing import Any, List, Optional

import logfire
from fastmcp import FastMCP

from stadt_bonn_oparl import __version__ as stadt_bonn_oparl_version
from stadt_bonn_oparl.config import OPARL_BASE_URL, OPARL_PAPERS_ENDPOINT
from stadt_bonn_oparl.logging import configure_logging
from stadt_bonn_oparl.oparl_fetcher import get_oparl_data, get_oparl_list_data
from stadt_bonn_oparl.papers.models import Paper
from stadt_bonn_oparl.processors import download_oparl_pdfs
from stadt_bonn_oparl.utils import extract_id_from_oparl_url

mcp = FastMCP("oparl, Stadt Bonn")


configure_logging(1)

logfire.configure(
    service_name="stadt-bonn-oparl-mcp",
    service_version=stadt_bonn_oparl_version,
)
logfire.instrument_pydantic()
logfire.instrument_mcp()


@mcp.prompt()
def get_paper_summary() -> str:
    """Get the summary of the OParl API"""
    return """schau dir die das paper mit der id 2022736 im allris der stadt bonn an, und gibt mir einen kleinen überblick. gehe vor allem auf die sitzungen ein in denen die durcksache bearbeitet worden ist, und welche personen wichtig sind. nutze deutsche sprache für deine antwort. schreib einen flashy and glossy eilmeldung im stil von spiegel online, ueberpruefe fuer jeden link ob er wirklich erreichbar ist, zB mit `curl`"""


@mcp.resource(
    "data://version",
    name="Version",
    description="Version information for the OParl MCP",
    mime_type="application/json",
)
def get_version() -> dict:
    return {"version": stadt_bonn_oparl_version, "name": "stadt-bonn-oparl-mcp"}


@mcp.resource(
    "oparl://system",
    name="OPARL System der Stadt Bonn, see https://oparl.org/spezifikation/online-ansicht/#entity-system",
    description="Ein oparl:System-Objekt repräsentiert eine OParl-Schnittstelle für eine bestimmte OParl-Version. Es ist außerdem der Startpunkt für Clients beim Zugriff auf einen Server. Die ist das Sysem-Object der Stadt Bonn",
    mime_type="application/json",
)
async def get_system() -> Optional[dict[str, Any]]:
    """Get the system information from the OParl API"""
    return await get_oparl_data("/system")


@mcp.tool(
    "stadt_bonn_oparl_paper_summary",
    annotations={
        "title": "Drucksachenzusammenfassung",
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def stadt_bonn_oparl_paper_summary(paper_id: str) -> Optional[dict[str, Any]]:
    """Generates a summary for a specific Drucksache/Paper in the OParl API, it does not deliver all data, but a summary of the paper"""
    paper_data = await get_paper(paper_id)
    if paper_data:
        # Generate a summary based on the paper data
        summary = {
            "title": paper_data.get("title"),
            "abstract": paper_data.get("abstract"),
            "author": paper_data.get("author"),
        }
        return summary
    return None


@mcp.resource(
    "oparl://paper/{paper_id}/content",
    name="OPARL Paper Content, Allris der Stadt Bonn",
    description="Dieser Objekttyp dient der Abbildung von Inhalten von Drucksachen in der parlamentarischen Arbeit, wie zum Beispiel Anfragen, Anträgen und Beschlussvorlagen.",
    mime_type="application/json",
)
async def get_paper_content(paper_id: str) -> Paper:
    """Get the paper content from the OParl API"""
    oparl_url = f"{OPARL_BASE_URL}{OPARL_PAPERS_ENDPOINT}"
    data_path = Path("data-mcp")
    total_downloads, actual_pdfs, html_pages = download_oparl_pdfs(
        oparl_url,
        start_page=start_page,
        max_pages=max_pages,
        data_path=data_path,
        state_file=state_file,
    )


@mcp.resource(
    "oparl://paper/{paper_id}",
    name="OPARL Paper, Allris der Stadt Bonn",
    description="Dieser Objekttyp dient der Abbildung von Drucksachen in der parlamentarischen Arbeit, wie zum Beispiel Anfragen, Anträgen und Beschlussvorlagen. Drucksachen werden in Form einer Beratung (oparl:Consultation) im Rahmen eines Tagesordnungspunkts (oparl:AgendaItem) einer Sitzung (oparl:Meeting) behandelt.",
    mime_type="application/json",
)
async def get_paper(paper_id: str) -> Optional[dict[str, Any]]:
    """Get the paper information from the OParl API"""
    return await get_oparl_data("/papers", params={"id": paper_id})


@mcp.resource(
    "oparl://papers/last_20",
    name="OPARL last 20 Papers, Allris der Stadt Bonn",
    description="Die letzen/aktuellsten 20 Drucksachen, der Objekttyp Drucksache dient der Abbildung von Drucksachen in der parlamentarischen Arbeit, wie zum Beispiel Anfragen, Anträgen und Beschlussvorlagen. Drucksachen werden in Form einer Beratung (oparl:Consultation) im Rahmen eines Tagesordnungspunkts (oparl:AgendaItem) einer Sitzung (oparl:Meeting) behandelt.",
    mime_type="application/json",
)
async def get_last_20_papers() -> Optional[List[str]]:
    """Get the IDs of the last 20 papers from the OParl API"""
    papers_data = await get_oparl_list_data("/papers")

    if papers_data:
        paper_ids: List[str] = []
        for paper_item in papers_data:
            if isinstance(paper_item, dict) and "id" in paper_item:
                extracted_id = extract_id_from_oparl_url(paper_item["id"])
                if extracted_id:
                    paper_ids.append(extracted_id)
        return paper_ids
    return None


@mcp.resource(
    "oparl://person/{person_id}",
    name="OPARL Person, Allris der Stadt Bonn",
    description="Dieser Objekttyp dient der Abbildung von Personen in der parlamentarischen Arbeit, wie zum Beispiel Ratsmitgliedern, Bürgern und Mitarbeitern.",
    mime_type="application/json",
)
async def get_person(person_id: str) -> Optional[dict[str, Any]]:
    """Get the person information from the OParl API"""
    return await get_oparl_data("/persons", params={"id": person_id})


@mcp.resource(
    "oparl://consultation/{consultation_id}",
    name="OPARL Consultation, Allris der Stadt Bonn",
    description="Der Objekttyp oparl:Consultation dient dazu, die Beratung einer Drucksache (oparl:Paper) in einer Sitzung abzubilden. Dabei ist es nicht entscheidend, ob diese Beratung in der Vergangenheit stattgefunden hat oder diese für die Zukunft geplant ist. Die Gesamtheit aller Objekte des Typs oparl:Consultation zu einer bestimmten Drucksache bildet das ab, was in der Praxis als “Beratungsfolge” der Drucksache bezeichnet wird.",
    mime_type="application/json",
)
async def get_consultation(consultation_id: str) -> Optional[dict[str, Any]]:
    """Get the consultation information from the OParl API"""
    return await get_oparl_data("/consultations", params={"id": consultation_id})


@mcp.resource(
    "oparl://meeting/{meeting_id}",
    name="OPARL Meeting, Allris der Stadt Bonn",
    description="Eine Sitzung ist die Versammlung einer oder mehrerer Gruppierungen (oparl:Organization) zu einem bestimmten Zeitpunkt an einem bestimmten Ort. Die geladenen Teilnehmer der Sitzung sind jeweils als Objekte vom Typ oparl:Person, die in entsprechender Form referenziert werden. Verschiedene Dateien (Einladung, Ergebnis- und Wortprotokoll, sonstige Anlagen) können referenziert werden. Die Inhalte einer Sitzung werden durch Tagesordnungspunkte (oparl:AgendaItem) abgebildet.",
    mime_type="application/json",
)
async def get_meeting(meeting_id: str) -> Optional[dict[str, Any]]:
    """Get the meeting information from the OParl API"""
    return await get_oparl_data("/meetings", params={"id": meeting_id})


@mcp.resource(
    "oparl://agenda_item/{agenda_item_id}",
    name="OPARL Agenda Item, Allris der Stadt Bonn",
    description="Tagesordnungspunkte sind die Bestandteile von Sitzungen (oparl:Meeting). Jeder Tagesordnungspunkt widmet sich inhaltlich einem bestimmten Thema, wozu in der Regel auch die Beratung bestimmter Drucksachen gehört. Die Beziehung zwischen einem Tagesordnungspunkt und einer Drucksache wird über ein Objekt vom Typ oparl:Consultation hergestellt, das über die Eigenschaft consultation referenziert werden kann.",
    mime_type="application/json",
)
async def get_agenda_item(agenda_item_id: str) -> Optional[dict[str, Any]]:
    """Get the agenda item information from the OParl API"""
    return await get_oparl_data("/agendaItems", params={"id": agenda_item_id})


@mcp.resource(
    "oparl://organization/{organization_id}",
    name="OPARL Organization, Allris der Stadt Bonn",
    description="Dieser Objekttyp dient dazu, Gruppierungen von Personen abzubilden, die in der parlamentarischen Arbeit eine Rolle spielen. Dazu zählen in der Praxis insbesondere Fraktionen und Gremien.",
    mime_type="application/json",
)
async def get_organization(organization_id: str) -> Optional[dict[str, Any]]:
    """Get the organization information from the OParl API"""
    return await get_oparl_data(
        "/organizations", params={"id": organization_id, "typ": "gr"}
    )


@mcp.tool(
    "stadt_bonn_oparl_organization",
    annotations={
        "title": "Organisation der Stadt Bonn",
        "readOnlyHint": True,
        "openWorldHint": True,
    },
)
async def stadt_bonn_oparl_organization_summary(
    organization_id: str,
) -> Optional[dict[str, Any]]:
    """Generates a summary for a specific Organisation in the OParl API, it does not deliver all data, but a summary of the organization"""
    organization_data = await get_organization(organization_id)
    if organization_data:
        summary = {
            "title": organization_data.get("title"),
            "abstract": organization_data.get("abstract"),
            "author": organization_data.get("author"),
        }
        return summary
    return None
