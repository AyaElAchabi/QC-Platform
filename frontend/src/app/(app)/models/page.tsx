"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Brain, Plus, Download, Trash2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getAuthToken } from "@/lib/auth";

interface Model {
  id: string;
  name: string;
  version: string;
  architecture: string;
  task_type: string;
  stage: string;
  is_active: boolean;
  project_id: string;
  training_job_id?: string;
  storage_path: string;
  metrics: any;
  hyperparameters: any;
  inference_count: number;
  avg_inference_time_ms?: number;
  created_at: string;
  updated_at: string;
}

export default function ModelsPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const token = getAuthToken();
      if (!token) {
        console.error("No auth token found");
        return;
      }
      const response = await fetch("http://localhost:8000/models", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setModels(data);
      } else {
        console.error("Failed to fetch models:", response.status);
      }
    } catch (error) {
      console.error("Error fetching models:", error);
    } finally {
      setLoading(false);
    }
  };

  const productionModels = models.filter((m) => m.stage?.toLowerCase() === "production");
  const stagingModels = models.filter((m) => m.stage?.toLowerCase() === "staging");

  const getStageColor = (stage: string) => {
    switch (stage?.toLowerCase()) {
      case "production":
        return "bg-green-500";
      case "staging":
        return "bg-yellow-500";
      case "archived":
        return "bg-gray-500";
      default:
        return "bg-blue-500";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Modèles</h1>
          <p className="text-muted-foreground">
            Gérez vos modèles de détection YOLOv8
          </p>
        </div>
        <Button disabled>
          <Plus className="mr-2 h-4 w-4" />
          Entraîner un modèle
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Modèles
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{models.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              En Production
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{productionModels.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              En Staging
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stagingModels.length}</div>
          </CardContent>
        </Card>
      </div>

      {loading ? (
        <Card>
          <CardContent className="flex items-center justify-center py-16">
            <p className="text-muted-foreground">Chargement...</p>
          </CardContent>
        </Card>
      ) : models.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Brain className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Aucun modèle</h3>
            <p className="text-muted-foreground mb-4 text-center max-w-md">
              Entraînez votre premier modèle YOLOv8 pour détecter automatiquement les défauts
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {models.map((model) => (
            <Card key={model.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{model.name}</CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      {model.version}
                    </p>
                  </div>
                  <Badge className={getStageColor(model.stage)}>
                    {model.stage}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Architecture:</span>
                    <span className="font-medium">{model.architecture}</span>
                  </div>
                  {model.metrics?.map50_95 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">mAP50-95:</span>
                      <span className="font-medium">
                        {(model.metrics.map50_95 * 100).toFixed(2)}%
                      </span>
                    </div>
                  )}
                  {model.metrics?.map50 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">mAP50:</span>
                      <span className="font-medium">
                        {(model.metrics.map50 * 100).toFixed(2)}%
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Inférences:</span>
                    <span className="font-medium">{model.inference_count}</span>
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button variant="outline" size="sm" className="flex-1" disabled>
                    <Download className="mr-2 h-4 w-4" />
                    Télécharger
                  </Button>
                  <Button variant="outline" size="sm" disabled>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>

                {model.training_job_id && (
                  <Link
                    href={`/projects/${model.project_id}/training/${model.training_job_id}`}
                    className="text-xs text-blue-500 hover:underline block"
                  >
                    Voir le training →
                  </Link>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}