"use client";

import { use, useState } from "react";
import { useProject } from "@/lib/hooks/useProjects";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { LabelStudioButton } from "@/components/projects/LabelStudioButton";
import {
  ArrowLeft,
  Upload,
  Edit,
  Eye,
  Trash2,
  BarChart3,
  Play,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { data: project, isLoading } = useProject(id);
  const [activeTab, setActiveTab] = useState("overview");

  if (isLoading) {
    return <div>Chargement...</div>;
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <h2 className="text-2xl font-bold mb-4">Projet non trouvé</h2>
        <Link href="/projects">
          <Button>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Retour aux projets
          </Button>
        </Link>
      </div>
    );
  }

  const annotationPercentage = project.total_images > 0
    ? Math.round((project.annotated_images / project.total_images) * 100)
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/projects">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold">{project.name}</h1>
              <Badge variant="outline" className="bg-green-50">
                {project.status.toUpperCase()}
              </Badge>
            </div>
            <p className="text-muted-foreground">{project.description}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="icon">
            <Edit className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon">
            <BarChart3 className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" className="text-red-600">
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Images
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{project.total_images}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Images Annotées
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{project.annotated_images}</div>
            <p className="text-sm text-muted-foreground">{annotationPercentage}%</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Modèles
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{project.models_count || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Créé
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm">
              {new Date(project.created_at).toLocaleDateString("fr-FR")}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
          <TabsTrigger value="images">Images ({project.total_images})</TabsTrigger>
          <TabsTrigger value="annotations">Annotations</TabsTrigger>
          <TabsTrigger value="training">Training</TabsTrigger>
          <TabsTrigger value="models">Modèles ({project.models_count || 0})</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Actions rapides</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Gérer votre projet
                </p>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => router.push(`/projects/${id}/images`)}
                >
                  <Upload className="mr-2 h-4 w-4" />
                  Importer des images
                </Button>
                <LabelStudioButton projectId={id} />
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => router.push(`/projects/${id}/training`)}
                >
                  <Zap className="mr-2 h-4 w-4" />
                  Entraîner un modèle
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Informations du projet</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm font-medium">Type de tâche</p>
                  <p className="text-sm text-muted-foreground">
                    {project.task_type}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Statut</p>
                  <Badge variant="outline" className="bg-green-50">
                    {project.status.toUpperCase()}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm font-medium">Classes de défauts</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {project.classes && project.classes.length > 0 ? (
                      project.classes.map((cls: any) => (
                        <Badge
                          key={cls.name}
                          variant="outline"
                          style={{ backgroundColor: cls.color + "20", borderColor: cls.color }}
                        >
                          {cls.name}
                        </Badge>
                      ))
                    ) : (
                      <p className="text-sm text-muted-foreground">Aucune classe définie</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="images">
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground text-center py-8">
                Utilisez le bouton "Images" dans la sidebar
              </p>
              <div className="flex justify-center">
                <Button onClick={() => router.push(`/projects/${id}/images`)}>
                  Aller à la galerie
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="annotations">
          <Card>
            <CardHeader>
              <CardTitle>Annotations du projet</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  📊 {project.annotated_images} image(s) annotée(s) sur {project.total_images} ({annotationPercentage}%)
                </p>
                <div className="flex gap-2">
                  <Button onClick={() => router.push(`/projects/${id}/images`)}>
                    Annotation manuelle
                  </Button>
                  <LabelStudioButton projectId={id} />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="training">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Entraînement de modèles
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-900 font-medium mb-2">
                  ✅ Prêt pour l'entraînement !
                </p>
                <p className="text-sm text-blue-800">
                  Vous avez {project.annotated_images} images annotées avec {project.classes?.length || 0} classes. 
                  Vous pouvez maintenant entraîner un modèle YOLOv8.
                </p>
              </div>

              {project.annotated_images >= 10 ? (
                <Button
                  size="lg"
                  className="w-full"
                  onClick={() => router.push(`/projects/${id}/training`)}
                >
                  <Play className="mr-2 h-5 w-5" />
                  Configurer et lancer l'entraînement
                </Button>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">
                    Vous avez besoin d'au moins 10 images annotées pour entraîner un modèle.
                  </p>
                  <p className="text-lg font-medium">
                    {project.annotated_images} / 10 images annotées
                  </p>
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() => router.push(`/projects/${id}/images`)}
                  >
                    Annoter plus d'images
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="models">
          <Card>
            <CardContent className="pt-6">
              <p className="text-muted-foreground text-center py-8">
                Aucun modèle entraîné
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
