"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useProjects } from "@/lib/hooks/useProjects";
import { FolderKanban, Image, Brain, BarChart3, Plus } from "lucide-react";
import Link from "next/link";
import { useEffect } from "react";

export default function DashboardPage() {
  const { data: projects, isLoading, error } = useProjects();

  useEffect(() => {
    console.log("Dashboard mounted");
    console.log("Token:", localStorage.getItem("mlops_access_token"));
  }, []);

  useEffect(() => {
    console.log("🔵 Dashboard - État:", {
      projects,
      isLoading,
      error,
      projectsCount: projects?.length,
    });
  }, [projects, isLoading, error]);

  const stats = [
    {
      title: "Projets",
      value: projects?.length || 0,
      icon: FolderKanban,
      href: "/projects",
      color: "text-blue-600",
    },
    {
      title: "Images",
      value: projects?.reduce((acc, p) => acc + (p.total_images || 0), 0) || 0,
      icon: Image,
      href: "/images",
      color: "text-green-600",
    },
    {
      title: "Modèles",
      value: projects?.reduce((acc, p) => acc + (p.models_count || 0), 0) || 0,
      icon: Brain,
      href: "/models",
      color: "text-purple-600",
    },
    {
      title: "Rapports",
      value: 0,
      icon: BarChart3,
      href: "/reports",
      color: "text-orange-600",
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <p>Chargement...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-600 font-bold mb-2">Erreur de chargement</p>
          <p className="text-sm text-gray-600">{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Vue d'ensemble de votre plateforme MLOps QC
          </p>
        </div>
        <Link href="/projects">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Nouveau Projet
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Link key={stat.title} href={stat.href}>
            <Card className="hover:shadow-lg transition cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Projets Récents</CardTitle>
        </CardHeader>
        <CardContent>
          {projects && projects.length > 0 ? (
            <div className="space-y-4">
              {projects.slice(0, 5).map((project) => (
                <Link
                  key={project.id}
                  href={`/projects/${project.id}`}
                  className="block p-4 border rounded-lg hover:bg-gray-50 transition"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-semibold">{project.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {project.description}
                      </p>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {project.total_images || 0} images
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <p className="mb-4">Aucun projet pour le moment</p>
              <Link href="/projects">
                <Button>Créer votre premier projet</Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
