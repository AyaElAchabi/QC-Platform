"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Upload, FolderOpen, CheckCircle, XCircle } from "lucide-react";
import axios from "axios";

interface UploadDatasetDialogProps {
  projectId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function UploadDatasetDialog({
  projectId,
  open,
  onOpenChange,
}: UploadDatasetDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [importAnnotations, setImportAnnotations] = useState(true);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setAnalysis(null);

    // Analyser automatiquement
    await analyzeDataset(selectedFile);
  };

  const analyzeDataset = async (file: File) => {
    setIsAnalyzing(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("import_annotations", "true");

      const token = localStorage.getItem("mlops_access_token");
      const response = await axios.post(
        `http://localhost:8000/api/projects/${projectId}/upload-dataset`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setAnalysis(response.data);
    } catch (error) {
      console.error("Error analyzing dataset:", error);
      alert("Erreur lors de l'analyse du dataset");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleImport = async () => {
    if (!analysis) return;

    setIsImporting(true);

    try {
      const formData = new FormData();
      formData.append("extract_path", analysis.extract_path);
      formData.append("import_annotations", importAnnotations.toString());

      const token = localStorage.getItem("mlops_access_token");
      await axios.post(
        `http://localhost:8000/api/projects/${projectId}/import-dataset`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      alert("✅ Dataset importé avec succès !");
      onOpenChange(false);
      window.location.reload();
    } catch (error) {
      console.error("Error importing dataset:", error);
      alert("❌ Erreur lors de l'import du dataset");
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Importer un Dataset</DialogTitle>
          <DialogDescription>
            Uploadez un fichier ZIP contenant votre dataset (images + annotations optionnelles)
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* File Upload */}
          <div className="space-y-2">
            <Label>Fichier ZIP</Label>
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <input
                type="file"
                accept=".zip"
                onChange={handleFileChange}
                className="hidden"
                id="dataset-upload"
              />
              <label htmlFor="dataset-upload" className="cursor-pointer">
                {file ? (
                  <div className="flex items-center justify-center gap-2">
                    <FolderOpen className="h-6 w-6 text-blue-600" />
                    <span className="font-medium">{file.name}</span>
                  </div>
                ) : (
                  <div>
                    <Upload className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                    <p className="text-sm text-muted-foreground">
                      Cliquez pour sélectionner un fichier ZIP
                    </p>
                  </div>
                )}
              </label>
            </div>
          </div>

          {/* Analysis Result */}
          {isAnalyzing && (
            <div className="text-center py-4">
              <p className="text-sm text-muted-foreground">
                Analyse du dataset en cours...
              </p>
            </div>
          )}

          {analysis && (
            <div className="space-y-4 border rounded-lg p-4 bg-gray-50">
              <h3 className="font-semibold">Résumé du Dataset</h3>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Format</p>
                  <p className="font-medium uppercase">{analysis.format}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Images</p>
                  <p className="font-medium">{analysis.total_images}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Annotations</p>
                  <div className="flex items-center gap-2">
                    {analysis.has_annotations ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="font-medium text-green-600">
                          {analysis.annotated_images} images annotées
                        </span>
                      </>
                    ) : (
                      <>
                        <XCircle className="h-4 w-4 text-orange-600" />
                        <span className="font-medium text-orange-600">
                          Non annoté
                        </span>
                      </>
                    )}
                  </div>
                </div>
                {analysis.classes && analysis.classes.length > 0 && (
                  <div>
                    <p className="text-sm text-muted-foreground">Classes</p>
                    <p className="font-medium">{analysis.classes.join(", ")}</p>
                  </div>
                )}
              </div>

              {analysis.has_annotations && (
                <div className="flex items-center gap-2 pt-4 border-t">
                  <input
                    type="checkbox"
                    id="import-annotations"
                    checked={importAnnotations}
                    onChange={(e) => setImportAnnotations(e.target.checked)}
                    className="h-4 w-4"
                  />
                  <label htmlFor="import-annotations" className="text-sm">
                    Importer les annotations existantes
                  </label>
                </div>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Annuler
            </Button>
            <Button
              onClick={handleImport}
              disabled={!analysis || isImporting}
            >
              {isImporting ? "Import en cours..." : "Importer le Dataset"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
