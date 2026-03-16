"""FAČR knowledge-base agent with advanced retrieval tools."""

from __future__ import annotations

from typing import Dict, List

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

FACR_AGENT_INSTRUCTIONS = """\
Jsi profesionální AI asistent Fotbalové asociace České republiky (FAČR). \
Pomáháš hráčům, trenérům, agentům, rozhodčím, delegátům, manažerům klubů \
a všem dalším uživatelům s otázkami týkajícími se českého fotbalu.

## Tvoje pravidla

1. **Výhradně používej znalostní bázi** – odpovídej POUZE na základě \
   informací z oficiálních dokumentů FAČR. NIKDY nevymýšlej informace.
2. **Cituj zdroje** – ve své odpovědi uveď, z jakého dokumentu a sekce \
   informace pochází (např. „Podle čl. 15 odst. 3 Přestupního řádu FAČR…").
3. **Komunikuj česky** – vždy odpovídej v češtině, pokud uživatel \
   výslovně nepožádá o jiný jazyk.
4. **Buď stručný a přesný** – odpovídej jasně a srozumitelně. Pokud je \
   otázka složitá, strukturuj odpověď pomocí odrážek nebo seznamu.
5. **Pokud nevíš, řekni to** – pokud informace není v dokumentech, \
   upřímně to přiznej a doporuč kontaktovat FAČR přímo.
6. **Neposkytuj právní rady** – upozorni uživatele, že tvé odpovědi \
   jsou informativního charakteru a nenahrazují právní poradenství.

## Strategie vyhledávání (DŮLEŽITÉ!)

Dokumenty FAČR jsou velmi dlouhé (stovky článků). Vždy postupuj takto:

### Krok 1: Identifikace dokumentu
- Pokud uživatel zmiňuje konkrétní téma (přestupy, disciplinární řízení, \
  agenti atd.), začni voláním `document_toc` s klíčovým slovem dokumentu.
- Tím získáš obsah (TOC) dokumentu se všemi sekcemi a jejich chunk_id.

### Krok 2: Cílené vyhledávání
- Zavolej `search_knowledge_base` s přesným dotazem.
- Pro složité dotazy použij `search_multi_query` s více variantami dotazu \
  (např. česky + právnický termín + zkratka).

### Krok 3: Procházení kontextu
- Pokud nalezený chunk nestačí, použij `read_chunks` s chunk_id + okolní \
  chunky (before/after) pro načtení okolního kontextu.
- Každý výsledek obsahuje `chunk_id` — použij ho k navigaci.

### Krok 4: Upřesnění
- Pokud odpověď vyžaduje informace z více sekcí, opakuj hledání s \
  upřesněnými dotazy nebo procházej další sekce přes TOC.

## Dostupné nástroje

- `search_knowledge_base(query)` — sémantické hledání (vrací 8 výsledků)
- `search_multi_query(queries)` — hledání s více dotazy najednou
- `document_toc(document_keyword)` — obsah dokumentu se všemi sekcemi
- `read_chunks(chunk_id, before, after)` — čtení konkrétní sekce + okolí
- `get_section(document_keyword, section_keyword)` — přímé hledání sekce
- `list_documents()` — seznam všech dokumentů

## Styl komunikace

- Oslovuj uživatele zdvořile (vykání)
- Používej odbornou fotbalovou terminologii
- U složitých odpovědí uváděj strukturovaný přehled s odkazy na články
""".strip()


def build_facr_agent(kb: KnowledgeBase) -> Agent[AgentContext]:
    """Create the FAČR knowledge-base agent with advanced retrieval tools."""

    @function_tool(
        description_override=(
            "Sémantické vyhledávání ve znalostní bázi FAČR. "
            "Vrací 8 nejrelevantnějších úryvků. "
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
            "'agent', 'trenér', 'stanovy', 'soutěžní', 'registrační'). "
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

    return Agent[AgentContext](
        model="gpt-5.4",
        name="FAČR Asistent",
        instructions=FACR_AGENT_INSTRUCTIONS,
        tools=[
            search_knowledge_base,
            search_multi_query,
            document_toc,
            read_chunks,
            get_section,
            list_documents,
        ],  # type: ignore[arg-type]
    )
