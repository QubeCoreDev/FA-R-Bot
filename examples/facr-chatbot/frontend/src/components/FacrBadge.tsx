import facrLogo from "../assets/facr-logo.png";

type FacrBadgeProps = {
  size?: number;
};

export function FacrBadge({ size = 44 }: FacrBadgeProps) {
  return (
    <img
      src={facrLogo}
      alt="FAČR – Fotbalová asociace České republiky"
      width={size}
      height={size}
      className="badge-shield"
      draggable={false}
      style={{ objectFit: "contain" }}
    />
  );
}
