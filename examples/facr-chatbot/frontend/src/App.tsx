import { Moon, Sun } from "lucide-react";

import { ChatKitPanel } from "./components/ChatKitPanel";
import { FacrBadge } from "./components/FacrBadge";
import { FootballDecorations } from "./components/FootballDecorations";
import { PitchBackground } from "./components/PitchBackground";
import { useColorScheme } from "./hooks/useColorScheme";

export default function App() {
  const { scheme, toggle } = useColorScheme();

  return (
    <div className="app-shell">
      <PitchBackground theme={scheme} />
      <div className="app-card">
        <header className="app-header">
          <div className="header-content">
            <div className="facr-badge">
              <FacrBadge size={44} />
            </div>
            <div className="header-text">
              <div className="app-title">
                <span className="title-lion">Lvíček</span>
                <span className="title-separator">|</span>
                <span className="title-facr">FAČR</span>
              </div>
              <div className="app-subtitle">
                AI Průvodce českým fotbalem
              </div>
            </div>
          </div>
          <FootballDecorations className="header-deco" />
          <div className="header-actions">
            <button
              className="theme-toggle-btn"
              onClick={toggle}
              aria-label={
                scheme === "dark"
                  ? "Přepnout na světlý režim"
                  : "Přepnout na tmavý režim"
              }
            >
              {scheme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
            </button>
          </div>
        </header>
        <div className="chat-container">
          <ChatKitPanel theme={scheme} />
        </div>
        <footer className="app-footer">
          <span className="footer-lion-paw">🦁</span>
          <span className="footer-text">
            Lvíček – oficiální AI asistent{" "}
            <a
              href="https://facr.fotbal.cz"
              target="_blank"
              rel="noopener noreferrer"
              className="footer-link"
            >
              FAČR
            </a>{" "}
            &middot; Odpovědi vychází z oficiálních dokumentů
          </span>
          <span className="footer-ball">⚽</span>
        </footer>
      </div>
    </div>
  );
}
