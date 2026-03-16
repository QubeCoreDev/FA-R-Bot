import { Moon, Sun } from "lucide-react";

import { ChatKitPanel } from "./components/ChatKitPanel";
import { FacrBadge } from "./components/FacrBadge";
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
              <FacrBadge size={48} />
            </div>
            <div className="header-text">
              <div className="app-title">FAČR Asistent</div>
              <div className="app-subtitle">
                Fotbalová asociace České republiky
              </div>
            </div>
          </div>
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
          <span className="footer-dot" />
          <span className="footer-text">
            Oficiální AI asistent{" "}
            <a
              href="https://facr.fotbal.cz"
              target="_blank"
              rel="noopener noreferrer"
              className="footer-link"
            >
              FAČR
            </a>{" "}
            &middot; Odpovědi vychází z oficiálních dokumentů a řádů
          </span>
          <span className="footer-dot" />
        </footer>
      </div>
    </div>
  );
}
