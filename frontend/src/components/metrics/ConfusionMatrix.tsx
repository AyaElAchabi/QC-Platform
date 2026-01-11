"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Grid3X3 } from "lucide-react";

interface ConfusionMatrixData {
    tp_per_class: Record<string, number>;
    fp_per_class: Record<string, number>;
    fn_per_class: Record<string, number>;
    total_tp: number;
    total_fp: number;
    total_fn: number;
    iou_threshold: number;
}

interface ConfusionMatrixProps {
    data: ConfusionMatrixData | null;
    classNames: string[];
    isLoading?: boolean;
}

export function ConfusionMatrix({ data, classNames, isLoading = false }: ConfusionMatrixProps) {
    if (isLoading) {
        return (
            <Card>
                <CardContent className="py-8">
                    <div className="flex items-center justify-center">
                        <div className="animate-pulse text-muted-foreground">
                            Chargement de la matrice de confusion...
                        </div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (!data || classNames.length === 0) {
        return null;
    }

    // Créer une matrice visuelle simple pour la détection d'objets
    // Pour chaque classe: TP, FP, FN
    const getColorIntensity = (value: number, max: number) => {
        if (max === 0) return "bg-gray-100";
        const intensity = value / max;
        if (intensity > 0.75) return "bg-green-500 text-white";
        if (intensity > 0.5) return "bg-green-400 text-white";
        if (intensity > 0.25) return "bg-green-300";
        if (intensity > 0) return "bg-green-200";
        return "bg-gray-100";
    };

    const getErrorColorIntensity = (value: number, max: number) => {
        if (max === 0) return "bg-gray-100";
        const intensity = value / max;
        if (intensity > 0.75) return "bg-red-500 text-white";
        if (intensity > 0.5) return "bg-red-400 text-white";
        if (intensity > 0.25) return "bg-red-300";
        if (intensity > 0) return "bg-red-200";
        return "bg-gray-100";
    };

    const maxTP = Math.max(...Object.values(data.tp_per_class), 1);
    const maxFP = Math.max(...Object.values(data.fp_per_class), 1);
    const maxFN = Math.max(...Object.values(data.fn_per_class), 1);

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2">
                        <Grid3X3 className="h-5 w-5 text-blue-500" />
                        Matrice de Confusion par Classe
                    </CardTitle>
                    <Badge variant="outline">IoU ≥ {(data.iou_threshold * 100).toFixed(0)}%</Badge>
                </div>
            </CardHeader>
            <CardContent>
                <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                        <thead>
                            <tr>
                                <th className="p-2 text-left border-b font-medium">Classe</th>
                                <th className="p-2 text-center border-b font-medium text-green-600">
                                    TP
                                    <div className="text-xs font-normal text-gray-500">Vrais Positifs</div>
                                </th>
                                <th className="p-2 text-center border-b font-medium text-red-600">
                                    FP
                                    <div className="text-xs font-normal text-gray-500">Faux Positifs</div>
                                </th>
                                <th className="p-2 text-center border-b font-medium text-orange-600">
                                    FN
                                    <div className="text-xs font-normal text-gray-500">Faux Négatifs</div>
                                </th>
                                <th className="p-2 text-center border-b font-medium">Total Détections</th>
                            </tr>
                        </thead>
                        <tbody>
                            {classNames.map((className) => {
                                const tp = data.tp_per_class[className] || 0;
                                const fp = data.fp_per_class[className] || 0;
                                const fn = data.fn_per_class[className] || 0;
                                const total = tp + fp;

                                return (
                                    <tr key={className} className="hover:bg-gray-50">
                                        <td className="p-2 border-b font-medium">{className}</td>
                                        <td className="p-2 border-b text-center">
                                            <div
                                                className={`inline-block px-3 py-1 rounded ${getColorIntensity(tp, maxTP)}`}
                                            >
                                                {tp}
                                            </div>
                                        </td>
                                        <td className="p-2 border-b text-center">
                                            <div
                                                className={`inline-block px-3 py-1 rounded ${getErrorColorIntensity(fp, maxFP)}`}
                                            >
                                                {fp}
                                            </div>
                                        </td>
                                        <td className="p-2 border-b text-center">
                                            <div
                                                className={`inline-block px-3 py-1 rounded ${getErrorColorIntensity(fn, maxFN)}`}
                                            >
                                                {fn}
                                            </div>
                                        </td>
                                        <td className="p-2 border-b text-center text-gray-600">{total}</td>
                                    </tr>
                                );
                            })}
                            {/* Totaux */}
                            <tr className="bg-gray-50 font-semibold">
                                <td className="p-2 border-t-2">Total</td>
                                <td className="p-2 border-t-2 text-center text-green-600">{data.total_tp}</td>
                                <td className="p-2 border-t-2 text-center text-red-600">{data.total_fp}</td>
                                <td className="p-2 border-t-2 text-center text-orange-600">{data.total_fn}</td>
                                <td className="p-2 border-t-2 text-center">{data.total_tp + data.total_fp}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                {/* Légende */}
                <div className="mt-4 flex flex-wrap gap-4 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-green-400 rounded"></div>
                        <span>Vrais Positifs (détections correctes)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-red-400 rounded"></div>
                        <span>Faux Positifs (fausses alertes)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-orange-400 rounded"></div>
                        <span>Faux Négatifs (défauts manqués)</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
