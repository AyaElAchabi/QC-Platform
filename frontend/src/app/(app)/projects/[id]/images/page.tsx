"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import { useProject } from "@/lib/hooks/useProjects";
import { useImages } from "@/lib/hooks/useImages";
import { ImageUpload } from "@/components/images/ImageUpload";
import { ImageGallery } from "@/components/images/ImageGallery";
import { DatasetImport } from "@/components/dataset/DatasetImport";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Upload as UploadIcon, FolderArchive } from "lucide-react";
import Link from "next/link";

export default function ProjectImagesPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { data: project } = useProject(id);
  const { images, isLoading, uploadImages, deleteImage, deleteMultipleImages, isUploading, refetch } = useImages(id);
  const [activeTab, setActiveTab] = useState("gallery");

  const handleUpload = async (files: File[]) => {
    await uploadImages({ files });
    setActiveTab("gallery");
  };

  const handleDelete = async (imageId: string) => {
    if (confirm("Êtes-vous sûr de vouloir supprimer cette image ?")) {
      await deleteImage(imageId);
    }
  };

  const handleDeleteMultiple = async (imageIds: string[]) => {
    if (confirm(`Êtes-vous sûr de vouloir supprimer ${imageIds.length} image(s) ?`)) {
      await deleteMultipleImages(imageIds);
    }
  };

  const handleAnnotate = (imageId: string) => {
    router.push(`/projects/${id}/annotate/${imageId}`);
  };

  const handleDatasetImportSuccess = () => {
    refetch();
    setActiveTab("gallery");
  };

  if (!project) {
    return <div>Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href={`/projects/${id}`}>
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Images</h1>
            <p className="text-muted-foreground">{project.name}</p>
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="gallery">
            Galerie ({images.length})
          </TabsTrigger>
          <TabsTrigger value="upload">
            <UploadIcon className="mr-2 h-4 w-4" />
            Importer
          </TabsTrigger>
          <TabsTrigger value="dataset">
            <FolderArchive className="mr-2 h-4 w-4" />
            Dataset ZIP
          </TabsTrigger>
        </TabsList>

        <TabsContent value="gallery" className="space-y-4">
          {isLoading ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground">Chargement des images...</p>
            </div>
          ) : images.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-4">
                Aucune image pour le moment. Commencez par en uploader !
              </p>
              <div className="flex gap-2 justify-center">
                <Button onClick={() => setActiveTab("upload")}>
                  <UploadIcon className="mr-2 h-4 w-4" />
                  Importer des images
                </Button>
                <Button variant="outline" onClick={() => setActiveTab("dataset")}>
                  <FolderArchive className="mr-2 h-4 w-4" />
                  Importer un dataset
                </Button>
              </div>
            </div>
          ) : (
            <ImageGallery
              images={images}
              onDelete={handleDelete}
              onDeleteMultiple={handleDeleteMultiple}
              onAnnotate={handleAnnotate}
            />
          )}
        </TabsContent>

        <TabsContent value="upload">
          <ImageUpload onUpload={handleUpload} isUploading={isUploading} />
        </TabsContent>

        <TabsContent value="dataset">
          <DatasetImport projectId={id} onSuccess={handleDatasetImportSuccess} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
