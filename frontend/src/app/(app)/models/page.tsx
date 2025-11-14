"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Plus } from "lucide-react";
import Link from "next/link";

export default function ModelsPage() {
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
            <div className="text-3xl font-bold">0</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              En Production
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              En Entraînement
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">0</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="flex flex-col items-center justify-center py-16">
          <Brain className="h-16 w-16 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">Aucun modèle</h3>
          <p className="text-muted-foreground mb-4 text-center max-w-md">
            Entraînez votre premier modèle YOLOv8 pour détecter automatiquement les défauts
          </p>
          <div className="text-sm text-muted-foreground">
            Module d'entraînement disponible prochainement
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
