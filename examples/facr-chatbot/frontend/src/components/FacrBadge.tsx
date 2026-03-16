type FacrBadgeProps = {
  size?: number;
};

export function FacrBadge({ size = 48 }: FacrBadgeProps) {
  return (
    <svg
      className="badge-shield"
      width={size}
      height={size}
      viewBox="0 0 52 52"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Outer glow */}
      <defs>
        <linearGradient id="shieldGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#1a4a9e" />
          <stop offset="100%" stopColor="#001f5c" />
        </linearGradient>
        <linearGradient id="redGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ED1C24" />
          <stop offset="100%" stopColor="#c41820" />
        </linearGradient>
      </defs>

      {/* Shield outline */}
      <path
        d="M26 3L7 11V24C7 35 15 43 26 47C37 43 45 35 45 24V11L26 3Z"
        fill="url(#shieldGrad)"
        stroke="rgba(255,255,255,0.5)"
        strokeWidth="1"
      />

      {/* Red bottom half */}
      <path
        d="M26 47C15 43 7 35 7 24V23H45V24C45 35 37 43 26 47Z"
        fill="url(#redGrad)"
      />

      {/* White divider */}
      <line
        x1="7"
        y1="23"
        x2="45"
        y2="23"
        stroke="white"
        strokeWidth="1.2"
        opacity="0.8"
      />

      {/* Football */}
      <circle cx="26" cy="17" r="6.5" fill="white" />
      <circle cx="26" cy="17" r="6.5" fill="none" stroke="#ccc" strokeWidth="0.3" />

      {/* Pentagon pattern */}
      <polygon
        points="26,12.5 28,14.5 27.3,17 24.7,17 24,14.5"
        fill="#003087"
        opacity="0.65"
      />
      {/* Hex segments */}
      <polygon
        points="29,15 30,17.5 28.8,19.5 27.3,17.5 28,15"
        fill="#003087"
        opacity="0.35"
      />
      <polygon
        points="23,15 24,14.5 24.7,17 23.2,19.5 22,17.5"
        fill="#003087"
        opacity="0.35"
      />
      <polygon
        points="24.7,17.5 27.3,17.5 28,20 26,21.5 24,20"
        fill="#003087"
        opacity="0.35"
      />

      {/* FAČR text */}
      <text
        x="26"
        y="36"
        textAnchor="middle"
        fill="white"
        fontSize="7.5"
        fontFamily="Barlow Condensed, sans-serif"
        fontWeight="800"
        letterSpacing="1.2"
      >
        FAČR
      </text>

      {/* Subtle top shine */}
      <path
        d="M26 3L7 11V15C16 11 36 11 45 15V11L26 3Z"
        fill="white"
        opacity="0.1"
      />

      {/* Gold rim at bottom of shield */}
      <path
        d="M26 47C15 43 7 35 7 24"
        fill="none"
        stroke="#c9a84c"
        strokeWidth="0.5"
        opacity="0.4"
      />
      <path
        d="M26 47C37 43 45 35 45 24"
        fill="none"
        stroke="#c9a84c"
        strokeWidth="0.5"
        opacity="0.4"
      />
    </svg>
  );
}
