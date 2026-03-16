import type { ColorScheme } from "../hooks/useColorScheme";

type PitchBackgroundProps = {
  theme: ColorScheme;
};

export function PitchBackground({ theme }: PitchBackgroundProps) {
  const stroke =
    theme === "dark" ? "rgba(59,130,246,0.12)" : "rgba(0,48,135,0.10)";
  const strokeLight =
    theme === "dark" ? "rgba(59,130,246,0.06)" : "rgba(0,48,135,0.05)";

  return (
    <>
      <div className="pitch-bg" />
      <svg
        className="pitch-lines"
        viewBox="0 0 1000 800"
        preserveAspectRatio="xMidYMid slice"
      >
        {/* Center circle */}
        <circle
          cx="500"
          cy="400"
          r="120"
          fill="none"
          stroke={stroke}
          strokeWidth="2"
        />
        {/* Center dot */}
        <circle cx="500" cy="400" r="5" fill={stroke} />
        {/* Halfway line */}
        <line
          x1="0"
          y1="400"
          x2="1000"
          y2="400"
          stroke={stroke}
          strokeWidth="2"
        />
        {/* Top penalty box */}
        <rect
          x="300"
          y="0"
          width="400"
          height="140"
          fill="none"
          stroke={stroke}
          strokeWidth="1.5"
        />
        {/* Top goal box */}
        <rect
          x="380"
          y="0"
          width="240"
          height="55"
          fill="none"
          stroke={strokeLight}
          strokeWidth="1.2"
        />
        {/* Top penalty arc */}
        <path
          d="M 380 140 Q 500 195 620 140"
          fill="none"
          stroke={strokeLight}
          strokeWidth="1.2"
        />
        {/* Top penalty spot */}
        <circle cx="500" cy="110" r="3" fill={strokeLight} />
        {/* Bottom penalty box */}
        <rect
          x="300"
          y="660"
          width="400"
          height="140"
          fill="none"
          stroke={stroke}
          strokeWidth="1.5"
        />
        {/* Bottom goal box */}
        <rect
          x="380"
          y="745"
          width="240"
          height="55"
          fill="none"
          stroke={strokeLight}
          strokeWidth="1.2"
        />
        {/* Bottom penalty arc */}
        <path
          d="M 380 660 Q 500 605 620 660"
          fill="none"
          stroke={strokeLight}
          strokeWidth="1.2"
        />
        {/* Bottom penalty spot */}
        <circle cx="500" cy="690" r="3" fill={strokeLight} />
        {/* Corner arcs */}
        <path
          d="M 0 25 A 25 25 0 0 1 25 0"
          fill="none"
          stroke={stroke}
          strokeWidth="1.2"
        />
        <path
          d="M 975 0 A 25 25 0 0 1 1000 25"
          fill="none"
          stroke={stroke}
          strokeWidth="1.2"
        />
        <path
          d="M 0 775 A 25 25 0 0 0 25 800"
          fill="none"
          stroke={stroke}
          strokeWidth="1.2"
        />
        <path
          d="M 975 800 A 25 25 0 0 0 1000 775"
          fill="none"
          stroke={stroke}
          strokeWidth="1.2"
        />
        {/* Outer boundary */}
        <rect
          x="2"
          y="2"
          width="996"
          height="796"
          fill="none"
          stroke={stroke}
          strokeWidth="2.5"
          rx="3"
        />
      </svg>
    </>
  );
}
