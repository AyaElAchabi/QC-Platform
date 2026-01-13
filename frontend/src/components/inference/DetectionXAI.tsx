"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sparkles,
  Loader2,
  Info,
  Download,
  Clock,
  AlertCircle,
  CheckCircle,
  Lightbulb,
  Layers,
  Zap,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";

interface Detection {
  class: string;
  confidence: number;
  bbox: [number, number, number, number];
}

interface DetectionXAIProps {
  imageUrl: string;
  detection: Detection;
  modelId?: string;
}

interface XAIResult {
  method: string;
  heatmap: string | null;
  success: boolean;
  error?: string;
  processing_time_ms?: number;
  interpretation?: string;
}

interface XAIMethod {
  id: string;
  name: string;
  description: string;
  available: boolean;
  speed: "fast" | "medium" | "slow";
  recommended: boolean;
}

const methodInterpretations: Record<string, { title: string; guide: string[] }> = {
  gradcam: {
    title: "Grad-CAM - Carte d'Activation",
    guide: [
      "Les zones rouges/jaunes indiquent où le modèle a regardé pour détecter le défaut",
      "Plus la couleur est chaude, plus la région est importante pour la décision",
      "Permet de vérifier que le modèle regarde au bon endroit",
    ],
  },
  "gradcam++": {
    title: "Grad-CAM++ - Carte d'Activation Améliorée",
    guide: [
      "Version améliorée de Grad-CAM avec meilleure localisation des petits objets",
      "Particulièrement utile pour les défauts de petite taille",
      "Les zones colorées montrent les régions d'attention du modèle",
    ],
  },
  lime: {
    title: "LIME - Explications par Super-pixels",
    guide: [
      "L'image est divisée en régions (super-pixels)",
      "Les zones vertes contribuent positivement à la détection",
      "Les zones rouges contribuent négativement (s'opposent à la détection)",
      "Utile pour comprendre quelles textures/formes influencent la décision",
    ],
  },
  shap: {
    title: "SHAP - Valeurs d'Importance",
    guide: [
      "Basé sur la théorie des jeux (valeurs de Shapley)",
      "Chaque pixel reçoit une valeur d'importance",
      "Les zones colorées ont le plus d'impact sur la prédiction",
      "Méthode plus lente mais très robuste théoriquement",
    ],
  },
  integrated_gradients: {
    title: "Integrated Gradients - Attribution par Gradients",
    guide: [
      "Compare l'image à une baseline (image noire)",
      "Calcule comment chaque pixel contribue à la détection",
      "Les zones claires sont les plus importantes",
      "Satisfait des propriétés mathématiques rigoureuses",
    ],
  },
};

