"use client";

import { useProjects } from "@/lib/hooks/useProjects";
import { StatsCard, QuickActionCard, DashboardSection, RecentActivityItem } from "./DashboardWidgets";
import { Upload, Zap, CheckSquare, FolderKanban, Image as ImageIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function OperatorDashboard() {
    const { data: projects, isLoading } = useProjects();

    // Calculs statistiques pour l'opérateur
    const assignedProjects = projects?.length || 0;
    const totalImages = projects?.reduce((acc, p) => acc + (p.total_images || 0), 0) || 0;
    const annotatedImages = projects?.reduce((acc, p) => acc + (p.annotated_images || 0), 0) || 0;
    const remainingImages = totalImages - annotatedImages;

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
                <h1 className="text-3xl font-bold">Dashboard Opérateur</h1>
                <p className="text-muted-foreground">
                    Vos tâches d'annotation et d'inférence
                </p>
            </div>

            {/* Statistiques de Travail */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatsCard
                    title="Projets Assignés"
                    value={assignedProjects}
                    icon={FolderKanban}
                    description="Projets actifs"
                    href="/projects"
                    color="text-blue-600"
                />
                <StatsCard
                    title="Images Annotées"
                    value={annotatedImages}
                    icon={CheckSquare}
                    description={`Sur ${totalImages} totales`}
                    color="text-green-600"
                />
                <StatsCard
                    title="À Annoter"
                    value={remainingImages}
                    icon={ImageIcon}
                    description="Images restantes"
                    color="text-orange-600"
                />
                <StatsCard
                    title="Inférences"
                    value={0}
                    icon={Zap}
                    description="Exécutées aujourd'hui"
                    href="/inference/detect"
                    color="text-purple-600"
                />
            </div>

            {/* Actions Rapides d'Opération */}
            <DashboardSection title="Actions Rapides" description="Vos tâches quotidiennes">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <QuickActionCard
                        title="Upload Images"
                        description="Ajouter de nouvelles images à annoter"
                        icon={Upload}
                        href="/images"
                    />
                    <QuickActionCard
                        title="Annoter des Images"
                        description="Continuer les tâches d'annotation"
                        icon={CheckSquare}
                        href="/images"
                    />
                    <QuickActionCard
                        title="Lancer une Inférence"
                        description="Tester un modèle sur de nouvelles images"
                        icon={Zap}
                        href="/inference/detect"
                        variant="outline"
                    />
                </div>
            </DashboardSection>

            {/* Projets Assignés */}
            <DashboardSection
                title="Mes Projets"
                description="Projets sur lesquels vous travaillez"
                action={{ label: "Voir tous", href: "/projects" }}
            >
                <Card>
                    <CardContent className="pt-6">
                        {projects && projects.length > 0 ? (
                            <div className="space-y-2">
                                {projects.slice(0, 5).map((project) => {
                                    const progress = project.total_images
                                        ? Math.round(((project.annotated_images || 0) / project.total_images) * 100)
                                        : 0;

                                    return (
                                        <RecentActivityItem
                                            key={project.id}
                                            title={project.name}
                                            description={`${project.annotated_images || 0}/${project.total_images || 0} images annotées (${progress}%)`}
                                            time={project.total_images && project.total_images > (project.annotated_images || 0) ? "En cours" : "Terminé"}
                                            icon={FolderKanban}
                                            href={`/projects/${project.id}`}
                                        />
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-muted-foreground">
                                <p>Aucun projet assigné</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </DashboardSection>

            {/* Tâches à Faire */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center">
                            <CheckSquare className="h-5 w-5 mr-2 text-green-600" />
                            Tâches d'Annotation
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {remainingImages > 0 ? (
                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm font-medium">Images à annoter</span>
                                    <span className="text-2xl font-bold text-orange-600">{remainingImages}</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div
                                        className="bg-green-600 h-2 rounded-full"
                                        style={{
                                            width: totalImages > 0 ? `${(annotatedImages / totalImages) * 100}%` : "0%"
                                        }}
                                    />
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    Progression globale : {totalImages > 0 ? Math.round((annotatedImages / totalImages) * 100) : 0}%
                                </p>
                            </div>
                        ) : (
                            <div className="text-center py-8 text-muted-foreground">
                                <p className="text-sm">Toutes les images sont annotées !</p>
                            </div>
                        )}
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center">
                            <Zap className="h-5 w-5 mr-2 text-purple-600" />
                            Historique d'Inférence
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-center py-8 text-muted-foreground">
                            <p className="text-sm">Aucune inférence récente</p>
                            <p className="text-xs mt-2">Vos inférences apparaîtront ici</p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
