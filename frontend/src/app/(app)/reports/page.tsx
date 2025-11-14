"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useProjects } from "@/lib/hooks/useProjects";
import { BarChart3, TrendingUp, AlertCircle, CheckCircle } from "lucide-react";

export default function ReportsPage() {
  const { data: projects, isLoading } = useProjects();

  const totalImages = projects?.reduce((acc, p) => acc + (p.total_images || 0), 0) || 0;
  const totalAnnotated = projects?.reduce((acc, p) => acc + (p.annotated_images || 0), 0) || 0;
  const annotationRate = totalImages > 0 ? Math.round((totalAnnotated / totalImages) * 100) : 0;

  if (isLoading) {
    return <div className="flex items-center justify-center h-96">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Rapports</h1>
        <p className="text-muted-foreground">
          Statistiques et analytics de votre plateforme
        </p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Projets Actifs
            </CardTitle>
            <BarChart3 className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{projects?.length || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Taux d'Annotation
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{annotationRate}%</div>
            <p className="text-xs text-muted-foreground">
              {totalAnnotated} / {totalImages} images
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Modèles Déployés
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Détections Aujourd'hui
            </CardTitle>
            <AlertCircle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0</div>
          </CardContent>
        </Card>
      </div>

      {/* Détails par projet */}
      <Card>
        <CardHeader>
          <CardTitle>Performance par Projet</CardTitle>
        </CardHeader>
        <CardContent>
          {projects && projects.length > 0 ? (
            <div className="space-y-4">
              {projects.map((project) => (
                <div key={project.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <h3 className="font-semibold">{project.name}</h3>
                    <p className="text-sm text-muted-foreground">{project.description}</p>
                  </div>
                  <div className="flex gap-8 text-sm">
                    <div>
                      <p className="text-muted-foreground">Images</p>
                      <p className="font-semibold">{project.total_images || 0}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Annotées</p>
                      <p className="font-semibold text-green-600">
                        {project.annotated_images || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Taux</p>
                      <p className="font-semibold">
                        {project.total_images > 0
                          ? Math.round(((project.annotated_images || 0) / project.total_images) * 100)
                          : 0}%
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              Aucun projet pour générer des rapports
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
