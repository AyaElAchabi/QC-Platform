"use client";

import { useProjects } from "@/lib/hooks/useProjects";
import { StatsCard, QuickActionCard, DashboardSection, ProjectOverviewCard } from "./DashboardWidgets";
import { FolderKanban, Brain, Zap, Plus, Upload, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ChefOperatorDashboard() {
    const { data: projects, isLoading } = useProjects();

    // Calculs statistiques
    const totalProjects = projects?.length || 0;
    const totalImages = projects?.reduce((acc, p) => acc + (p.total_images || 0), 0) || 0;
    const totalModels = projects?.reduce((acc, p) => acc + (p.models_count || 0), 0) || 0;
    const annotatedImages = projects?.reduce((acc, p) => acc + (p.annotated_images || 0), 0) || 0;

    // Calcul du taux d'annotation
    const annotationRate = totalImages > 0 ? Math.round((annotatedImages / totalImages) * 100) : 0;

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Dashboard Chef Opérateur</h1>
                <p className="text-muted-foreground">
                    Gestion des projets, entraînements et supervision de l'équipe
                </p>
            </div>

            {/* Statistiques d'Équipe */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatsCard
                    title="Projets"
                    value={totalProjects}
                    icon={FolderKanban}
                    description="Projets gérés"
                    href="/projects"
                    color="text-blue-600"
                />
                <StatsCard
                    title="Images Totales"
                    value={totalImages}
                    icon={Upload}
                    description="Dans tous les projets"
                    href="/images"
                    color="text-green-600"
                />
                <StatsCard
                    title="Taux d'Annotation"
                    value={`${annotationRate}%`}
                    icon={TrendingUp}
                    description={`${annotatedImages} / ${totalImages} images`}
                    color="text-purple-600"
                />
                <StatsCard
                    title="Modèles"
                    value={totalModels}
                    icon={Brain}
                    description="Modèles entraînés"
                    href="/models"
                    color="text-orange-600"
                />
            </div>

            {/* Actions Rapides de Supervision */}
            <DashboardSection title="Actions Rapides" description="Accès rapide aux fonctionnalités de gestion">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <QuickActionCard
                        title="Créer un Projet"
                        description="Démarrer un nouveau projet de détection"
                        icon={Plus}
                        href="/projects"
                    />
                    <QuickActionCard
                        title="Entraîner un Modèle"
                        description="Lancer un nouvel entraînement"
                        icon={Brain}
                        href="/models"
                    />
                    <QuickActionCard
                        title="Déployer un Modèle"
                        description="Mettre un modèle en production"
                        icon={Zap}
                        href="/inference/detect"
                        variant="outline"
                    />
                </div>
            </DashboardSection>

            {/* Mes Projets */}
            <DashboardSection
                title="Mes Projets"
                description="Projets en cours de gestion"
                action={{ label: "Voir tous", href: "/projects" }}
            >
                {projects && projects.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {projects.slice(0, 6).map((project) => (
                            <ProjectOverviewCard key={project.id} project={project} />
                        ))}
                    </div>
                ) : (
                    <Card>
                        <CardContent className="py-12 text-center text-muted-foreground">
                            <p className="mb-4">Aucun projet pour le moment</p>
                            <p className="text-sm">Créez votre premier projet pour commencer</p>
                        </CardContent>
                    </Card>
                )}
            </DashboardSection>

            {/* Entraînements Actifs */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center">
                        <Brain className="h-5 w-5 mr-2 text-blue-600" />
                        Entraînements en Cours
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8 text-muted-foreground">
                        <p className="text-sm">Aucun entraînement en cours</p>
                        <p className="text-xs mt-2">Les entraînements actifs apparaîtront ici</p>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
