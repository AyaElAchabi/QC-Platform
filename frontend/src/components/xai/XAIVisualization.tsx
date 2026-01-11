"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
  Eye,
  Zap,
  Brain,
  Sparkles,
  Loader2,
  Download,
  Info
} from "lucide-react";
import { apiClient } from "@/lib/api/client";

interface XAIVisualizationProps {
  imageUrl: string;
  modelId?: string;
  onGenerate?: (methods: string[]) => void;
}

interface XAIMethod {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  available: boolean;
  speed: "fast" | "medium" | "slow" | "very_slow";
}

const XAI_METHODS: XAIMethod[] = [
  {
    id: "gradcam",
    name: "Grad-CAM",
    description: "Visualise les zones importantes pour la détection",
    icon: <Eye className="h-4 w-4" />,
    available: true,
    speed: "fast"
  },
  {
    id: "gradcam++",
    name: "Grad-CAM++",
    description: "Version améliorée de Grad-CAM",
    icon: <Zap className="h-4 w-4" />,
    available: true,
    speed: "fast"
  },
  {
    id: "lime",
    name: "LIME",
    description: "Explications locales interprétables",
    icon: <Brain className="h-4 w-4" />,
    available: false,
    speed: "slow"
  },
  {
    id: "integrated_gradients",
    name: "Integrated Gradients",
    description: "Attribution des gradients intégrés",
    icon: <Sparkles className="h-4 w-4" />,
    available: false,
    speed: "medium"
  }
];

const SPEED_LABELS = {
  fast: { label: "Rapide", color: "bg-green-500" },
  medium: { label: "Moyen", color: "bg-yellow-500" },
  slow: { label: "Lent", color: "bg-orange-500" },
  very_slow: { label: "Très lent", color: "bg-red-500" }
};

export function XAIVisualization({ imageUrl, modelId, onGenerate }: XAIVisualizationProps) {
  const [selectedMethods, setSelectedMethods] = useState<string[]>(["gradcam"]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [explanations, setExplanations] = useState<Record<string, any>>({});

  const toggleMethod = (methodId: string) => {
    setSelectedMethods(prev =>
      prev.includes(methodId)
        ? prev.filter(m => m !== methodId)
        : [...prev, methodId]
    );
  };

  const handleGenerate = async () => {
    if (selectedMethods.length === 0) return;

    setIsGenerating(true);
    try {
      const response = await apiClient.post("/api/xai/generate", {
        image_path: imageUrl,
        methods: selectedMethods,
        model_id: modelId
      });

      setExplanations(response.data.explanations);

      if (onGenerate) {
        onGenerate(selectedMethods);
      }
    } catch (error) {
      console.error("XAI generation error:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = (methodId: string) => {
    const explanation = explanations[methodId];
    if (!explanation?.heatmap) return;

    const link = document.createElement("a");
    link.href = explanation.heatmap;
    link.download = `xai-${methodId}-${Date.now()}.png`;
    link.click();
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-500" />
            Explications XAI
          </CardTitle>
          <CardDescription>
            Visualisez les décisions du modèle
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {XAI_METHODS.map((method) => (
              <button
                key={method.id}
                onClick={() => method.available && toggleMethod(method.id)}
                disabled={!method.available}
                className={`
                  p-4 rounded-lg border-2 text-left transition-all
                  ${selectedMethods.includes(method.id)
                    ? "border-purple-500 bg-purple-50"
                    : "border-gray-200 hover:border-gray-300"
                  }
                  ${!method.available && "opacity-50 cursor-not-allowed"}
                `}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {method.icon}
                    <span className="font-semibold">{method.name}</span>
                  </div>
                  <div className="flex gap-2">
                    <Badge
                      variant="outline"
                      className={`text-xs ${SPEED_LABELS[method.speed].color} text-white border-none`}
                    >
                      {SPEED_LABELS[method.speed].label}
                    </Badge>
                    {!method.available && (
                      <Badge variant="outline" className="text-xs">
                        Bientôt
                      </Badge>
                    )}
                  </div>
                </div>
                <p className="text-sm text-gray-600">
                  {method.description}
                </p>
              </button>
            ))}
          </div>

          <Button
            onClick={handleGenerate}
            disabled={selectedMethods.length === 0 || isGenerating}
            className="w-full"
            size="lg"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Génération en cours...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Générer ({selectedMethods.length})
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {Object.keys(explanations).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Résultats</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue={Object.keys(explanations)[0]}>
              <TabsList>
                {Object.keys(explanations).map((methodId) => (
                  <TabsTrigger key={methodId} value={methodId}>
                    {XAI_METHODS.find(m => m.id === methodId)?.name}
                  </TabsTrigger>
                ))}
              </TabsList>

              {Object.entries(explanations).map(([methodId, result]) => (
                <TabsContent key={methodId} value={methodId} className="mt-4">
                  {result.success && result.heatmap ? (
                    <div className="space-y-4">
                      <div className="relative rounded-lg overflow-hidden border">
                        <img
                          src={result.heatmap}
                          alt={`XAI - ${methodId}`}
                          className="w-full h-auto"
                        />
                      </div>

                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="space-y-1">
                          <p className="text-sm font-medium">Méthode: {result.method}</p>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownload(methodId)}
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Télécharger
                        </Button>
                      </div>

                      <div className="flex gap-2 p-3 bg-blue-50 rounded-lg text-sm">
                        <Info className="h-4 w-4 text-blue-600 mt-0.5" />
                        <p className="text-blue-900">
                          Les zones rouges/jaunes indiquent les régions importantes
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-red-600">
                      <p>Erreur: {result.error}</p>
                    </div>
                  )}
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
