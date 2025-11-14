"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Trash2, Edit, Download, MoreVertical, Maximize2, Tag } from "lucide-react";
import { AuthImage } from "./AuthImage";
import type { Image } from "@/types/image";
import { formatDistanceToNow } from "date-fns";
import { fr } from "date-fns/locale";

interface ImageGalleryProps {
  images: Image[];
  onDelete?: (imageId: string) => void;
  onDeleteMultiple?: (imageIds: string[]) => void;
  onAnnotate?: (imageId: string) => void;
  isDeleting?: boolean;
}

export function ImageGallery({
  images,
  onDelete,
  onDeleteMultiple,
  onAnnotate,
  isDeleting,
}: ImageGalleryProps) {
  const [selectedImages, setSelectedImages] = useState<Set<string>>(new Set());
  const [lightboxImage, setLightboxImage] = useState<Image | null>(null);

  const toggleSelection = (imageId: string) => {
    const newSelected = new Set(selectedImages);
    if (newSelected.has(imageId)) {
      newSelected.delete(imageId);
    } else {
      newSelected.add(imageId);
    }
    setSelectedImages(newSelected);
  };

  const selectAll = () => {
    if (selectedImages.size === images.length) {
      setSelectedImages(new Set());
    } else {
      setSelectedImages(new Set(images.map((img) => img.id)));
    }
  };

  const handleDeleteMultiple = () => {
    if (selectedImages.size > 0 && onDeleteMultiple) {
      onDeleteMultiple(Array.from(selectedImages));
      setSelectedImages(new Set());
    }
  };

  const statusColors = {
    uploaded: "bg-blue-100 text-blue-800",
    annotated: "bg-green-100 text-green-800",
    processing: "bg-yellow-100 text-yellow-800",
  };

  return (
    <div className="space-y-4">
      {/* Actions Bar */}
      {images.length > 0 && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Checkbox
              checked={selectedImages.size === images.length}
              onCheckedChange={selectAll}
            />
            <span className="text-sm text-muted-foreground">
              {selectedImages.size > 0
                ? `${selectedImages.size} sélectionnée(s)`
                : `${images.length} image(s)`}
            </span>
          </div>

          {selectedImages.size > 0 && (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleDeleteMultiple}
              disabled={isDeleting}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Supprimer ({selectedImages.size})
            </Button>
          )}
        </div>
      )}

      {/* Image Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        {images.map((image) => (
          <Card
            key={image.id}
            className={`relative group overflow-hidden ${
              selectedImages.has(image.id) ? "ring-2 ring-blue-500" : ""
            }`}
          >
            <CardContent className="p-0">
              {/* Checkbox */}
              <div className="absolute top-2 left-2 z-10">
                <Checkbox
                  checked={selectedImages.has(image.id)}
                  onCheckedChange={() => toggleSelection(image.id)}
                  className="bg-white"
                />
              </div>

              {/* Annotation Count Badge */}
              {image.annotation_count > 0 && (
                <div className="absolute top-2 left-12 z-10">
                  <Badge variant="secondary" className="bg-green-500 text-white text-xs">
                    <Tag className="h-3 w-3 mr-1" />
                    {image.annotation_count}
                  </Badge>
                </div>
              )}

              {/* Actions Menu */}
              <div className="absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="secondary" size="icon" className="h-8 w-8">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => setLightboxImage(image)}>
                      <Maximize2 className="mr-2 h-4 w-4" />
                      Voir en grand
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => onAnnotate?.(image.id)}
                      disabled={!onAnnotate}
                    >
                      <Edit className="mr-2 h-4 w-4" />
                      {image.annotation_count > 0 ? "Modifier annotations" : "Annoter"}
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Download className="mr-2 h-4 w-4" />
                      Télécharger
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      className="text-red-600"
                      onClick={() => onDelete?.(image.id)}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Supprimer
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              {/* Image */}
              <div
                className="aspect-square bg-gray-100 cursor-pointer overflow-hidden"
                onClick={() => setLightboxImage(image)}
              >
                <AuthImage
                  imageId={image.id}
                  alt={image.filename}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Info */}
              <div className="p-2 space-y-1">
                <p className="text-xs font-medium truncate" title={image.filename}>
                  {image.filename}
                </p>
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className={statusColors[image.status]}>
                    {image.status}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(image.created_at), {
                      addSuffix: true,
                      locale: fr,
                    })}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Lightbox */}
      {lightboxImage && (
        <div
          className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
          onClick={() => setLightboxImage(null)}
        >
          <div className="relative max-w-5xl w-full" onClick={(e) => e.stopPropagation()}>
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-4 right-4 text-white hover:bg-white/20 z-10"
              onClick={() => setLightboxImage(null)}
            >
              ✕
            </Button>
            <div className="bg-white rounded-lg p-4">
              <div className="max-h-[70vh] flex items-center justify-center mb-4 bg-gray-100 rounded">
                <AuthImage
                  imageId={lightboxImage.id}
                  alt={lightboxImage.filename}
                  className="max-w-full max-h-[70vh] object-contain"
                />
              </div>
              
              {/* Info et Actions */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{lightboxImage.filename}</p>
                    <p className="text-sm text-muted-foreground">
                      {lightboxImage.width}x{lightboxImage.height}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Download className="mr-2 h-4 w-4" />
                      Télécharger
                    </Button>
                    <Button size="sm" onClick={() => {
                      setLightboxImage(null);
                      onAnnotate?.(lightboxImage.id);
                    }}>
                      <Edit className="mr-2 h-4 w-4" />
                      {lightboxImage.annotation_count > 0 ? "Voir/Modifier annotations" : "Annoter"}
                    </Button>
                  </div>
                </div>
                
                {/* Annotation Info */}
                {lightboxImage.annotation_count > 0 && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-green-800">
                      <Tag className="h-4 w-4" />
                      <span className="text-sm font-medium">
                        Cette image a {lightboxImage.annotation_count} annotation(s)
                      </span>
                    </div>
                    <p className="text-xs text-green-700 mt-1">
                      Cliquez sur "Voir/Modifier annotations" pour visualiser les bounding boxes
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
