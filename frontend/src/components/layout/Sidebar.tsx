"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Home,
  FolderKanban,
  Settings,
  LogOut,
  ImagePlus,
  Brain,
  BarChart3,
  Zap,
  Users
} from "lucide-react";
import { useAuth } from "@/lib/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { RoleBadge } from "@/components/auth/RoleBadge";
import { UserRole, Permission } from "@/types/roles";
import { LucideIcon } from "lucide-react";

interface MenuItem {
  title: string;
  href: string;
  icon: LucideIcon;
  requiredRoles?: UserRole[];
  requiredPermissions?: Permission[];
}

const menuItems: MenuItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: Home,
    // Accessible à tous
  },
  {
    title: "Projets",
    href: "/projects",
    icon: FolderKanban,
    // Accessible à tous (mais contenu différent selon le rôle)
  },
  {
    title: "Images",
    href: "/images",
    icon: ImagePlus,
    requiredPermissions: [Permission.IMAGE_READ],
  },
  {
    title: "Modèles",
    href: "/models",
    icon: Brain,
    requiredRoles: [UserRole.CHEF_OPERATOR, UserRole.ADMIN],
  },
  {
    title: "Inférence",
    href: "/inference/detect",
    icon: Zap,
    requiredPermissions: [Permission.INFERENCE_RUN],
  },
  {
    title: "Rapports",
    href: "/reports",
    icon: BarChart3,
    requiredRoles: [UserRole.CHEF_OPERATOR, UserRole.ADMIN],
  },
  {
    title: "Utilisateurs",
    href: "/settings/users",
    icon: Users,
    requiredRoles: [UserRole.ADMIN],
  },
  {
    title: "Paramètres",
    href: "/settings",
    icon: Settings,
    // Accessible à tous
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout, checkAuth, hasAnyRole, hasAnyPermission } = useAuth();

  // Charger les données utilisateur au montage
  React.useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Filtrer les menus selon les permissions et rôles
  const visibleMenuItems = menuItems.filter((item) => {
    // Si le menu nécessite un rôle spécifique
    if (item.requiredRoles && item.requiredRoles.length > 0) {
      if (!user?.role || !item.requiredRoles.includes(user.role as UserRole)) {
        return false;
      }
    }

    // Si le menu nécessite des permissions spécifiques
    if (item.requiredPermissions && item.requiredPermissions.length > 0) {
      if (!hasAnyPermission(item.requiredPermissions)) {
        return false;
      }
    }

    return true; // Accessible par défaut
  });

  return (
    <aside className="w-64 border-r border-slate-200 bg-slate-50 h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-200">
        <Link href="/dashboard" className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-lg bg-slate-800 flex items-center justify-center">
            <span className="text-white font-bold text-lg">M</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-800">MLOps QC</h1>
            <p className="text-xs text-slate-500">Quality Control</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {visibleMenuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200",
                isActive
                  ? "bg-slate-800 text-white font-medium"
                  : "text-slate-600 hover:bg-slate-200 hover:text-slate-800"
              )}
            >
              <Icon className="h-5 w-5" />
              <span>{item.title}</span>
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="p-4 border-t">
        <div className="mb-3 px-3">
          <p className="text-sm font-medium truncate">{user?.email || "Chargement..."}</p>
          <div className="mt-2">
            {user?.role && <RoleBadge role={user.role as UserRole} />}
          </div>
        </div>
        <Button
          variant="outline"
          className="w-full"
          onClick={() => {
            console.log("🚪 Déconnexion...");
            logout();
            window.location.href = "/auth/login";
          }}
        >
          <LogOut className="mr-2 h-4 w-4" />
          Déconnexion
        </Button>
      </div>
    </aside>
  );
}

