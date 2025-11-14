"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Upload, X, FileImage, CheckCircle, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface UploadFile extends File {
  preview?: string;
  uploadProgress?: number;
  uploadStatus?: "pending" | "uploading" | "success" | "error";
  uploadError?: string;
}

interface ImageUploadProps {
  onUpload: (files: File[]) => Promise<void>;
  isUploading?: boolean;
  maxFiles?: number;
  maxSize?: number; // en MB
}

export function ImageUpload({ 
  onUpload, 
  isUploading = false,
  maxFiles = 100,
  maxSize = 10 
}: ImageUploadProps) {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) =>
      Object.assign(file, {
        preview: URL.createObjectURL(file),
        uploadProgress: 0,
        uploadStatus: "pending" as const,
      })
    );
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    maxSize: maxSize * 1024 * 1024,
    maxFiles,
    disabled: isUploading,
  });

  const removeFile = (index: number) => {
    setFiles((prev) => {
      const newFiles = [...prev];
      if (newFiles[index].preview) {
        URL.revokeObjectURL(newFiles[index].preview!);
      }
      newFiles.splice(index, 1);
      return newFiles;
    });
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    try {
      await onUpload(files);
      // Succès - nettoyer les fichiers
      files.forEach((file) => {
        if (file.preview) {
          URL.revokeObjectURL(file.preview);
        }
      });
      setFiles([]);
      setUploadProgress({});
    } catch (error) {
      console.error("Upload error:", error);
    }
  };

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <Card>
        <CardContent className="pt-6">
          <div
            {...getRootProps()}
            className={cn(
              "border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors",
              isDragActive
                ? "border-blue-500 bg-blue-50"
                : "border-gray-300 hover:border-gray-400",
              isUploading && "opacity-50 cursor-not-allowed"
            )}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            {isDragActive ? (
              <p className="text-lg font-medium">Déposez les images ici...</p>
            ) : (
              <>
                <p className="text-lg font-medium mb-2">
                  Glissez-déposez vos images ici
                </p>
                <p className="text-sm text-muted-foreground mb-4">
                  ou cliquez pour sélectionner des fichiers
                </p>
                <p className="text-xs text-muted-foreground">
                  JPEG, PNG (max {maxSize}MB par fichier, max {maxFiles} fichiers)
                </p>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Files Preview */}
      {files.length > 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">
                {files.length} fichier{files.length > 1 ? "s" : ""} sélectionné
                {files.length > 1 ? "s" : ""}
              </h3>
              <Button onClick={handleUpload} disabled={isUploading}>
                {isUploading ? (
                  <>
                    <Upload className="mr-2 h-4 w-4 animate-pulse" />
                    Upload en cours...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Uploader {files.length} image{files.length > 1 ? "s" : ""}
                  </>
                )}
              </Button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {files.map((file, index) => (
                <div key={index} className="relative group">
                  <div className="aspect-square rounded-lg overflow-hidden bg-gray-100">
                    <img
                      src={file.preview}
                      alt={file.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <Button
                    variant="destructive"
                    size="icon"
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6"
                    onClick={() => removeFile(index)}
                    disabled={isUploading}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                  <p className="text-xs mt-1 truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