export function DetectionXAI({ imageUrl, detection, modelId }: DetectionXAIProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [explanations, setExplanations] = useState<Record<string, XAIResult>>({});
  const [availableMethods, setAvailableMethods] = useState<XAIMethod[]>([]);
  const [selectedMethods, setSelectedMethods] = useState<string[]>(["gradcam"]);
  const [activeTab, setActiveTab] = useState("gradcam");
  const [loadingMethod, setLoadingMethod] = useState<string | null>(null);

  // Charger les méthodes disponibles
  useEffect(() => {
    const fetchMethods = async () => {
      try {
        const response = await apiClient.get("/api/xai/methods");
        setAvailableMethods(response.data.methods);
      } catch (error) {
        console.error("Failed to fetch XAI methods:", error);
        // Fallback avec méthodes par défaut
        setAvailableMethods([
          { id: "gradcam", name: "Grad-CAM", description: "", available: true, speed: "fast", recommended: true },
          { id: "gradcam++", name: "Grad-CAM++", description: "", available: true, speed: "fast", recommended: true },
          { id: "lime", name: "LIME", description: "", available: true, speed: "medium", recommended: true },
          { id: "integrated_gradients", name: "Integrated Gradients", description: "", available: true, speed: "medium", recommended: true },
          { id: "shap", name: "SHAP", description: "", available: true, speed: "slow", recommended: false },
        ]);
      }
    };
    fetchMethods();
  }, []);

  const handleExplain = async () => {
    setIsOpen(true);

    // Générer Grad-CAM par défaut si pas encore fait
    if (!explanations.gradcam) {
      await generateExplanation("gradcam");
    }
  };

  const generateExplanation = async (method: string) => {
    if (explanations[method]?.success) {
      // Déjà généré avec succès
      setActiveTab(method);
      return;
    }

    setLoadingMethod(method);
    setIsGenerating(true);

    try {
      const response = await apiClient.post("/api/xai/generate", {
        image_path: imageUrl,
        methods: [method],
        model_id: modelId,
        bbox: detection.bbox,
      });

      const result = response.data.explanations[method];
      setExplanations((prev) => ({
        ...prev,
        [method]: result,
      }));
      setActiveTab(method);
    } catch (error) {
      console.error(`XAI generation error for ${method}:`, error);
      setExplanations((prev) => ({
        ...prev,
        [method]: {
          method,
          heatmap: null,
          success: false,
          error: "Échec de la génération",
        },
      }));
    } finally {
      setLoadingMethod(null);
      setIsGenerating(false);
    }
  };

  const handleDownload = (method: string) => {
    const explanation = explanations[method];
    if (!explanation?.heatmap) return;

    const link = document.createElement("a");
    link.href = explanation.heatmap;
    link.download = `xai-${detection.class}-${method}-${Date.now()}.png`;
    link.click();
  };

  const getSpeedBadge = (speed: string) => {
    switch (speed) {
      case "fast":
        return <Badge variant="default" className="bg-green-500">Rapide</Badge>;
      case "medium":
        return <Badge variant="secondary">Moyen</Badge>;
      case "slow":
        return <Badge variant="outline" className="text-orange-600 border-orange-600">Lent</Badge>;
      default:
        return null;
    }
  };

  return (
    <>
      {/* Bouton Expliquer */}
      <Button
        variant="outline"
        size="sm"
        onClick={handleExplain}
        className="gap-2"
      >
        <Sparkles className="h-4 w-4" />
        Expliquer
      </Button>

      {/* Dialog avec les explications */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="w-[95vw] max-w-none max-h-[95vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-500" />
              Explications XAI - {detection.class}
            </DialogTitle>
            <DialogDescription>
              Comprenez pourquoi le modèle a détecté &quot;{detection.class}&quot; avec{" "}
              {(detection.confidence * 100).toFixed(1)}% de confiance
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Info Box pour les opérateurs */}
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-4">
                <div className="flex gap-2">
                  <Lightbulb className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="text-sm text-blue-900">
                    <p className="font-medium mb-1">Guide d&apos;interprétation</p>
                    <p>
                      Ces visualisations montrent les régions de l&apos;image qui ont
                      influencé la décision du modèle. Utilisez différentes méthodes
                      pour valider la cohérence de la détection.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Sélecteur de méthodes */}
            <div className="flex flex-wrap gap-2">
              {availableMethods.filter(m => m.available).map((method) => (
                <Button
                  key={method.id}
                  variant={activeTab === method.id ? "default" : "outline"}
                  size="sm"
                  onClick={() => generateExplanation(method.id)}
                  disabled={loadingMethod !== null}
                  className="gap-2"
                >
                  {loadingMethod === method.id ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : explanations[method.id]?.success ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : explanations[method.id]?.error ? (
                    <AlertCircle className="h-4 w-4 text-red-500" />
                  ) : (
                    <Layers className="h-4 w-4" />
                  )}
                  {method.name}
                  {getSpeedBadge(method.speed)}
                </Button>
              ))}
            </div>

            {/* Contenu principal */}
            {loadingMethod && !explanations[loadingMethod] ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Loader2 className="h-12 w-12 animate-spin text-purple-500 mb-4" />
                <p className="text-sm text-gray-600">
                  Génération de l&apos;explication {loadingMethod.toUpperCase()} en cours...
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  Cela peut prendre quelques secondes
                </p>
              </div>
            ) : explanations[activeTab] ? (
              <div className="space-y-4">
                {/* Visualisation */}
                {explanations[activeTab].success && explanations[activeTab].heatmap ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Image originale */}
                    <div className="space-y-3">
                      <h3 className="text-base font-semibold">Image Originale</h3>
                      <div className="relative rounded-lg border-2 overflow-hidden bg-gray-100 shadow-md">
                        <img
                          src={imageUrl}
                          alt="Original"
                          className="w-full h-auto"
                          style={{ minHeight: '350px', objectFit: 'contain' }}
                        />
                      </div>
                    </div>

                    {/* Heatmap XAI */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="text-base font-semibold">
                          {methodInterpretations[activeTab]?.title || activeTab.toUpperCase()}
                        </h3>
                        <div className="flex gap-2">
                          {explanations[activeTab].processing_time_ms && (
                            <Badge variant="outline" className="gap-1">
                              <Clock className="h-3 w-3" />
                              {explanations[activeTab].processing_time_ms?.toFixed(0)}ms
                            </Badge>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDownload(activeTab)}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="relative rounded-lg border-2 overflow-hidden shadow-md">
                        <img
                          src={explanations[activeTab].heatmap!}
                          alt={`${activeTab} explanation`}
                          className="w-full h-auto"
                          style={{ minHeight: '350px', objectFit: 'contain' }}
                        />
                      </div>
                    </div>
                  </div>
                ) : explanations[activeTab].error ? (
                  <div className="text-center py-8">
                    <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                    <p className="text-red-600 font-medium">
                      Erreur lors de la génération
                    </p>
                    <p className="text-sm text-muted-foreground mt-2">
                      {explanations[activeTab].error}
                    </p>
                  </div>
                ) : null}

                {/* Guide d'interprétation */}
                {explanations[activeTab]?.success && methodInterpretations[activeTab] && (
                  <Card className="bg-gray-50">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <Info className="h-4 w-4 text-blue-500" />
                        Comment interpréter
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <ul className="text-sm space-y-1 text-muted-foreground">
                        {methodInterpretations[activeTab].guide.map((item, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-blue-500 mt-1">•</span>
                            {item}
                          </li>
                        ))}
                      </ul>
                      {explanations[activeTab]?.interpretation && (
                        <p className="mt-3 text-sm font-medium text-gray-700">
                          {explanations[activeTab].interpretation}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                )}

                {/* Détails de la détection */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Détails de la Détection</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-muted-foreground">Classe :</span>
                        <Badge className="ml-2">{detection.class}</Badge>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Confiance :</span>
                        <span className="ml-2 font-semibold">
                          {(detection.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Position :</span>
                        <span className="ml-2 font-mono text-xs">
                          [{detection.bbox.map((v) => v.toFixed(0)).join(", ")}]
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Méthode XAI :</span>
                        <span className="ml-2 font-semibold uppercase">{activeTab}</span>
                      </div>
                    </div>
                    <div className="pt-2">
                      <span className="text-muted-foreground">Niveau de confiance :</span>
                      <Progress
                        value={detection.confidence * 100}
                        className="mt-1 h-2"
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Zap className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Sélectionnez une méthode XAI pour générer l&apos;explication</p>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
