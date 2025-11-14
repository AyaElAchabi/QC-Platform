"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, Download, CheckCircle, XCircle, Clock, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface TrainingMetrics {
  epoch: number;
  map50?: number;
  map50_95?: number;
  precision?: number;
  recall?: number;
  box_loss?: number;
  cls_loss?: number;
  dfl_loss?: number;
  [key: string]: any;
}

interface TrainingJob {
  id: number;
  status: string;
  progress: number;
  current_epoch: number;
  total_epochs: number;
  metrics: TrainingMetrics[];
  model_path?: string;
  error_message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  config: any;
}

export default function TrainingJobPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const jobId = params.jobId as string;

  const [job, setJob] = useState<TrainingJob | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleDownloadModel = async () => {
    if (!job?.model_path) return;
    
    try {
      // TODO: Implémenter le téléchargement depuis MinIO
      // Pour l'instant, afficher une alerte
      alert(`Téléchargement du modèle: ${job.model_path}\n\nL'implémentation du téléchargement depuis MinIO sera ajoutée prochainement.`);
    } catch (err) {
      console.error("Erreur lors du téléchargement:", err);
      alert("Erreur lors du téléchargement du modèle");
    }
  };

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const response = await apiClient.get(`/api/projects/${projectId}/training/jobs/${jobId}`);
        setJob(response.data);
        setError(null);
      } catch (err: any) {
        console.error("Erreur lors de la récupération du job:", err);
        setError(err.response?.data?.detail || "Erreur lors du chargement du job");
      } finally {
        setIsLoading(false);
      }
    };

    fetchJob();

    // Polling toutes les 5 secondes si le job est en cours
    const interval = setInterval(() => {
      if (job?.status === "running" || job?.status === "pending") {
        fetchJob();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [projectId, jobId, job?.status]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-6 w-6 text-green-600" />;
      case "failed":
        return <XCircle className="h-6 w-6 text-red-600" />;
      case "running":
        return <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />;
      default:
        return <Clock className="h-6 w-6 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600 bg-green-50 border-green-200";
      case "failed":
        return "text-red-600 bg-red-50 border-red-200";
      case "running":
        return "text-blue-600 bg-blue-50 border-blue-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: string } = {
      pending: "En attente",
      running: "En cours",
      completed: "Terminé",
      failed: "Échoué",
    };
    return labels[status] || status;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          <p className="font-semibold">Erreur</p>
          <p>{error || "Job introuvable"}</p>
          <Button
            variant="outline"
            onClick={() => router.push(`/projects/${projectId}/training`)}
            className="mt-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Retour
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            onClick={() => router.push(`/projects/${projectId}/training`)}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Retour
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Training Job #{jobId.substring(0, 8)}...</h1>
            <p className="text-gray-600">Monitoring de l'entraînement en temps réel</p>
          </div>
        </div>
        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${getStatusColor(job.status)}`}>
          {getStatusIcon(job.status)}
          <span className="font-semibold">{getStatusLabel(job.status)}</span>
        </div>
      </div>

      {/* Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Progression</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Epoch {job.current_epoch} / {job.total_epochs}</span>
              <span>{job.progress}%</span>
            </div>
            <Progress value={job.progress} className="h-2" />
          </div>

          {job.error_message && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              <p className="font-semibold">Erreur:</p>
              <p className="text-sm">{job.error_message}</p>
            </div>
          )}

          {job.status === "completed" && job.model_path && (
            <Button className="w-full" onClick={handleDownloadModel}>
              <Download className="mr-2 h-4 w-4" />
              Télécharger le modèle
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Metrics Chart */}
      {job.metrics && job.metrics.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Métriques d'Entraînement</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">{/* mAP Chart */}
              <div>
                <h3 className="text-sm font-semibold mb-2">Mean Average Precision (mAP)</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={job.metrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="epoch" label={{ value: "Epoch", position: "insideBottom", offset: -5 }} />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Legend />
                    {job.metrics.some(m => m.map50 !== undefined) && (
                      <Line
                        type="monotone"
                        dataKey="map50"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        name="mAP@50"
                      />
                    )}
                    {job.metrics.some(m => m.map50_95 !== undefined) && (
                      <Line
                        type="monotone"
                        dataKey="map50_95"
                        stroke="#10b981"
                        strokeWidth={2}
                        name="mAP@50-95"
                      />
                    )}
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Precision & Recall Chart */}
              <div>
                <h3 className="text-sm font-semibold mb-2">Precision & Recall</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={job.metrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="epoch" label={{ value: "Epoch", position: "insideBottom", offset: -5 }} />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Legend />
                    {job.metrics.some(m => m.precision !== undefined) && (
                      <Line
                        type="monotone"
                        dataKey="precision"
                        stroke="#8b5cf6"
                        strokeWidth={2}
                        name="Precision"
                      />
                    )}
                    {job.metrics.some(m => m.recall !== undefined) && (
                      <Line
                        type="monotone"
                        dataKey="recall"
                        stroke="#f59e0b"
                        strokeWidth={2}
                        name="Recall"
                      />
                    )}
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Loss Chart */}
              <div>
                <h3 className="text-sm font-semibold mb-2">Losses</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={job.metrics}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="epoch" label={{ value: "Epoch", position: "insideBottom", offset: -5 }} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    {job.metrics.some(m => m.box_loss !== undefined) && (
                      <Line
                        type="monotone"
                        dataKey="box_loss"
                        stroke="#ef4444"
                        strokeWidth={2}
                        name="Box Loss"
                      />
                    )}
                    {job.metrics.some(m => m.cls_loss !== undefined) && (
                      <Line
                        type="monotone"
                        dataKey="cls_loss"
                        stroke="#f97316"
                        strokeWidth={2}
                        name="Class Loss"
                      />
                    )}
                    {job.metrics.some(m => m.dfl_loss !== undefined) && (
                      <Line
                        type="monotone"
                        dataKey="dfl_loss"
                        stroke="#ec4899"
                        strokeWidth={2}
                        name="DFL Loss"
                      />
                    )}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="py-8">
            <div className="flex flex-col items-center justify-center gap-3 text-center">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              <div>
                <p className="font-semibold text-blue-900">Préparation du training...</p>
                <p className="text-sm text-blue-700 mt-1">
                  Les métriques apparaîtront dès que le premier epoch sera complété
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Modèle</p>
              <p className="font-semibold">{job.config?.model_name || job.config?.model || "yolov8n"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Epochs</p>
              <p className="font-semibold">{job.total_epochs || job.config?.epochs || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Batch Size</p>
              <p className="font-semibold">{job.config?.batch_size || "N/A"}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Image Size</p>
              <p className="font-semibold">{job.config?.img_size || "640"}</p>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Créé le</p>
                <p className="font-medium">{new Date(job.created_at).toLocaleString('fr-FR')}</p>
              </div>
              {job.started_at && (
                <div>
                  <p className="text-gray-600">Démarré le</p>
                  <p className="font-medium">{new Date(job.started_at).toLocaleString('fr-FR')}</p>
                </div>
              )}
              {job.completed_at && (
                <div>
                  <p className="text-gray-600">Terminé le</p>
                  <p className="font-medium">{new Date(job.completed_at).toLocaleString('fr-FR')}</p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
