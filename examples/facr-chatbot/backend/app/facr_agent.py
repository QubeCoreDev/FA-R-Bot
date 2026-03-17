"""FAČR knowledge-base agent with advanced retrieval and web tools."""

from __future__ import annotations

from typing import Any, Dict, List

from agents import Agent, RunContextWrapper, function_tool
from chatkit.agents import AgentContext

from .knowledge_base import (
    KnowledgeBase,
    format_chunks,
    format_document_list,
    format_search_results,
    format_toc,
    get_document_section,
    get_document_toc,
    read_chunk_with_neighbors,
    search,
    search_multi,
)
from .web_tools import fetch_facr_page, search_facr_web

FACR_AGENT_INSTRUCTIONS = """\
Jsi Lvíček – AI průvodce českým fotbalem od FAČR. Lev je symbolem \
českého fotbalu. Odpovídáš česky, přátelsky a stručně.

## Pravidla
- Odpovídej VÝHRADNĚ z KB dokumentů nebo webu FAČR. Nevymýšlej.
- Cituj zdroj (dokument, článek, odstavec).
- Buď stručný. Složité odpovědi strukturuj odrážkami.
- Pokud nevíš → přiznej a doporuč kontaktovat FAČR.
- Nenahrazuješ právní poradenství.

## Jak hledat (RYCHLE!)
1. **Začni JEDNÍM voláním `search_knowledge_base`** s výstižným dotazem.
2. Pokud výsledky stačí → IHNED odpověz. Nevolej další nástroje zbytečně.
3. Pouze pokud výsledky nestačí → použij `read_chunks` pro širší kontext \
   nebo `search_multi_query` pro jiné formulace.
4. Pro kontakty: hledej v KB „kontakt + téma". Pouze pokud nenajdeš, \
   použij `browse_facr_website` s URL „/facr/kontakty/p68".
5. Web nástroje (`browse/search_facr_website`) používej jen když KB nestačí.

## Styl
- Přátelsky, profesionálně, česky. Tykej/vykej dle kontextu.
- Představuj se jako Lvíček.
- Kontakty uváděj přehledně: jméno, pozice, e-mail, telefon.
""".strip()


def build_facr_agent(kb: KnowledgeBase) -> Agent[AgentContext]:
    """Create the FAČR knowledge-base agent with retrieval and web tools."""

    @function_tool(
        description_override=(
            "Sémantické vyhledávání ve znalostní bázi FAČR (dokumenty, řády, "
            "předpisy, kontakty). Vrací 8 nejrelevantnějších úryvků. "
            "Každý výsledek obsahuje chunk_id pro další navigaci."
        ),
    )
    async def search_knowledge_base(
        ctx: RunContextWrapper[AgentContext],
        query: str,
    ) -> Dict[str, str]:
        results = search(kb, query, top_k=8)
        return {"results": format_search_results(results)}

    @function_tool(
        description_override=(
            "Vyhledávání s více dotazy najednou – užitečné pro složité otázky. "
            "Zadej 2–4 varianty dotazu (např. různá formulace, synonyma, "
            "odborné termíny). Výsledky se sloučí a deduplikují."
        ),
    )
    async def search_multi_query(
        ctx: RunContextWrapper[AgentContext],
        queries: List[str],
    ) -> Dict[str, str]:
        results = search_multi(kb, queries, top_k=8)
        return {"results": format_search_results(results)}

    @function_tool(
        description_override=(
            "Vrátí obsah (table of contents) konkrétního dokumentu FAČR. "
            "Zadej klíčové slovo dokumentu (např. 'přestupní', 'disciplinární', "
            "'agent', 'trenér', 'stanovy', 'soutěžní', 'registrační', 'kontakt'). "
            "Výsledek obsahuje seznam všech sekcí s chunk_id pro navigaci."
        ),
    )
    async def document_toc(
        ctx: RunContextWrapper[AgentContext],
        document_keyword: str,
    ) -> Dict[str, str]:
        doc = get_document_toc(kb, document_keyword)
        if doc is None:
            available = format_document_list(kb)
            return {"result": f"Dokument nenalezen. {available}"}
        return {"result": format_toc(doc)}

    @function_tool(
        description_override=(
            "Přečte konkrétní chunk podle chunk_id včetně okolních sekcí. "
            "Parametry 'before' a 'after' určují kolik okolních chunků "
            "načíst (výchozí: 1 před + 2 za). Použij pro procházení "
            "dlouhých dokumentů po sekcích."
        ),
    )
    async def read_chunks(
        ctx: RunContextWrapper[AgentContext],
        chunk_id: int,
        before: int = 1,
        after: int = 2,
    ) -> Dict[str, str]:
        chunks = read_chunk_with_neighbors(kb, chunk_id, before=before, after=after)
        if not chunks:
            return {"result": f"Chunk {chunk_id} neexistuje."}
        return {"result": format_chunks(chunks)}

    @function_tool(
        description_override=(
            "Hledá sekci dokumentu podle klíčových slov pro název dokumentu "
            "a název sekce. Vhodné pokud znáš přesný název sekce."
        ),
    )
    async def get_section(
        ctx: RunContextWrapper[AgentContext],
        document_keyword: str,
        section_keyword: str,
    ) -> Dict[str, str]:
        chunks = get_document_section(kb, document_keyword, section_keyword)
        if not chunks:
            return {"result": "Sekce nebyla nalezena. Zkuste jiná klíčová slova."}
        return {"result": format_chunks(chunks)}

    @function_tool(
        description_override="Vrátí seznam všech dokumentů ve znalostní bázi FAČR s počty sekcí.",
    )
    async def list_documents(
        ctx: RunContextWrapper[AgentContext],
    ) -> Dict[str, str]:
        return {"documents": format_document_list(kb)}

    @function_tool(
        description_override=(
            "Načte stránku z oficiálního webu FAČR (fotbal.cz). "
            "Zadej URL cestu jako '/facr/kontakty/p68' pro kontakty, "
            "'/facr/organizacni-struktura-a-organy-facr' pro strukturu, "
            "'/facr/pravni-servis/predpisy/soubor-predpisu' pro předpisy, "
            "nebo celou URL začínající 'https://www.fotbal.cz/...'. "
            "Vrací textový obsah stránky a seznam odkazů. "
            "POUŽÍVEJ pro kontakty, aktuální organizační info, nebo "
            "když uživatel odkazuje na konkrétní stránku fotbal.cz."
        ),
    )
    async def browse_facr_website(
        ctx: RunContextWrapper[AgentContext],
        url: str,
    ) -> Dict[str, Any]:
        return await fetch_facr_page(url)

    @function_tool(
        description_override=(
            "Vyhledá relevantní stránku na webu FAČR (fotbal.cz) podle "
            "klíčového slova. Vhodné pro hledání kontaktů, organizační "
            "struktury, aktualit, předpisů, reprezentace atd. "
            "Příklady: 'kontakty', 'předpisy', 'výkonný výbor', 'komise', "
            "'přestupy', 'vstupenky', 'reprezentace', 'integrity'."
        ),
    )
    async def search_facr_website(
        ctx: RunContextWrapper[AgentContext],
        query: str,
    ) -> Dict[str, Any]:
        return await search_facr_web(query)

    return Agent[AgentContext](
        model="gpt-5.4",
        name="Lvíček",
        instructions=FACR_AGENT_INSTRUCTIONS,
        tools=[
            search_knowledge_base,
            search_multi_query,
            document_toc,
            read_chunks,
            get_section,
            list_documents,
            browse_facr_website,
            search_facr_website,
        ],  # type: ignore[arg-type]
    )
