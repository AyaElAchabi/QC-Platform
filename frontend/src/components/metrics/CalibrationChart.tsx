"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ReferenceLine,
    Bar,
    ComposedChart,
} from "recharts";
import { Target, Info } from "lucide-react";

interface CalibrationData {
    bins: number[];
    accuracy_per_bin: (number | null)[];
    confidence_per_bin: (number | null)[];
    count_per_bin: number[];
    ece: number;
}

interface CalibrationChartProps {
    data: CalibrationData | null;
    isLoading?: boolean;
}

export function CalibrationChart({ data, isLoading = false }: CalibrationChartProps) {
    if (isLoading) {
        return (
            <Card>
                <CardContent className="py-8">
                    <div className="flex items-center justify-center">
                        <div className="animate-pulse text-muted-foreground">
                            Chargement de la courbe de calibration...
                        </div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (!data) {
        return null;
    }

    // Préparer les données pour le graphique
    const chartData = data.bins.map((bin, index) => ({
        bin: (bin * 100).toFixed(0) + "%",
        binValue: bin,
        accuracy: data.accuracy_per_bin[index] !== null ? data.accuracy_per_bin[index]! * 100 : null,
        confidence: data.confidence_per_bin[index] !== null ? data.confidence_per_bin[index]! * 100 : null,
        count: data.count_per_bin[index],
        perfect: bin * 100, // Ligne de calibration parfaite
    }));

    const getECEColor = (ece: number) => {
        if (ece <= 0.05) return "text-green-600";
        if (ece <= 0.10) return "text-blue-600";
        if (ece <= 0.15) return "text-yellow-600";
        if (ece <= 0.25) return "text-orange-600";
        return "text-red-600";
    };

    const getECEBadge = (ece: number) => {
        if (ece <= 0.05) return { text: "Excellent", variant: "default" as const };
        if (ece <= 0.10) return { text: "Bon", variant: "default" as const };
        if (ece <= 0.15) return { text: "Modéré", variant: "secondary" as const };
        if (ece <= 0.25) return { text: "Faible", variant: "destructive" as const };
        return { text: "Très faible", variant: "destructive" as const };
    };

    const eceBadge = getECEBadge(data.ece);

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2">
                        <Target className="h-5 w-5 text-purple-500" />
                        Courbe de Calibration (Reliability Diagram)
                    </CardTitle>
                    <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">ECE:</span>
                        <span className={`font-bold ${getECEColor(data.ece)}`}>
                            {(data.ece * 100).toFixed(2)}%
                        </span>
                        <Badge variant={eceBadge.variant}>{eceBadge.text}</Badge>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" className="opacity-50" />
                            <XAxis
                                dataKey="bin"
                                label={{ value: "Confiance prédite", position: "bottom", offset: 0 }}
                            />
                            <YAxis
                                label={{ value: "Précision réelle (%)", angle: -90, position: "insideLeft" }}
                                domain={[0, 100]}
                            />
                            <Tooltip
                                content={({ active, payload }) => {
                                    if (active && payload && payload.length) {
                                        const data = payload[0].payload;
                                        return (
                                            <div className="bg-white p-3 border rounded-lg shadow-lg">
                                                <p className="font-semibold">Bin: {data.bin}</p>
                                                <p className="text-blue-600">
                                                    Précision réelle: {data.accuracy !== null ? data.accuracy.toFixed(1) + "%" : "N/A"}
                                                </p>
                                                <p className="text-green-600">
                                                    Confiance moy.: {data.confidence !== null ? data.confidence.toFixed(1) + "%" : "N/A"}
                                                </p>
                                                <p className="text-gray-500">
                                                    Échantillons: {data.count}
                                                </p>
                                            </div>
                                        );
                                    }
                                    return null;
                                }}
                            />
                            <Legend />

                            {/* Ligne de calibration parfaite (diagonale) */}
                            <Line
                                type="linear"
                                dataKey="perfect"
                                stroke="#9CA3AF"
                                strokeDasharray="5 5"
                                dot={false}
                                name="Calibration parfaite"
                            />

                            {/* Courbe de calibration réelle */}
                            <Line
                                type="monotone"
                                dataKey="accuracy"
                                stroke="#3B82F6"
                                strokeWidth={2}
                                dot={{ fill: "#3B82F6", r: 4 }}
                                connectNulls
                                name="Précision réelle"
                            />

                            {/* Barres pour le nombre d'échantillons (optionnel, commenté) */}
                            {/* <Bar dataKey="count" fill="#E5E7EB" opacity={0.5} name="Nombre d'échantillons" /> */}
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>

                {/* Légende explicative */}
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-start gap-2">
                        <Info className="h-5 w-5 text-blue-500 mt-0.5" />
                        <div className="text-sm text-gray-700">
                            <p className="font-medium mb-1">Comment lire ce graphique :</p>
                            <ul className="list-disc list-inside space-y-1 text-xs">
                                <li>La <strong>ligne en pointillés</strong> représente une calibration parfaite</li>
                                <li>La <strong>courbe bleue</strong> montre la précision réelle du modèle</li>
                                <li>Si la courbe est au-dessus de la diagonale, le modèle est <strong>sous-confiant</strong></li>
                                <li>Si la courbe est en-dessous, le modèle est <strong>sur-confiant</strong></li>
                                <li>L&apos;<strong>ECE</strong> (Expected Calibration Error) mesure l&apos;écart moyen</li>
                            </ul>
                        </div>
                    </div>
                </div>

                {/* Distribution des échantillons par bin */}
                <div className="mt-4">
                    <p className="text-sm font-medium mb-2">Distribution des prédictions par bin de confiance:</p>
                    <div className="flex gap-1">
                        {data.count_per_bin.map((count, idx) => {
                            const maxCount = Math.max(...data.count_per_bin);
                            const height = maxCount > 0 ? (count / maxCount) * 40 + 4 : 4;
                            return (
                                <div
                                    key={idx}
                                    className="flex-1 bg-blue-200 rounded-t"
                                    style={{ height: `${height}px` }}
                                    title={`${data.bins[idx] * 100}%: ${count} échantillons`}
                                />
                            );
                        })}
                    </div>
                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                        <span>0%</span>
                        <span>50%</span>
                        <span>100%</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
