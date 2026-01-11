"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    BarChart3,
    Target,
    AlertTriangle,
    CheckCircle,
    XCircle,
    TrendingUp,
} from "lucide-react";

interface PerClassMetrics {
    tp: number;
    fp: number;
    fn: number;
    precision: number;
    recall: number;
    f1: number;
}

interface BusinessMetrics {
    per_class: Record<string, PerClassMetrics>;
    global: {
        total_tp: number;
        total_fp: number;
        total_fn: number;
        precision: number;
        recall: number;
        f1: number;
    };
}

interface CalibrationData {
    bins: number[];
    accuracy_per_bin: (number | null)[];
    confidence_per_bin: (number | null)[];
    count_per_bin: number[];
    ece: number;
}

interface IoUDistribution {
    values: number[];
    mean: number;
    std: number;
    min: number;
    max: number;
}

interface MetricsPanelProps {
    businessMetrics: BusinessMetrics | null;
    auroc: number | null;
    calibration: CalibrationData | null;
    iouDistribution: IoUDistribution | null;
    isLoading?: boolean;
}

export function MetricsPanel({
    businessMetrics,
    auroc,
    calibration,
    iouDistribution,
    isLoading = false,
}: MetricsPanelProps) {
    if (isLoading) {
        return (
            <Card>
                <CardContent className="py-8">
                    <div className="flex items-center justify-center">
                        <div className="animate-pulse text-muted-foreground">
                            Chargement des métriques...
                        </div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    const getECEInterpretation = (ece: number) => {
        if (ece <= 0.05) return { level: "Excellent", color: "bg-green-500", description: "Très bien calibré" };
        if (ece <= 0.10) return { level: "Bon", color: "bg-blue-500", description: "Bien calibré" };
        if (ece <= 0.15) return { level: "Modéré", color: "bg-yellow-500", description: "Calibration acceptable" };
        if (ece <= 0.25) return { level: "Faible", color: "bg-orange-500", description: "Mal calibré" };
        return { level: "Très faible", color: "bg-red-500", description: "Très mal calibré" };
    };

    const getAUROCInterpretation = (value: number) => {
        if (value >= 0.9) return { level: "Excellent", color: "text-green-600" };
        if (value >= 0.8) return { level: "Bon", color: "text-blue-600" };
        if (value >= 0.7) return { level: "Acceptable", color: "text-yellow-600" };
        if (value >= 0.6) return { level: "Faible", color: "text-orange-600" };
        return { level: "Insuffisant", color: "text-red-600" };
    };

    return (
        <div className="space-y-6">
            {/* Global Metrics Summary */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {/* AUROC */}
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">AUROC</p>
                                <p className={`text-2xl font-bold ${auroc ? getAUROCInterpretation(auroc).color : ""}`}>
                                    {auroc !== null ? (auroc * 100).toFixed(1) + "%" : "N/A"}
                                </p>
                                {auroc !== null && (
                                    <p className="text-xs text-muted-foreground">
                                        {getAUROCInterpretation(auroc).level}
                                    </p>
                                )}
                            </div>
                            <TrendingUp className="h-8 w-8 text-blue-500" />
                        </div>
                    </CardContent>
                </Card>

                {/* ECE */}
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">ECE (Calibration)</p>
                                <p className="text-2xl font-bold">
                                    {calibration ? (calibration.ece * 100).toFixed(1) + "%" : "N/A"}
                                </p>
                                {calibration && (
                                    <Badge className={`${getECEInterpretation(calibration.ece).color} text-white text-xs`}>
                                        {getECEInterpretation(calibration.ece).level}
                                    </Badge>
                                )}
                            </div>
                            <Target className="h-8 w-8 text-purple-500" />
                        </div>
                    </CardContent>
                </Card>

                {/* Precision */}
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Précision</p>
                                <p className="text-2xl font-bold text-green-600">
                                    {businessMetrics ? (businessMetrics.global.precision * 100).toFixed(1) + "%" : "N/A"}
                                </p>
                                <Progress
                                    value={businessMetrics ? businessMetrics.global.precision * 100 : 0}
                                    className="h-1 mt-2"
                                />
                            </div>
                            <CheckCircle className="h-8 w-8 text-green-500" />
                        </div>
                    </CardContent>
                </Card>

                {/* Recall */}
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Rappel</p>
                                <p className="text-2xl font-bold text-blue-600">
                                    {businessMetrics ? (businessMetrics.global.recall * 100).toFixed(1) + "%" : "N/A"}
                                </p>
                                <Progress
                                    value={businessMetrics ? businessMetrics.global.recall * 100 : 0}
                                    className="h-1 mt-2"
                                />
                            </div>
                            <BarChart3 className="h-8 w-8 text-blue-500" />
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* FP/FN Summary */}
            {businessMetrics && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                            <AlertTriangle className="h-5 w-5 text-orange-500" />
                            Faux Positifs / Faux Négatifs
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-3 gap-4 mb-4">
                            <div className="text-center p-4 bg-green-50 rounded-lg">
                                <div className="text-3xl font-bold text-green-600">
                                    {businessMetrics.global.total_tp}
                                </div>
                                <div className="text-sm text-muted-foreground">Vrais Positifs (TP)</div>
                            </div>
                            <div className="text-center p-4 bg-red-50 rounded-lg">
                                <div className="text-3xl font-bold text-red-600">
                                    {businessMetrics.global.total_fp}
                                </div>
                                <div className="text-sm text-muted-foreground">Faux Positifs (FP)</div>
                            </div>
                            <div className="text-center p-4 bg-orange-50 rounded-lg">
                                <div className="text-3xl font-bold text-orange-600">
                                    {businessMetrics.global.total_fn}
                                </div>
                                <div className="text-sm text-muted-foreground">Faux Négatifs (FN)</div>
                            </div>
                        </div>

                        <div className="text-sm text-muted-foreground">
                            <p>• <strong>TP</strong>: Défauts correctement détectés</p>
                            <p>• <strong>FP</strong>: Fausses alertes (détections incorrectes)</p>
                            <p>• <strong>FN</strong>: Défauts manqués (non détectés)</p>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Per-Class Metrics Table */}
            {businessMetrics && Object.keys(businessMetrics.per_class).length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Métriques par Classe</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Classe</TableHead>
                                    <TableHead className="text-center">TP</TableHead>
                                    <TableHead className="text-center">FP</TableHead>
                                    <TableHead className="text-center">FN</TableHead>
                                    <TableHead className="text-center">Précision</TableHead>
                                    <TableHead className="text-center">Rappel</TableHead>
                                    <TableHead className="text-center">F1</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {Object.entries(businessMetrics.per_class).map(([className, metrics]) => (
                                    <TableRow key={className}>
                                        <TableCell className="font-medium">{className}</TableCell>
                                        <TableCell className="text-center text-green-600">{metrics.tp}</TableCell>
                                        <TableCell className="text-center text-red-600">{metrics.fp}</TableCell>
                                        <TableCell className="text-center text-orange-600">{metrics.fn}</TableCell>
                                        <TableCell className="text-center">
                                            <Badge variant={metrics.precision > 0.8 ? "default" : "secondary"}>
                                                {(metrics.precision * 100).toFixed(1)}%
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-center">
                                            <Badge variant={metrics.recall > 0.8 ? "default" : "secondary"}>
                                                {(metrics.recall * 100).toFixed(1)}%
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-center">
                                            <Badge variant={metrics.f1 > 0.8 ? "default" : "secondary"}>
                                                {(metrics.f1 * 100).toFixed(1)}%
                                            </Badge>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            )}

            {/* IoU Distribution */}
            {iouDistribution && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Distribution IoU</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-4 gap-4">
                            <div className="text-center">
                                <div className="text-xl font-bold">{(iouDistribution.mean * 100).toFixed(1)}%</div>
                                <div className="text-sm text-muted-foreground">Moyenne</div>
                            </div>
                            <div className="text-center">
                                <div className="text-xl font-bold">{(iouDistribution.std * 100).toFixed(1)}%</div>
                                <div className="text-sm text-muted-foreground">Écart-type</div>
                            </div>
                            <div className="text-center">
                                <div className="text-xl font-bold">{(iouDistribution.min * 100).toFixed(1)}%</div>
                                <div className="text-sm text-muted-foreground">Min</div>
                            </div>
                            <div className="text-center">
                                <div className="text-xl font-bold">{(iouDistribution.max * 100).toFixed(1)}%</div>
                                <div className="text-sm text-muted-foreground">Max</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
