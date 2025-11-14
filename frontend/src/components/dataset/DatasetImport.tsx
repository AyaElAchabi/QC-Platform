"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, FileArchive, CheckCircle, AlertCircle } from "lucide-react";
import axios from "axios";

interface DatasetImportProps {
  projectId: string;
  onSuccess?: () => void;
}

export function DatasetImport({ projectId, onSuccess }: DatasetImportProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const token = localStorage.getItem("mlops_access_token");
      const response = await axios.post(
        `http://localhost:8000/api/projects/${projectId}/import-dataset`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult(response.data);
      setFile(null);
      
      if (onSuccess) {
        setTimeout(() => onSuccess(), 2000);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur lors de l'import");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileArchive className="h-5 w-5" />
          Importer un Dataset Complet
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Formats supportés : COCO, YOLO, Pascal VOC, ou dossier d'images simple
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="border-2 border-dashed rounded-lg p-8 text-center">
          <input
            type="file"
            accept=".zip"
            onChange={handleFileChange}
            className="hidden"
            id="dataset-upload"
          />
          <label
            htmlFor="dataset-upload"
            className="cursor-pointer flex flex-col items-center gap-2"
          >
            <Upload className="h-12 w-12 text-muted-foreground" />
            <p className="text-sm font-medium">
              {file ? file.name : "Sélectionner un fichier ZIP"}
            </p>
            <p className="text-xs text-muted-foreground">
              Cliquez pour sélectionner ou glissez-déposez
            </p>
          </label>
        </div>

        {file && (
          <Button
            onClick={handleUpload}
            disabled={isUploading}
            className="w-full"
          >
            {isUploading ? "Import en cours..." : "Importer le Dataset"}
          </Button>
        )}

        {result && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-green-900">
                  Dataset importé avec succès !
                </p>
                <div className="mt-2 space-y-1 text-sm text-green-800">
                  <p>📦 Format détecté : <strong>{result.format.toUpperCase()}</strong></p>
                  <p>✅ {result.imported} image(s) importée(s)</p>
                  <p>📝 {result.annotated} image(s) avec annotations</p>
                  {result.skipped > 0 && (
                    <p>⚠️ {result.skipped} image(s) ignorée(s) (déjà présentes)</p>
                  )}
                  {result.classes && result.classes.length > 0 && (
                    <p>🏷️ Classes : {result.classes.join(", ")}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Erreur d'import</p>
                <p className="text-sm text-red-800 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
          <p className="font-medium text-blue-900 mb-2">📚 Formats supportés :</p>
          <ul className="space-y-1 text-blue-800">
            <li>• <strong>COCO</strong> : annotations.json + dossier images/</li>
            <li>• <strong>YOLO</strong> : fichiers .txt + data.yaml</li>
            <li>• <strong>Pascal VOC</strong> : fichiers .xml + images</li>
            <li>• <strong>Simple</strong> : juste des images (à annoter après)</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
