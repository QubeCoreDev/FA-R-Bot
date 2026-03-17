import type { StartScreenPrompt } from "@openai/chatkit";

export const THEME_STORAGE_KEY = "facr-chatbot-theme";

const FACR_API_BASE = import.meta.env.VITE_FACR_API_BASE ?? "/facr";

export const FACR_CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY ?? "domain_pk_localhost_dev";

export const FACR_CHATKIT_API_URL =
  import.meta.env.VITE_FACR_CHATKIT_API_URL ?? `${FACR_API_BASE}/chatkit`;

export const FACR_GREETING =
  "Ahoj! Jsem Lvíček, tvůj AI průvodce světem českého fotbalu. Znám všechny předpisy, řády a pravidla FAČR – zeptej se mě na cokoliv!";

export const FACR_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Přestupy hráčů",
    prompt:
      "Jaká jsou pravidla pro přestup hráče mezi kluby podle Přestupního řádu FAČR?",
    icon: "document",
  },
  {
    label: "Disciplinární tresty",
    prompt:
      "Jaké druhy disciplinárních trestů existují podle Disciplinárního řádu FAČR?",
    icon: "notebook",
  },
  {
    label: "Fotbaloví agenti",
    prompt:
      "Jaké jsou podmínky pro získání licence fotbalového agenta podle Řádu agentů FAČR?",
    icon: "profile",
  },
  {
    label: "Odměny rozhodčích",
    prompt:
      "Jaké jsou odměny rozhodčích a delegátů podle aktuálního sazebníku FAČR?",
    icon: "sparkle",
  },
];
