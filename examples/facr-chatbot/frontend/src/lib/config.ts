import type { StartScreenPrompt } from "@openai/chatkit";

export const THEME_STORAGE_KEY = "facr-chatbot-theme";

const FACR_API_BASE = import.meta.env.VITE_FACR_API_BASE ?? "/facr";

export const FACR_CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY ?? "domain_pk_localhost_dev";

export const FACR_CHATKIT_API_URL =
  import.meta.env.VITE_FACR_CHATKIT_API_URL ?? `${FACR_API_BASE}/chatkit`;

export const FACR_GREETING =
  "Dobrý den! Jsem AI asistent FAČR. Pomohu vám s otázkami ohledně pravidel, předpisů a řádů českého fotbalu.";

export const FACR_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Pravidla přestupů hráčů",
    prompt:
      "Jaká jsou pravidla pro přestup hráče mezi kluby podle Přestupního řádu FAČR?",
    icon: "document",
  },
  {
    label: "Disciplinární řízení",
    prompt:
      "Jaké druhy disciplinárních trestů existují podle Disciplinárního řádu FAČR a jaký je postup při disciplinárním řízení?",
    icon: "notebook",
  },
  {
    label: "Licence fotbalového agenta",
    prompt:
      "Jaké jsou podmínky pro získání licence fotbalového agenta podle Řádu agentů FAČR?",
    icon: "profile",
  },
  {
    label: "Sazebník odměn rozhodčích",
    prompt:
      "Jaké jsou odměny rozhodčích a delegátů v první a druhé lize podle aktuálního sazebníku odměn FAČR?",
    icon: "sparkle",
  },
];
