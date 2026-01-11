"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { useAuth } from "@/lib/hooks/useAuth";

export default function AppLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { checkAuth, user } = useAuth();

  useEffect(() => {
    const token = localStorage.getItem("mlops_access_token");
    console.log("🔵 AppLayout - Vérification auth, token:", !!token);
    
    if (!token) {
      console.log("🔴 AppLayout - Pas de token, redirection vers login");
      router.push("/auth/login");
    } else {
      // Charger les données utilisateur depuis le localStorage
      console.log("🟢 AppLayout - Token présent, chargement des données...");
      checkAuth();
    }
  }, [router, checkAuth]);
  
  // Log pour debug
  useEffect(() => {
    console.log("🔍 AppLayout - User chargé:", user);
  }, [user]);

  // Toujours afficher le layout - la redirection se fera si nécessaire
  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
