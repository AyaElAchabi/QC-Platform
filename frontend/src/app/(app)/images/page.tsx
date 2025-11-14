"use client";

import { useState } from "react";
import { useProjects } from "@/lib/hooks/useProjects";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Search, Image as ImageIcon } from "lucide-react";
import Link from "next/link";

export default function ImagesPage() {
  const { data: projects, isLoading } = useProjects();
  const [searchQuery, setSearchQuery] = useState("");

  // Calculer le total d'images
  const totalImages = projects?.reduce((acc, p) => acc + (p.total_images || 0), 0) || 0;
  const totalAnnotated = projects?.reduce((acc, p) => acc + (p.annotated_images || 0), 0) || 0;

  if (isLoading) {
    return <div className="flex items-center justify-center h-96">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Images</h1>
        <p className="text-muted-foreground">
          Toutes les images de vos projets
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Images
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{totalImages}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Images Annotées
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{totalAnnotated}</div>
            <p className="text-sm text-muted-foreground">
              {totalImages > 0 ? Math.round((totalAnnotated / totalImages) * 100) : 0}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              À Annoter
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{totalImages - totalAnnotated}</div>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Rechercher des images..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Projects with Images */}
      <div className="space-y-4">
        {projects && projects.length > 0 ? (
          projects
            .filter(p => (p.total_images || 0) > 0)
            .map((project) => (
              <Card key={project.id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle>{project.name}</CardTitle>
                      <p className="text-sm text-muted-foreground">
                        {project.description}
                      </p>
                    </div>
                    <Badge variant="outline">
                      {project.total_images} images
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <Link
                    href={`/projects/${project.id}/images`}
                    className="text-blue-600 hover:underline text-sm"
                  >
                    Voir la galerie →
                  </Link>
                </CardContent>
              </Card>
            ))
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16">
              <ImageIcon className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Aucune image</h3>
              <p className="text-muted-foreground">
                Commencez par créer un projet et importer des images
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
