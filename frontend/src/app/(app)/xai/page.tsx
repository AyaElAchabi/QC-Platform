"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { XAIVisualization } from "@/components/xai/XAIVisualization";
import { Brain } from "lucide-react";

export default function XAIPage() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [imagePath, setImagePath] = useState<string>("");

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Brain className="h-8 w-8 text-purple-500" />
        <div>
          <h1 className="text-3xl font-bold">XAI - Explainable AI</h1>
          <p className="text-gray-600">
            Comprenez les décisions de vos modèles
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Image à analyser</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="image-upload">Uploader une image</Label>
              <Input
                id="image-upload"
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="mt-2"
              />
            </div>

            <div>
              <Label htmlFor="image-path">Ou entrer le chemin</Label>
              <Input
                id="image-path"
                value={imagePath}
                onChange={(e) => setImagePath(e.target.value)}
                placeholder="/path/to/image.jpg"
                className="mt-2"
              />
            </div>

            {selectedImage && (
              <div className="mt-4 rounded-lg border overflow-hidden">
                <img
                  src={selectedImage}
                  alt="Selected"
                  className="w-full h-auto"
                />
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>À propos</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div>
              <h3 className="font-semibold mb-2">Méthodes XAI</h3>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                <li><strong>Grad-CAM:</strong> Heatmap des zones importantes</li>
                <li><strong>Grad-CAM++:</strong> Version améliorée</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      {(selectedImage || imagePath) && (
        <XAIVisualization
          imageUrl={imagePath || selectedImage || ""}
        />
      )}
    </div>
  );
}
