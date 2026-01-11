"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";
import { UserRole, Permission } from "@/types/roles";

interface RequireAuthProps {
  children: ReactNode;
  roles?: UserRole[];
  permissions?: Permission[];
  requireAll?: boolean; // Si true, nécessite toutes les permissions, sinon au moins une
  fallbackUrl?: string;
}

/**
 * Composant de protection des routes basé sur les rôles et permissions
 */
export function RequireAuth({
  children,
  roles,
  permissions,
  requireAll = false,
  fallbackUrl = "/auth/login",
}: RequireAuthProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading, hasAnyRole, hasPermission, hasAnyPermission, hasAllPermissions } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      // Vérifier si l'utilisateur est authentifié
      if (!isAuthenticated) {
        router.push(fallbackUrl);
        return;
      }

      // Vérifier les rôles si spécifiés
      if (roles && roles.length > 0) {
        if (!hasAnyRole(roles)) {
          router.push("/unauthorized");
          return;
        }
      }

      // Vérifier les permissions si spécifiées
      if (permissions && permissions.length > 0) {
        const hasRequiredPermissions = requireAll
          ? hasAllPermissions(permissions)
          : hasAnyPermission(permissions);

        if (!hasRequiredPermissions) {
          router.push("/unauthorized");
          return;
        }
      }
    }
  }, [isAuthenticated, isLoading, roles, permissions, requireAll, router, fallbackUrl, hasAnyRole, hasAnyPermission, hasAllPermissions]);

  // Afficher un loader pendant la vérification
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Vérifier immédiatement les conditions (sans attendre useEffect)
  if (!isAuthenticated) {
    return null;
  }

  if (roles && roles.length > 0 && !hasAnyRole(roles)) {
    return null;
  }

  if (permissions && permissions.length > 0) {
    const hasRequiredPermissions = requireAll
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions);

    if (!hasRequiredPermissions) {
      return null;
    }
  }

  return <>{children}</>;
}

/**
 * HOC pour protéger une page
 */
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options?: {
    roles?: UserRole[];
    permissions?: Permission[];
    requireAll?: boolean;
    fallbackUrl?: string;
  }
) {
  return function ProtectedComponent(props: P) {
    return (
      <RequireAuth {...options}>
        <Component {...props} />
      </RequireAuth>
    );
  };
}
