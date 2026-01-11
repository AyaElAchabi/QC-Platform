"use client";

import { ReactNode } from "react";
import { useAuth } from "@/lib/hooks/useAuth";
import { UserRole, Permission } from "@/types/roles";

interface PermissionGateProps {
  children: ReactNode;
  roles?: UserRole[];
  permissions?: Permission[];
  requireAll?: boolean;
  fallback?: ReactNode;
}

/**
 * Composant pour afficher conditionnellement du contenu basé sur les permissions
 * Ne redirige pas, affiche simplement le fallback si les permissions ne sont pas satisfaites
 */
export function PermissionGate({
  children,
  roles,
  permissions,
  requireAll = false,
  fallback = null,
}: PermissionGateProps) {
  const { isAuthenticated, hasAnyRole, hasAnyPermission, hasAllPermissions } = useAuth();

  if (!isAuthenticated) {
    return <>{fallback}</>;
  }

  // Vérifier les rôles si spécifiés
  if (roles && roles.length > 0) {
    if (!hasAnyRole(roles)) {
      return <>{fallback}</>;
    }
  }

  // Vérifier les permissions si spécifiées
  if (permissions && permissions.length > 0) {
    const hasRequiredPermissions = requireAll
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions);

    if (!hasRequiredPermissions) {
      return <>{fallback}</>;
    }
  }

  return <>{children}</>;
}

/**
 * Hook pour vérifier les permissions de manière déclarative
 */
export function usePermissions() {
  const auth = useAuth();

  return {
    isAuthenticated: auth.isAuthenticated,
    hasRole: auth.hasRole,
    hasAnyRole: auth.hasAnyRole,
    hasPermission: auth.hasPermission,
    hasAnyPermission: auth.hasAnyPermission,
    hasAllPermissions: auth.hasAllPermissions,
    isAdmin: auth.isAdmin,
    isChefOrAdmin: auth.isChefOrAdmin,
    user: auth.user,
  };
}
