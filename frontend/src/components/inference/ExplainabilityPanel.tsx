"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Eye, BarChart3, MapPin, Info } from "lucide-react";

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

interface ExplainabilityPanelProps {
    heatmapImage: string | null;
    metrics: XAIMetrics | null;
    isLoading?: boolean;
}

export function ExplainabilityPanel({
    heatmapImage,
    metrics,
    isLoading = false,
}: ExplainabilityPanelProps) {
    if (isLoading) {
        return (
            <Card className="border-blue-200 bg-blue-50/50">
                <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center gap-2">
                        <Eye className="h-5 w-5 text-blue-600" />
                        Explications (XAI)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-center py-8">
                        <div className="animate-pulse text-muted-foreground">
                            Génération des explications...
                        </div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (!heatmapImage && !metrics) {
        return null;
    }

    return (
        <Card className="border-blue-200 bg-gradient-to-br from-blue-50/50 to-purple-50/50">
            <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                    <Eye className="h-5 w-5 text-blue-600" />
                    Explications du Modèle (XAI)
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                {/* Heatmap Visualization */}
                {heatmapImage && (
                    <div className="space-y-2">
                        <h4 className="font-medium text-sm flex items-center gap-2">
                            <MapPin className="h-4 w-4 text-orange-500" />
                            Carte d&apos;Attention
                        </h4>
                        <p className="text-xs text-muted-foreground mb-2">
                            Les zones chaudes (rouge/jaune) indiquent où le modèle a concentré son attention pour détecter les défauts.
                        </p>
                        <div className="relative border rounded-lg overflow-hidden bg-gray-100">
                            <img
                                src={heatmapImage}
                                alt="Heatmap d'attention"
                                className="w-full h-auto"
                            />
                        </div>
                        <div className="flex items-center justify-between text-xs text-muted-foreground mt-1">
                            <span className="flex items-center gap-1">
                                <div className="w-3 h-3 rounded bg-blue-500"></div>
                                Basse attention
                            </span>
                            <span className="flex items-center gap-1">
                                <div className="w-3 h-3 rounded bg-green-500"></div>
                                Moyenne
                            </span>
                            <span className="flex items-center gap-1">
                                <div className="w-3 h-3 rounded bg-yellow-500"></div>
                                Élevée
                            </span>
                            <span className="flex items-center gap-1">
                                <div className="w-3 h-3 rounded bg-red-500"></div>
                                Très élevée
                            </span>
                        </div>
                    </div>
                )}

                {/* Metrics Section */}
                {metrics && (
                    <div className="space-y-4">
                        {/* Confidence Statistics */}
                        <div className="space-y-2">
                            <h4 className="font-medium text-sm flex items-center gap-2">
                                <BarChart3 className="h-4 w-4 text-green-500" />
                                Statistiques de Confiance
                            </h4>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="bg-white rounded-lg p-3 border">
                                    <div className="text-xs text-muted-foreground">Moyenne</div>
                                    <div className="text-lg font-semibold text-green-600">
                                        {(metrics.confidence_stats.mean * 100).toFixed(1)}%
                                    </div>
                                    <Progress
                                        value={metrics.confidence_stats.mean * 100}
                                        className="h-1 mt-1"
                                    />
                                </div>
                                <div className="bg-white rounded-lg p-3 border">
                                    <div className="text-xs text-muted-foreground">Min / Max</div>
                                    <div className="text-lg font-semibold">
                                        <span className="text-orange-500">
                                            {(metrics.confidence_stats.min * 100).toFixed(0)}%
                                        </span>
                                        {" / "}
                                        <span className="text-green-600">
                                            {(metrics.confidence_stats.max * 100).toFixed(0)}%
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Class Distribution */}
                        {Object.keys(metrics.class_distribution).length > 0 && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-sm">Distribution par Classe</h4>
                                <div className="space-y-2">
                                    {Object.entries(metrics.class_distribution).map(
                                        ([className, stats]) => (
                                            <div
                                                key={className}
                                                className="flex items-center justify-between bg-white rounded-lg p-2 border"
                                            >
                                                <div className="flex items-center gap-2">
                                                    <Badge variant="outline">{className}</Badge>
                                                    <span className="text-sm text-muted-foreground">
                                                        {stats.count} détection(s)
                                                    </span>
                                                </div>
                                                <Badge
                                                    variant={
                                                        stats.avg_confidence > 0.7 ? "default" : "secondary"
                                                    }
                                                >
                                                    {(stats.avg_confidence * 100).toFixed(0)}%
                                                </Badge>
                                            </div>
                                        )
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Spatial Distribution */}
                        <div className="space-y-2">
                            <h4 className="font-medium text-sm">Distribution Spatiale</h4>
                            <div className="flex gap-4">
                                <div className="flex-1 bg-white rounded-lg p-3 border text-center">
                                    <div className="text-2xl font-bold text-blue-600">
                                        {metrics.spatial_distribution.center}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                        Au centre
                                    </div>
                                </div>
                                <div className="flex-1 bg-white rounded-lg p-3 border text-center">
                                    <div className="text-2xl font-bold text-purple-600">
                                        {metrics.spatial_distribution.edges}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                        Sur les bords
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Explanation Text */}
                        {metrics.explanation_text && (
                            <div className="space-y-2">
                                <h4 className="font-medium text-sm flex items-center gap-2">
                                    <Info className="h-4 w-4 text-blue-500" />
                                    Synthèse
                                </h4>
                                <div className="bg-white rounded-lg p-4 border text-sm leading-relaxed">
                                    {metrics.explanation_text.split("\n").map((line, idx) => (
                                        <p key={idx} className="mb-1">
                                            {line.startsWith("**") ? (
                                                <span
                                                    dangerouslySetInnerHTML={{
                                                        __html: line
                                                            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"),
                                                    }}
                                                />
                                            ) : line.startsWith("-") ? (
                                                <span className="ml-2 text-muted-foreground">{line}</span>
                                            ) : (
                                                line
                                            )}
                                        </p>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
