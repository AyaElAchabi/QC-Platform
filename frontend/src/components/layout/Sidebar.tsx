"use client";

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
  BarChart3
} from "lucide-react";
import { useAuth } from "@/lib/hooks/useAuth";
import { Button } from "@/components/ui/button";

const menuItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: Home,
  },
  {
    title: "Projets",
    href: "/projects",
    icon: FolderKanban,
  },
  {
    title: "Images",
    href: "/images",
    icon: ImagePlus,
  },
  {
    title: "Modèles",
    href: "/models",
    icon: Brain,
  },
  {
    title: "Rapports",
    href: "/reports",
    icon: BarChart3,
  },
  {
    title: "Paramètres",
    href: "/settings",
    icon: Settings,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="w-64 border-r bg-card h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b">
        <Link href="/dashboard" className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <span className="text-white font-bold text-lg">M</span>
          </div>
          <div>
            <h1 className="text-xl font-bold">MLOps QC</h1>
            <p className="text-xs text-muted-foreground">Quality Control</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors",
                isActive
                  ? "bg-blue-100 text-blue-900 font-medium"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
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
          <p className="text-sm font-medium">{user?.email}</p>
          <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
        </div>
        <Button
          variant="outline"
          className="w-full"
          onClick={logout}
        >
          <LogOut className="mr-2 h-4 w-4" />
          Déconnexion
        </Button>
      </div>
    </aside>
  );
}
