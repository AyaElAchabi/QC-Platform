"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Upload, Zap, Loader2, Eye, CheckCircle, AlertTriangle } from "lucide-react";
import { getAuthToken } from "@/lib/auth";
import { ExplainabilityPanel } from "@/components/inference/ExplainabilityPanel";
import { DetectionXAI } from "@/components/inference/DetectionXAI";

interface Detection {
  bbox: [number, number, number, number];
  class_name: string;
  confidence: number;
  class_id: number;
}

interface Model {
  id: string;
  name: string;
  version: string;
  architecture: string;
  metrics: any;
}

interface XAIMetrics {
  summary: string;
  confidence_stats: {
    mean: number;
    min: number;
    max: number;
    std: number;
  };
  class_distribution: Record<string, { count: number; avg_confidence: number }>;
  spatial_distribution: {
    center: number;
    edges: number;
  };
  detection_areas: Array<{
    class: string;
    area_percent: number;
    confidence: number;
  }>;
  explanation_text: string;
}

export default function InferenceDetectPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.25);
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [inferenceTime, setInferenceTime] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [enableXai, setEnableXai] = useState(false);
  const [xaiHeatmap, setXaiHeatmap] = useState<string | null>(null);
  const [xaiMetrics, setXaiMetrics] = useState<XAIMetrics | null>(null);
  const [hasRun, setHasRun] = useState(false); // Track if inference was run
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    fetchModels();
  }, []);

  // Redraw when detections change or image loads
  const drawDetections = useCallback(() => {
    console.log("🎨 drawDetections appelée");
    const canvas = canvasRef.current;
    const img = imageRef.current;

    console.log("📋 Canvas:", canvas ? "✅" : "❌");
    console.log("📋 Image:", img ? "✅" : "❌");
    console.log("📋 Image loaded:", img?.complete, img?.naturalWidth);
    console.log("📋 Détections:", detections.length);

    if (!canvas || !img || !img.complete || img.naturalWidth === 0) {
      console.warn("⚠️  Canvas ou image pas prêt !");
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      console.warn("⚠️  Contexte canvas manquant !");
      return;
    }

    // Définir les dimensions du canvas
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;

    console.log(`📐 Dimensions canvas: ${canvas.width}x${canvas.height}`);

    // Dessiner l'image
    ctx.drawImage(img, 0, 0);

    // Couleurs pour les classes
    const colors = [
      "#FF6B6B",
      "#4ECDC4",
      "#45B7D1",
      "#FFA07A",
      "#98D8C8",
      "#F7DC6F",
    ];

    // Dessiner les bounding boxes
    console.log(`🖼️  Dessin de ${detections.length} détections...`);
    detections.forEach((detection, idx) => {
      const [x1, y1, x2, y2] = detection.bbox;
      const color = colors[detection.class_id % colors.length];

      console.log(`  Detection ${idx + 1}:`, detection.class_name, detection.confidence);

      // Box
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

      // Label background
      ctx.fillStyle = color;
      const label = `${detection.class_name} ${(detection.confidence * 100).toFixed(1)}%`;
      ctx.font = "bold 16px Arial";
      const textWidth = ctx.measureText(label).width;
      ctx.fillRect(x1, y1 - 25, textWidth + 10, 25);

      // Label text
      ctx.fillStyle = "#FFFFFF";
      ctx.fillText(label, x1 + 5, y1 - 7);
    });

    console.log("✅ Dessin terminé !");
  }, [detections]);

  useEffect(() => {
    if (imagePreview) {
      // Wait for image to be fully loaded before drawing
      const img = imageRef.current;
      if (img) {
        if (img.complete && img.naturalWidth > 0) {
          drawDetections();
        }
      }
    }
  }, [imagePreview, detections, drawDetections]);

  const fetchModels = async () => {
    try {
      const token = getAuthToken();
      const response = await fetch("http://localhost:8000/models", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setModels(data);
        if (data.length > 0) {
          setSelectedModel(data[0].id);
        }
      }
    } catch (error) {
      console.error("Error fetching models:", error);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      setHasRun(false); // Reset when new image is uploaded
      setDetections([]);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDetect = async () => {
    if (!image || !selectedModel) return;

    setLoading(true);
    setDetections([]);
    setXaiHeatmap(null);
    setXaiMetrics(null);
    setHasRun(false);

    try {
      const token = getAuthToken();
      const formData = new FormData();
      formData.append("image", image);
      formData.append("model_id", selectedModel);
      formData.append("confidence_threshold", confidenceThreshold.toString());
      formData.append("enable_xai", enableXai.toString());

      console.log("🚀 Envoi requête d'inférence...");
      const response = await fetch("http://localhost:8000/api/inference/predict", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      console.log("📡 Réponse reçue:", response.status);

      if (response.ok) {
        const data = await response.json();
        console.log("✅ Données reçues:", data);
        console.log("📊 Nombre de détections:", data.detections?.length || 0);
        console.log("🎯 Détections:", data.detections);

        setDetections(data.detections || []);
        setInferenceTime(data.inference_time_ms || 0);
        setHasRun(true);

        // Handle XAI data if present
        if (data.xai_heatmap) {
          console.log("🔥 Heatmap reçue");
          setXaiHeatmap(data.xai_heatmap);
        }
        if (data.xai_metrics) {
          console.log("📊 Métriques XAI reçues");
          setXaiMetrics(data.xai_metrics);
        }

        // Force redraw after state updates
        setTimeout(() => {
          console.log("🎨 Redessinage des détections...");
          drawDetections();
        }, 100);
      } else {
        const error = await response.json();
        console.error("❌ Erreur:", error);
        alert(`Erreur: ${error.detail}`);
      }
    } catch (error) {
      console.error("💥 Error during inference:", error);
      alert("Erreur lors de la détection");
    } finally {
      setLoading(false);
    }
  };

  const handleImageLoad = () => {
    console.log("🖼️ Image chargée, redessinage...");
    drawDetections();
  };

  const selectedModelData = models.find((m) => m.id === selectedModel);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Détection de Défauts</h1>
        <p className="text-muted-foreground">
          Utilisez un modèle entraîné pour détecter les défauts sur vos images
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Model Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Modèle</label>
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionner un modèle" />
                </SelectTrigger>
                <SelectContent>
                  {models.map((model) => (
                    <SelectItem key={model.id} value={model.id}>
                      {model.name} - {model.version}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedModelData && (
                <div className="text-sm space-y-1 mt-2">
                  <p className="text-muted-foreground">
                    Architecture: {selectedModelData.architecture}
                  </p>
                  {selectedModelData.metrics?.map50_95 && (
                    <p className="text-muted-foreground">
                      mAP50-95: {(selectedModelData.metrics.map50_95 * 100).toFixed(2)}%
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Confidence Threshold */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <label className="text-sm font-medium">Seuil de Confiance</label>
                <span className="text-sm text-muted-foreground">
                  {(confidenceThreshold * 100).toFixed(0)}%
                </span>
              </div>
              <Slider
                value={[confidenceThreshold]}
                onValueChange={(value) => setConfidenceThreshold(value[0])}
                min={0.1}
                max={0.9}
                step={0.05}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Détections avec une confiance &gt; {(confidenceThreshold * 100).toFixed(0)}% seront affichées
              </p>
            </div>

            {/* XAI Toggle */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <label className="text-sm font-medium flex items-center gap-2">
                    <Eye className="h-4 w-4 text-blue-500" />
                    Explications (XAI)
                  </label>
                  <p className="text-xs text-muted-foreground">
                    Génère une heatmap et des métriques
                  </p>
                </div>
                <Switch
                  checked={enableXai}
                  onCheckedChange={setEnableXai}
                />
              </div>
              {enableXai && (
                <p className="text-xs text-orange-600 bg-orange-50 p-2 rounded">
                  ⚠️ Ajoute ~500-1000ms au temps d&apos;inférence
                </p>
              )}
            </div>

            {/* Image Upload */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Image</label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                  id="image-upload"
                />
                <label
                  htmlFor="image-upload"
                  className="cursor-pointer flex flex-col items-center"
                >
                  <Upload className="h-8 w-8 text-gray-400 mb-2" />
                  <span className="text-sm text-gray-600">
                    {image ? image.name : "Cliquez pour uploader"}
                  </span>
                </label>
              </div>
            </div>

            {/* Detect Button */}
            <Button
              onClick={handleDetect}
              disabled={!image || !selectedModel || loading}
              className="w-full"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Détection en cours...
                </>
              ) : (
                <>
                  <Zap className="mr-2 h-4 w-4" />
                  Détecter les Défauts
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Results Panel */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Résultats</CardTitle>
              {inferenceTime > 0 && (
                <Badge variant="outline">
                  {inferenceTime.toFixed(0)}ms
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {imagePreview ? (
              <div className="space-y-4">
                {/* Canvas with detections */}
                <div className="relative border-2 border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm">
                  <img
                    ref={imageRef}
                    src={imagePreview}
                    alt="Upload"
                    className="hidden"
                    onLoad={handleImageLoad}
                  />
                  <canvas
                    ref={canvasRef}
                    className="w-full h-auto"
                    style={{ display: 'block', maxHeight: '600px', objectFit: 'contain' }}
                  />

                  {/* Overlay messages */}
                  {!hasRun && !loading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-white/80">
                      <p className="text-sm text-muted-foreground">
                        Cliquez sur &quot;Détecter les Défauts&quot; pour analyser l&apos;image
                      </p>
                    </div>
                  )}

                  {loading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-white/80">
                      <div className="flex flex-col items-center gap-2">
                        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                        <p className="text-sm text-muted-foreground">Analyse en cours...</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Results Summary - After inference */}
                {hasRun && !loading && (
                  <div className={`border rounded-lg p-4 ${detections.length > 0 ? 'bg-blue-50 border-blue-200' : 'bg-green-50 border-green-200'}`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {detections.length > 0 ? (
                          <AlertTriangle className="h-5 w-5 text-orange-500" />
                        ) : (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        )}
                        <div>
                          <h3 className="font-semibold">
                            {detections.length > 0
                              ? `${detections.length} défaut${detections.length > 1 ? 's' : ''} détecté${detections.length > 1 ? 's' : ''}`
                              : "Aucun défaut détecté"}
                          </h3>
                          {detections.length > 0 ? (
                            <p className="text-sm text-blue-700">
                              Confiance moyenne: {(detections.reduce((acc, d) => acc + d.confidence, 0) / detections.length * 100).toFixed(1)}%
                            </p>
                          ) : (
                            <p className="text-sm text-green-700">
                              L&apos;image ne contient pas de défauts détectables (seuil: {(confidenceThreshold * 100).toFixed(0)}%)
                            </p>
                          )}
                        </div>
                      </div>
                      {inferenceTime > 0 && (
                        <Badge variant="outline" className="text-sm">
                          ⚡ {inferenceTime.toFixed(0)}ms
                        </Badge>
                      )}
                    </div>
                  </div>
                )}

                {/* Detections Table */}
                {detections.length > 0 && (
                  <div className="space-y-2">
                    <h3 className="font-semibold text-lg">Détails des Détections</h3>
                    <div className="border rounded-lg overflow-hidden shadow-sm">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50 border-b">
                          <tr>
                            <th className="px-4 py-3 text-left font-semibold">Classe</th>
                            <th className="px-4 py-3 text-left font-semibold">Confiance</th>
                            <th className="px-4 py-3 text-left font-semibold">Position (x,y,w,h)</th>
                            <th className="px-4 py-3 text-right font-semibold">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white">
                          {detections.map((detection, idx) => (
                            <tr key={idx} className="border-t hover:bg-gray-50">
                              <td className="px-4 py-3">
                                <Badge className="font-medium">{detection.class_name}</Badge>
                              </td>
                              <td className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                  <Badge
                                    variant={detection.confidence > 0.7 ? "default" : "secondary"}
                                    className="min-w-[60px] justify-center"
                                  >
                                    {(detection.confidence * 100).toFixed(1)}%
                                  </Badge>
                                  <Progress
                                    value={detection.confidence * 100}
                                    className="h-2 w-24"
                                  />
                                </div>
                              </td>
                              <td className="px-4 py-3 text-xs text-muted-foreground font-mono">
                                [{detection.bbox.map((v) => Math.round(v)).join(", ")}]
                              </td>
                              <td className="px-4 py-3 text-right">
                                <DetectionXAI
                                  imageUrl={imagePreview}
                                  detection={{
                                    class: detection.class_name,
                                    confidence: detection.confidence,
                                    bbox: detection.bbox
                                  }}
                                  modelId={selectedModel}
                                />
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                <Upload className="h-16 w-16 mb-4" />
                <p>Uploadez une image pour commencer la détection</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* XAI Explainability Panel - Always show after inference when XAI is enabled */}
      {enableXai && (hasRun || loading) && (
        <ExplainabilityPanel
          heatmapImage={xaiHeatmap}
          metrics={xaiMetrics}
          isLoading={loading}
        />
      )}
    </div>
  );
}
