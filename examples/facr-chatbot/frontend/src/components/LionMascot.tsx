type LionMascotProps = {
  size?: number;
  className?: string;
};

export function LionMascot({ size = 120, className = "" }: LionMascotProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 200 200"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="maneGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#d4a843" />
          <stop offset="100%" stopColor="#b8892a" />
        </linearGradient>
        <linearGradient id="faceGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#f5c842" />
          <stop offset="100%" stopColor="#e6b530" />
        </linearGradient>
        <linearGradient id="noseGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#c9703a" />
          <stop offset="100%" stopColor="#a85a2a" />
        </linearGradient>
      </defs>

      {/* Mane */}
      <ellipse cx="100" cy="88" rx="62" ry="58" fill="url(#maneGrad)" />
      <ellipse cx="52" cy="60" rx="18" ry="16" fill="#c9973a" />
      <ellipse cx="148" cy="60" rx="18" ry="16" fill="#c9973a" />
      <ellipse cx="40" cy="82" rx="14" ry="15" fill="#c9973a" />
      <ellipse cx="160" cy="82" rx="14" ry="15" fill="#c9973a" />
      <ellipse cx="55" cy="110" rx="12" ry="13" fill="#b8892a" />
      <ellipse cx="145" cy="110" rx="12" ry="13" fill="#b8892a" />

      {/* Face */}
      <ellipse cx="100" cy="92" rx="45" ry="42" fill="url(#faceGrad)" />

      {/* Ears */}
      <ellipse cx="62" cy="56" rx="14" ry="13" fill="#e6b530" />
      <ellipse cx="62" cy="56" rx="9" ry="8" fill="#f0c8a0" />
      <ellipse cx="138" cy="56" rx="14" ry="13" fill="#e6b530" />
      <ellipse cx="138" cy="56" rx="9" ry="8" fill="#f0c8a0" />

      {/* Eyes */}
      <ellipse cx="82" cy="82" rx="10" ry="11" fill="white" />
      <ellipse cx="118" cy="82" rx="10" ry="11" fill="white" />
      <circle cx="84" cy="83" r="6" fill="#2c1810" />
      <circle cx="120" cy="83" r="6" fill="#2c1810" />
      <circle cx="86" cy="80" r="2.5" fill="white" />
      <circle cx="122" cy="80" r="2.5" fill="white" />

      {/* Eyebrows */}
      <path d="M72 72 Q82 67 92 72" stroke="#a85a2a" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      <path d="M108 72 Q118 67 128 72" stroke="#a85a2a" strokeWidth="2.5" strokeLinecap="round" fill="none" />

      {/* Muzzle */}
      <ellipse cx="100" cy="100" rx="18" ry="14" fill="#f0d8a8" />

      {/* Nose */}
      <ellipse cx="100" cy="95" rx="8" ry="5.5" fill="url(#noseGrad)" />
      <ellipse cx="100" cy="93.5" rx="4" ry="2" fill="#d47a42" opacity="0.5" />

      {/* Mouth */}
      <path d="M100 100.5 L100 105" stroke="#a85a2a" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M92 106 Q100 112 108 106" stroke="#a85a2a" strokeWidth="2" strokeLinecap="round" fill="none" />

      {/* Whiskers */}
      <line x1="60" y1="95" x2="78" y2="98" stroke="#c9973a" strokeWidth="1.2" opacity="0.5" />
      <line x1="58" y1="102" x2="77" y2="102" stroke="#c9973a" strokeWidth="1.2" opacity="0.5" />
      <line x1="122" y1="98" x2="140" y2="95" stroke="#c9973a" strokeWidth="1.2" opacity="0.5" />
      <line x1="123" y1="102" x2="142" y2="102" stroke="#c9973a" strokeWidth="1.2" opacity="0.5" />

      {/* Crown */}
      <path
        d="M76 48 L80 32 L90 42 L100 28 L110 42 L120 32 L124 48 Z"
        fill="#d4a843"
        stroke="#b8892a"
        strokeWidth="1.5"
      />
      <circle cx="90" cy="40" r="2" fill="#ED1C24" />
      <circle cx="100" cy="32" r="2.5" fill="#003087" />
      <circle cx="110" cy="40" r="2" fill="#ED1C24" />

      {/* Football at paw level */}
      <circle cx="145" cy="140" r="18" fill="white" stroke="#ccc" strokeWidth="1" />
      <path d="M145 122 L145 158" stroke="#ddd" strokeWidth="0.8" />
      <path d="M127 140 L163 140" stroke="#ddd" strokeWidth="0.8" />
      <polygon
        points="145,130 150,136 148,143 142,143 140,136"
        fill="#003087"
        opacity="0.6"
      />
      <polygon
        points="152,137 157,142 155,148 150,145 150,138"
        fill="#003087"
        opacity="0.3"
      />
      <polygon
        points="138,137 133,142 135,148 140,145 140,138"
        fill="#003087"
        opacity="0.3"
      />

      {/* Paw reaching for ball */}
      <ellipse cx="130" cy="135" rx="10" ry="6" fill="#e6b530" transform="rotate(-20, 130, 135)" />

      {/* Cheek blush */}
      <ellipse cx="74" cy="96" rx="7" ry="4" fill="#f0a0a0" opacity="0.3" />
      <ellipse cx="126" cy="96" rx="7" ry="4" fill="#f0a0a0" opacity="0.3" />

      {/* Czech flag ribbon around neck */}
      <path d="M65 120 Q100 132 135 120" stroke="white" strokeWidth="5" fill="none" strokeLinecap="round" />
      <path d="M65 120 Q100 132 135 120" stroke="#ED1C24" strokeWidth="5" fill="none" strokeLinecap="round"
        strokeDasharray="12 5" strokeDashoffset="3" opacity="0.7" />
      <path d="M65 123 Q100 135 135 123" stroke="#003087" strokeWidth="2.5" fill="none" strokeLinecap="round" opacity="0.6" />
    </svg>
  );
}
