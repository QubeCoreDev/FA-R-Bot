type Props = {
  className?: string;
};

export function FootballDecorations({ className = "" }: Props) {
  return (
    <div className={`football-decorations ${className}`} aria-hidden="true">
      <svg className="deco-ball deco-ball-1" width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="11" fill="white" stroke="#ccc" strokeWidth="0.5" />
        <polygon points="12,5 14,9 12,12 10,9" fill="#003087" opacity="0.5" />
        <polygon points="16,10 18,13 16,15 14,13" fill="#003087" opacity="0.3" />
        <polygon points="8,10 6,13 8,15 10,13" fill="#003087" opacity="0.3" />
      </svg>
      <svg className="deco-ball deco-ball-2" width="18" height="18" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="11" fill="white" stroke="#ccc" strokeWidth="0.5" />
        <polygon points="12,5 14,9 12,12 10,9" fill="#ED1C24" opacity="0.5" />
        <polygon points="16,10 18,13 16,15 14,13" fill="#ED1C24" opacity="0.3" />
      </svg>
      <svg className="deco-ball deco-ball-3" width="14" height="14" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="11" fill="white" stroke="#ccc" strokeWidth="0.5" />
        <polygon points="12,5 14,9 12,12 10,9" fill="#003087" opacity="0.4" />
      </svg>
    </div>
  );
}
