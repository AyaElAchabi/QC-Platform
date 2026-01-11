"use client";

import { useProjects } from "@/lib/hooks/useProjects";
import { StatsCard, DashboardSection, ProjectOverviewCard } from "./DashboardWidgets";
import { FolderKanban, Image as ImageIcon, Brain, BarChart3 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

export function ViewerDashboard() {
    const { data: projects, isLoading } = useProjects();

    // Calculs statistiques (lecture seule)
    const totalProjects = projects?.length || 0;
    const totalImages = projects?.reduce((acc, p) => acc + (p.total_images || 0), 0) || 0;
    const totalModels = projects?.reduce((acc, p) => acc + (p.models_count || 0), 0) || 0;
    const annotatedImages = projects?.reduce((acc, p) => acc + (p.annotated_images || 0), 0) || 0;

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
                <h1 className="text-3xl font-bold">Dashboard Visualiseur</h1>
                <p className="text-muted-foreground">
                    Vue en lecture seule de la plateforme
                </p>
            </div>

            {/* Statistiques Globales (Lecture Seule) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatsCard
                    title="Projets"
                    value={totalProjects}
                    icon={FolderKanban}
                    description="Projets disponibles"
                    href="/projects"
                    color="text-blue-600"
                />
                <StatsCard
                    title="Images"
                    value={totalImages}
                    icon={ImageIcon}
                    description={`${annotatedImages} annotées`}
                    href="/images"
                    color="text-green-600"
                />
                <StatsCard
                    title="Modèles"
                    value={totalModels}
                    icon={Brain}
                    description="Modèles disponibles"
                    href="/models"
                    color="text-purple-600"
                />
                <StatsCard
                    title="Rapports"
                    value={0}
                    icon={BarChart3}
                    description="Rapports disponibles"
                    color="text-orange-600"
                />
            </div>

            {/* Note de Lecture Seule */}
            <Card className="bg-blue-50 border-blue-200">
                <CardContent className="pt-6">
                    <div className="flex items-start space-x-3">
                        <div className="p-2 bg-blue-100 rounded-lg">
                            <BarChart3 className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-blue-900">Mode Lecture Seule</h3>
                            <p className="text-sm text-blue-700 mt-1">
                                Vous disposez d'un accès en consultation uniquement. Vous pouvez visualiser les projets,
                                les images, les modèles et les rapports, mais vous ne pouvez pas effectuer de modifications.
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Projets Disponibles */}
            <DashboardSection
                title="Projets Disponibles"
                description="Consultation des projets"
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
                            <p>Aucun projet disponible</p>
                        </CardContent>
                    </Card>
                )}
            </DashboardSection>

            {/* Informations de Consultation */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardContent className="pt-6">
                        <div className="space-y-4">
                            <div>
                                <h3 className="font-semibold mb-2">Que pouvez-vous faire ?</h3>
                                <ul className="space-y-2 text-sm text-muted-foreground">
                                    <li className="flex items-center">
                                        <span className="text-green-600 mr-2">✓</span>
                                        Visualiser tous les projets
                                    </li>
                                    <li className="flex items-center">
                                        <span className="text-green-600 mr-2">✓</span>
                                        Consulter les images et annotations
                                    </li>
                                    <li className="flex items-center">
                                        <span className="text-green-600 mr-2">✓</span>
                                        Voir les modèles entraînés
                                    </li>
                                    <li className="flex items-center">
                                        <span className="text-green-600 mr-2">✓</span>
                                        Accéder aux rapports et statistiques
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="pt-6">
                        <div className="space-y-4">
                            <div>
                                <h3 className="font-semibold mb-2">Restrictions</h3>
                                <ul className="space-y-2 text-sm text-muted-foreground">
                                    <li className="flex items-center">
                                        <span className="text-red-600 mr-2">✗</span>
                                        Créer ou modifier des projets
                                    </li>
                                    <li className="flex items-center">
                                        <span className="text-red-600 mr-2">✗</span>
                                        Upload ou annoter des images
                                    </li>
                                    <li className="flex items-center">
                                        <span className="text-red-600 mr-2">✗</span>
                                        Entraîner ou déployer des modèles
                                    </li>
                                    <li className="flex items-center">
                                        <span className="text-red-600 mr-2">✗</span>
                                        Exécuter des inférences
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
