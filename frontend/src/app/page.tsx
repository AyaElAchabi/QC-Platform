"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Vérifier si l'utilisateur est connecté
    const token = localStorage.getItem("mlops_access_token");
    if (token) {
      router.push("/dashboard");
    } else {
      router.push("/auth/login");
    }
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-lg">Chargement...</div>
    </div>
  );
}
