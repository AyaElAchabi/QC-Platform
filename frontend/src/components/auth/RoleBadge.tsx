import { UserRole, ROLE_COLORS, ROLE_LABELS } from "@/types/roles";
import { Badge } from "@/components/ui/badge";

interface RoleBadgeProps {
  role: UserRole;
  className?: string;
}

export function RoleBadge({ role, className = "" }: RoleBadgeProps) {
  const colorClass = ROLE_COLORS[role];
  const label = ROLE_LABELS[role];

  return (
    <Badge 
      variant="outline" 
      className={`${colorClass} ${className}`}
    >
      {label}
    </Badge>
  );
}
