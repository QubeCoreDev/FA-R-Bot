import type { ColorScheme } from "../hooks/useColorScheme";

type PitchBackgroundProps = {
  theme: ColorScheme;
};

export function PitchBackground({ theme }: PitchBackgroundProps) {
  const stroke =
    theme === "dark" ? "rgba(0,48,135,0.18)" : "rgba(0,48,135,0.07)";
  const strokeFaint =
    theme === "dark" ? "rgba(0,48,135,0.10)" : "rgba(0,48,135,0.04)";

  return (
    <>
      <div className="pitch-bg" />
      <svg
        className="pitch-lines"
        viewBox="0 0 1000 800"
        preserveAspectRatio="xMidYMid slice"
      >
        <circle
          cx="500"
          cy="400"
          r="120"
          fill="none"
          stroke={stroke}
          strokeWidth="1.5"
        />
        <circle cx="500" cy="400" r="4" fill={stroke} />
        <line
          x1="0"
          y1="400"
          x2="1000"
          y2="400"
          stroke={stroke}
          strokeWidth="1.5"
        />
        <rect
          x="300"
          y="0"
          width="400"
          height="140"
          fill="none"
          stroke={stroke}
          strokeWidth="1.2"
        />
        <rect
          x="380"
          y="0"
          width="240"
          height="55"
          fill="none"
          stroke={strokeFaint}
          strokeWidth="1"
        />
        <path
          d="M 380 140 Q 500 195 620 140"
          fill="none"
          stroke={strokeFaint}
          strokeWidth="1"
        />
        <circle cx="500" cy="110" r="2.5" fill={strokeFaint} />
        <rect
          x="300"
          y="660"
          width="400"
          height="140"
          fill="none"
          stroke={stroke}
          strokeWidth="1.2"
        />
        <rect
          x="380"
          y="745"
          width="240"
          height="55"
          fill="none"
          stroke={strokeFaint}
          strokeWidth="1"
        />
        <path
          d="M 380 660 Q 500 605 620 660"
          fill="none"
          stroke={strokeFaint}
          strokeWidth="1"
        />
        <circle cx="500" cy="690" r="2.5" fill={strokeFaint} />
        <path d="M 0 22 A 22 22 0 0 1 22 0" fill="none" stroke={strokeFaint} strokeWidth="1" />
        <path d="M 978 0 A 22 22 0 0 1 1000 22" fill="none" stroke={strokeFaint} strokeWidth="1" />
        <path d="M 0 778 A 22 22 0 0 0 22 800" fill="none" stroke={strokeFaint} strokeWidth="1" />
        <path d="M 978 800 A 22 22 0 0 0 1000 778" fill="none" stroke={strokeFaint} strokeWidth="1" />
        <rect
          x="2"
          y="2"
          width="996"
          height="796"
          fill="none"
          stroke={stroke}
          strokeWidth="2"
          rx="3"
        />
      </svg>
    </>
  );
}
