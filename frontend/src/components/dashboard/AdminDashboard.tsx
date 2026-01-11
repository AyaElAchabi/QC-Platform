"use client";

import { useProjects } from "@/lib/hooks/useProjects";
import { StatsCard, QuickActionCard, DashboardSection, RecentActivityItem } from "./DashboardWidgets";
import { Users, FolderKanban, Brain, Zap, Plus, Settings, FileText, Activity } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function AdminDashboard() {
    const { data: projects, isLoading } = useProjects();

    // Calculs statistiques globales
    const totalProjects = projects?.length || 0;
    const totalImages = projects?.reduce((acc, p) => acc + (p.total_images || 0), 0) || 0;
    const totalModels = projects?.reduce((acc, p) => acc + (p.models_count || 0), 0) || 0;

    // Simulated data - À remplacer par de vraies données API
    const totalUsers = 7; // À récupérer depuis l'API
    const activeTrainings = 0; // À récupérer depuis l'API

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
                <h1 className="text-3xl font-bold">Dashboard Administrateur</h1>
                <p className="text-muted-foreground">
                    Vue d'ensemble complète de la plateforme MLOps QC
                </p>
            </div>

            {/* Statistiques Globales */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatsCard
                    title="Utilisateurs"
                    value={totalUsers}
                    icon={Users}
                    description="Utilisateurs actifs"
                    href="/settings/users"
                    color="text-purple-600"
                />
                <StatsCard
                    title="Projets"
                    value={totalProjects}
                    icon={FolderKanban}
                    description="Projets actifs"
                    href="/projects"
                    color="text-blue-600"
                />
                <StatsCard
                    title="Modèles"
                    value={totalModels}
                    icon={Brain}
                    description="Modèles entraînés"
                    href="/models"
                    color="text-green-600"
                />
                <StatsCard
                    title="Images"
                    value={totalImages}
                    icon={FileText}
                    description="Images totales"
                    href="/images"
                    color="text-orange-600"
                />
            </div>

            {/* Actions Rapides */}
            <DashboardSection title="Actions Rapides" description="Accès rapide aux fonctionnalités principales">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <QuickActionCard
                        title="Gérer les Utilisateurs"
                        description="Ajouter, modifier ou supprimer des utilisateurs"
                        icon={Users}
                        href="/settings/users"
                    />
                    <QuickActionCard
                        title="Créer un Projet"
                        description="Démarrer un nouveau projet de détection"
                        icon={Plus}
                        href="/projects"
                    />
                    <QuickActionCard
                        title="Voir les Paramètres"
                        description="Configuration système et préférences"
                        icon={Settings}
                        href="/settings"
                        variant="outline"
                    />
                </div>
            </DashboardSection>

            {/* Projets Récents */}
            <DashboardSection
                title="Projets Récents"
                description="Derniers projets créés ou modifiés"
                action={{ label: "Voir tous", href: "/projects" }}
            >
                <Card>
                    <CardContent className="pt-6">
                        {projects && projects.length > 0 ? (
                            <div className="space-y-2">
                                {projects.slice(0, 5).map((project) => (
                                    <RecentActivityItem
                                        key={project.id}
                                        title={project.name}
                                        description={`${project.total_images || 0} images • ${project.models_count || 0} modèles`}
                                        time="Récent"
                                        icon={FolderKanban}
                                        href={`/projects/${project.id}`}
                                    />
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-muted-foreground">
                                <p>Aucun projet pour le moment</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </DashboardSection>

            {/* Activité Système */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center">
                            <Activity className="h-5 w-5 mr-2 text-blue-600" />
                            Activité Récente
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            <RecentActivityItem
                                title="Nouveau projet créé"
                                description="Surface Detection Project"
                                time="Il y a 2h"
                            />
                            <RecentActivityItem
                                title="Utilisateur ajouté"
                                description="operator@test.com"
                                time="Il y a 5h"
                            />
                            <RecentActivityItem
                                title="Modèle déployé"
                                description="YOLOv8 - Défauts de surface"
                                time="Il y a 1j"
                            />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center">
                            <Zap className="h-5 w-5 mr-2 text-green-600" />
                            Entraînements en Cours
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {activeTrainings > 0 ? (
                            <div className="space-y-2">
                                <p className="text-sm text-muted-foreground">
                                    {activeTrainings} entraînement(s) en cours
                                </p>
                            </div>
                        ) : (
                            <div className="text-center py-8 text-muted-foreground">
                                <p className="text-sm">Aucun entraînement en cours</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
