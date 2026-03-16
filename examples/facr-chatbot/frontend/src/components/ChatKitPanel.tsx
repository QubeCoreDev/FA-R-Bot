import { ChatKit, useChatKit } from "@openai/chatkit-react";

import type { ColorScheme } from "../hooks/useColorScheme";
import {
  FACR_CHATKIT_API_DOMAIN_KEY,
  FACR_CHATKIT_API_URL,
  FACR_GREETING,
  FACR_PROMPTS,
} from "../lib/config";

type ChatKitPanelProps = {
  theme: ColorScheme;
};

export function ChatKitPanel({ theme }: ChatKitPanelProps) {
  const chatkit = useChatKit({
    api: {
      url: FACR_CHATKIT_API_URL,
      domainKey: FACR_CHATKIT_API_DOMAIN_KEY,
    },
    theme: {
      colorScheme: theme,
      color: {
        grayscale: {
          hue: 220,
          tint: theme === "dark" ? 4 : 7,
          shade: theme === "dark" ? -2 : -3,
        },
        accent: {
          primary: theme === "dark" ? "#60a5fa" : "#003087",
          level: 2,
        },
      },
      radius: "round",
    },
    startScreen: {
      greeting: FACR_GREETING,
      prompts: FACR_PROMPTS,
    },
    composer: {
      placeholder: "Zeptejte se na cokoliv ohledně pravidel FAČR…",
    },
    threadItemActions: {
      feedback: false,
    },
    onError: ({ error }) => {
      console.error("ChatKit error", error);
    },
  });

  return <ChatKit control={chatkit.control} className="block h-full w-full" />;
}
