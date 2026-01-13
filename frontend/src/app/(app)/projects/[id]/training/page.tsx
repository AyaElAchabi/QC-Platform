"use client";

import { use, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useProject } from "@/lib/hooks/useProjects";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { ArrowLeft, Play, Zap, Loader2, AlertCircle, Eye } from "lucide-react";
import Link from "next/link";
import axios from "axios";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface TrainingJob {
  job_id: string;
  status: string;
  progress: number;
  current_epoch: number;
  total_epochs: number;
  created_at: string;
}

export default function TrainingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { data: project } = useProject(id);

  const [config, setConfig] = useState({
    model_name: "yolov8n",
    epochs: 100,
    batch_size: 16,
    img_size: 640,
    learning_rate: 0.01,
    patience: 50,
    augmentation: true,
  });

  const [isTraining, setIsTraining] = useState(false);
  const [runningJob, setRunningJob] = useState<TrainingJob | null>(null);
  const [checkingJobs, setCheckingJobs] = useState(true);
  const [isCancelling, setIsCancelling] = useState(false);

  // Vérifier s'il y a un training en cours au chargement
  useEffect(() => {
    const checkRunningJobs = async () => {
      try {
        const token = localStorage.getItem("mlops_access_token");
        const response = await axios.get(
          `http://localhost:8000/api/projects/${id}/training-jobs`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        // Chercher un job en cours (running ou pending)
        const activeJob = response.data.find(
          (job: TrainingJob) => job.status === "running" || job.status === "pending"
        );

        if (activeJob) {
          setRunningJob(activeJob);
        }
      } catch (error) {
        console.error("Erreur lors de la vérification des jobs:", error);
      } finally {
        setCheckingJobs(false);
      }
    };

    if (id) {
      checkRunningJobs();
    }
  }, [id]);

  const handleCancelTraining = async () => {
    if (!runningJob) return;

    if (!confirm("Êtes-vous sûr de vouloir arrêter ce training en cours ?")) {
      return;
    }

    setIsCancelling(true);

    try {
      const token = localStorage.getItem("mlops_access_token");
      await axios.post(
        `http://localhost:8000/api/projects/${id}/training/jobs/${runningJob.job_id}/cancel`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      // Réinitialiser l'état
      setRunningJob(null);
      alert("Training annulé avec succès !");
    } catch (error: any) {
      console.error("Erreur lors de l'annulation:", error);
      alert(error.response?.data?.detail || "Erreur lors de l'annulation du training");
    } finally {
      setIsCancelling(false);
    }
  };

  const handleTrain = async () => {
    setIsTraining(true);

    try {
      const token = localStorage.getItem("mlops_access_token");
      const response = await axios.post(
        `http://localhost:8000/api/projects/${id}/train`,
        config,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      router.push(`/projects/${id}/training/${response.data.job_id}`);
    } catch (error: any) {
      alert(error.response?.data?.detail || "Error starting training");
    } finally {
      setIsTraining(false);
    }
  };

  if (!project) return <div className="flex items-center justify-center min-h-screen"><Loader2 className="h-8 w-8 animate-spin" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href={`/projects/${id}`}>
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Training Configuration</h1>
            <p className="text-muted-foreground">{project.name}</p>
          </div>
        </div>
      </div>

      {/* Alerte si un training est en cours */}
      {checkingJobs ? (
        <Card>
          <CardContent className="py-6">
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <p className="text-sm text-muted-foreground">Vérification des trainings en cours...</p>
            </div>
          </CardContent>
        </Card>
      ) : runningJob ? (
        <Alert className="border-amber-200 bg-amber-50">
          <AlertCircle className="h-5 w-5 text-amber-600" />
          <AlertTitle className="text-amber-900 font-semibold">Training en cours</AlertTitle>
          <AlertDescription className="text-amber-800">
            <div className="space-y-2 mt-2">
              <p>
                Un entrainement est déjà en cours pour ce projet (Status: <strong>{runningJob.status}</strong>).
              </p>
              <p className="text-sm">
                Progression: {runningJob.progress}% - Epoch {runningJob.current_epoch || 0}/{runningJob.total_epochs || 0}
              </p>
              <div className="flex gap-2 mt-3">
                <Button
                  variant="outline"
                  size="sm"
                  className="border-amber-600 text-amber-900 hover:bg-amber-100"
                  onClick={() => router.push(`/projects/${id}/training/${runningJob.job_id}`)}
                >
                  <Eye className="mr-2 h-4 w-4" />
                  Voir le training en cours
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleCancelTraining}
                  disabled={isCancelling}
                >
                  {isCancelling ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Annulation...
                    </>
                  ) : (
                    "Arrêter et relancer"
                  )}
                </Button>
              </div>
            </div>
          </AlertDescription>
        </Alert>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Model Selection</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Architecture</Label>
                <Select
                  value={config.model_name}
                  onValueChange={(value) =>
                    setConfig({ ...config, model_name: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="yolov8n">YOLOv8 Nano (Fastest)</SelectItem>
                    <SelectItem value="yolov8s">YOLOv8 Small</SelectItem>
                    <SelectItem value="yolov8m">YOLOv8 Medium</SelectItem>
                    <SelectItem value="yolov8l">YOLOv8 Large</SelectItem>
                    <SelectItem value="yolov8x">YOLOv8 XLarge (Most Accurate)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Hyperparameters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label>Epochs: {config.epochs}</Label>
                <Slider
                  value={[config.epochs]}
                  onValueChange={(v) => setConfig({ ...config, epochs: v[0] })}
                  min={10}
                  max={300}
                  step={10}
                  className="mt-2"
                />
              </div>

              <div>
                <Label>Batch Size: {config.batch_size}</Label>
                <Slider
                  value={[config.batch_size]}
                  onValueChange={(v) => setConfig({ ...config, batch_size: v[0] })}
                  min={4}
                  max={64}
                  step={4}
                  className="mt-2"
                />
              </div>

              <div>
                <Label>Image Size: {config.img_size}</Label>
                <Select
                  value={config.img_size.toString()}
                  onValueChange={(v) =>
                    setConfig({ ...config, img_size: parseInt(v) })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="320">320x320</SelectItem>
                    <SelectItem value="416">416x416</SelectItem>
                    <SelectItem value="640">640x640 (Recommended)</SelectItem>
                    <SelectItem value="1280">1280x1280</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Learning Rate</Label>
                <Input
                  type="number"
                  step="0.001"
                  value={config.learning_rate}
                  onChange={(e) =>
                    setConfig({ ...config, learning_rate: parseFloat(e.target.value) })
                  }
                />
              </div>

              <div>
                <Label>Patience (Early Stopping): {config.patience} epochs</Label>
                <Slider
                  value={[config.patience]}
                  onValueChange={(v) => setConfig({ ...config, patience: v[0] })}
                  min={10}
                  max={100}
                  step={10}
                  className="mt-2"
                />
              </div>

              <div className="flex items-center justify-between">
                <Label>Data Augmentation</Label>
                <Switch
                  checked={config.augmentation}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, augmentation: checked })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Summary */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Training Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Model</p>
                <p className="font-medium">{config.model_name.toUpperCase()}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Images</p>
                <p className="font-medium">{project.total_images}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Annotated</p>
                <p className="font-medium">{project.annotated_images}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Classes</p>
                <p className="font-medium">{project.classes?.length || 0}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Estimated Time</p>
                <p className="font-medium">~{Math.round(config.epochs * 0.5)} min</p>
              </div>
            </CardContent>
          </Card>

          <Button
            onClick={handleTrain}
            disabled={isTraining || (project.annotated_images < 10) || !!runningJob}
            className="w-full"
            size="lg"
          >
            {isTraining ? (
              <>
                <Zap className="mr-2 h-5 w-5 animate-spin" />
                Starting...
              </>
            ) : runningJob ? (
              <>
                <AlertCircle className="mr-2 h-5 w-5" />
                Training en cours
              </>
            ) : (
              <>
                <Play className="mr-2 h-5 w-5" />
                Start Training
              </>
            )}
          </Button>

          {runningJob && (
            <p className="text-sm text-amber-600 text-center">
              Un training est déjà en cours. Attendez qu'il se termine avant d'en lancer un nouveau.
            </p>
          )}

          {!runningJob && project.annotated_images < 10 && (
            <p className="text-sm text-red-600 text-center">
              Need at least 10 annotated images to train
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
