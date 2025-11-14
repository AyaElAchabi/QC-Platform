"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Eye, Edit, Trash2, Image as ImageIcon } from "lucide-react";
import Link from "next/link";
import type { Project } from "@/types/project";

interface ProjectCardProps {
  project: Project;
  onDelete?: (id: string) => void;
}

const taskTypeLabels: Record<string, string> = {
  classification: "Classification",
  detection: "Détection",
  segmentation: "Segmentation",
};

const statusColors: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  archived: "bg-gray-100 text-gray-800",
  completed: "bg-blue-100 text-blue-800",
};

export function ProjectCard({ project, onDelete }: ProjectCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="truncate">{project.name}</span>
          <div className="flex gap-2">
            <Link href={`/projects/${project.id}`}>
              <Button variant="ghost" size="icon">
                <Eye className="h-4 w-4" />
              </Button>
            </Link>
            <Button variant="ghost" size="icon">
              <Edit className="h-4 w-4" />
            </Button>
            {onDelete && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onDelete(project.id)}
              >
                <Trash2 className="h-4 w-4 text-red-600" />
              </Button>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2 mb-4">
          <Badge variant="outline">
            {taskTypeLabels[project.task_type] || project.task_type}
          </Badge>
          <Badge className={statusColors[project.status] || ""}>
            {project.status}
          </Badge>
        </div>

        <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
          {project.description}
        </p>

        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <ImageIcon className="h-4 w-4" />
            <span>{project.total_images || 0} images</span>
          </div>
          <div>
            <span>{project.annotated_images || 0} annotées</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
