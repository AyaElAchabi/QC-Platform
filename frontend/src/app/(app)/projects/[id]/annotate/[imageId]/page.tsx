"use client";

import { use, useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useProject } from "@/lib/hooks/useProjects";
import { annotationsApi } from "@/lib/api/annotations";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Save, Trash2 } from "lucide-react";
import Link from "next/link";
import axios from "axios";

interface BoundingBox {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  class_name: string;
  color: string;
}

export default function AnnotatePage({ 
  params 
}: { 
  params: Promise<{ id: string; imageId: string }> 
}) {
  const { id: projectId, imageId } = use(params);
  const router = useRouter();
  const { data: project } = useProject(projectId);
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [boxes, setBoxes] = useState<BoundingBox[]>([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [currentClass, setCurrentClass] = useState("");
  const [scale, setScale] = useState(1);
  
  // Charger les annotations existantes
  useEffect(() => {
    const loadExistingAnnotations = async () => {
      try {
        const token = localStorage.getItem("mlops_access_token");
        const response = await axios.get(
          `http://localhost:8000/api/images/${imageId}/annotations`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        
        if (response.data && response.data.length > 0) {
          // Convertir les annotations en boxes
          const existingBoxes = response.data.map((ann: any) => {
            const classObj = project?.classes?.find((c: any) => c.name === ann.class_name);
            return {
              id: ann.id,
              x: ann.bbox.x,
              y: ann.bbox.y,
              width: ann.bbox.width,
              height: ann.bbox.height,
              class_name: ann.class_name,
              color: classObj?.color || "#ef4444",
            };
          });
          
          setBoxes(existingBoxes);
          console.log(`✅ ${existingBoxes.length} annotations chargées`);
        }
      } catch (error) {
        console.error("Error loading annotations:", error);
      }
    };
    
    if (project && imageId) {
      loadExistingAnnotations();
    }
  }, [imageId, project]);
  
  // Définir la première classe par défaut
  useEffect(() => {
    if (project?.classes && project.classes.length > 0 && !currentClass) {
      setCurrentClass(project.classes[0].name);
    }
  }, [project, currentClass]);
  
  // Charger l'image
  useEffect(() => {
    const loadImage = async () => {
      setIsLoading(true);
      const token = localStorage.getItem("mlops_access_token");
      const response = await fetch(
        `http://localhost:8000/api/images/${imageId}/file`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const img = new Image();
        img.onload = () => {
          setImage(img);
          const canvas = canvasRef.current;
          if (canvas) {
            const scaleX = canvas.width / img.width;
            const scaleY = canvas.height / img.height;
            setScale(Math.min(scaleX, scaleY, 1));
          }
          setIsLoading(false);
        };
        img.src = url;
      }
    };
    
    loadImage();
  }, [imageId]);
  
  // Dessiner sur le canvas
  useEffect(() => {
    if (!image || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const scaledWidth = image.width * scale;
    const scaledHeight = image.height * scale;
    const offsetX = (canvas.width - scaledWidth) / 2;
    const offsetY = (canvas.height - scaledHeight) / 2;
    
    ctx.drawImage(image, offsetX, offsetY, scaledWidth, scaledHeight);
    
    // Dessiner les boxes
    boxes.forEach((box) => {
      ctx.strokeStyle = box.color;
      ctx.lineWidth = 3;
      ctx.strokeRect(
        offsetX + box.x * scale,
        offsetY + box.y * scale,
        box.width * scale,
        box.height * scale
      );
      
      ctx.fillStyle = box.color;
      const textWidth = ctx.measureText(box.class_name).width;
      ctx.fillRect(
        offsetX + box.x * scale,
        offsetY + box.y * scale - 22,
        textWidth + 12,
        22
      );
      ctx.fillStyle = "white";
      ctx.font = "bold 14px sans-serif";
      ctx.fillText(
        box.class_name,
        offsetX + box.x * scale + 6,
        offsetY + box.y * scale - 6
      );
    });
  }, [image, boxes, scale]);
  
  const getMousePos = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !image) return { x: 0, y: 0 };
    
    const rect = canvas.getBoundingClientRect();
    const scaledWidth = image.width * scale;
    const scaledHeight = image.height * scale;
    const offsetX = (canvas.width - scaledWidth) / 2;
    const offsetY = (canvas.height - scaledHeight) / 2;
    
    return {
      x: (e.clientX - rect.left - offsetX) / scale,
      y: (e.clientY - rect.top - offsetY) / scale,
    };
  };
  
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const pos = getMousePos(e);
    setStartPos(pos);
    setIsDrawing(true);
  };
  
  const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !project) return;
    
    const endPos = getMousePos(e);
    const width = Math.abs(endPos.x - startPos.x);
    const height = Math.abs(endPos.y - startPos.y);
    
    if (width > 10 && height > 10) {
      const currentClassObj = project.classes?.find((c: any) => c.name === currentClass);
      
      const newBox: BoundingBox = {
        id: Date.now().toString(),
        x: Math.min(startPos.x, endPos.x),
        y: Math.min(startPos.y, endPos.y),
        width,
        height,
        class_name: currentClass,
        color: currentClassObj?.color || "#ef4444",
      };
      
      setBoxes([...boxes, newBox]);
    }
    
    setIsDrawing(false);
  };
  
  const handleSave = async () => {
    try {
      setIsSaving(true);
      
      const annotations = boxes.map(box => ({
        class_name: box.class_name,
        bbox: {
          x: box.x,
          y: box.y,
          width: box.width,
          height: box.height,
        },
      }));
      
      await annotationsApi.save(imageId, annotations);
      
      alert(`✅ ${boxes.length} annotation(s) sauvegardée(s) avec succès !`);
      
      router.push(`/projects/${projectId}/images`);
    } catch (error) {
      console.error("Error saving annotations:", error);
      alert("❌ Erreur lors de la sauvegarde des annotations");
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleDelete = (id: string) => {
    setBoxes(boxes.filter((box) => box.id !== id));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p>Chargement de l'image...</p>
      </div>
    );
  }

  if (!project) return <div>Chargement...</div>;

  if (!project.classes || project.classes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <h2 className="text-2xl font-bold mb-4">Aucune classe définie</h2>
        <p className="text-muted-foreground mb-4">
          Veuillez d'abord définir des classes de défauts pour ce projet
        </p>
        <Link href={`/projects/${projectId}`}>
          <Button>Retour au projet</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      <div className="border-b p-4 flex items-center justify-between bg-white shadow-sm">
        <div className="flex items-center gap-4">
          <Link href={`/projects/${projectId}/images`}>
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-xl font-bold">Annotation d'image</h1>
            <p className="text-sm text-muted-foreground">{project.name}</p>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setBoxes([])}>
            <Trash2 className="mr-2 h-4 w-4" />
            Tout effacer
          </Button>
          <Button onClick={handleSave} disabled={boxes.length === 0 || isSaving}>
            <Save className="mr-2 h-4 w-4" />
            {isSaving ? "Sauvegarde..." : `Sauvegarder (${boxes.length})`}
          </Button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 p-6 flex items-center justify-center">
          <canvas
            ref={canvasRef}
            width={950}
            height={700}
            className="border-2 border-gray-300 bg-white shadow-xl rounded cursor-crosshair"
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
          />
        </div>

        <div className="w-[550px] border-l bg-white shadow-lg overflow-y-auto flex-shrink-0">
          <div className="p-8 space-y-6">
            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="text-xl">Classes de défauts</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 pt-0">
                {project.classes.map((cls: any) => (
                  <Button
                    key={cls.name}
                    variant={currentClass === cls.name ? "default" : "outline"}
                    className="w-full justify-start h-auto py-4"
                    onClick={() => setCurrentClass(cls.name)}
                  >
                    <div
                      className="w-5 h-5 rounded-full mr-4 flex-shrink-0"
                      style={{ backgroundColor: cls.color }}
                    />
                    <span className="text-lg font-medium">{cls.name}</span>
                  </Button>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="text-xl">Instructions</CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <ol className="space-y-3 list-decimal list-inside">
                  <li className="text-sm">Sélectionnez une classe</li>
                  <li className="text-sm">Cliquez et glissez sur l'image</li>
                  <li className="text-sm">Relâchez pour finaliser</li>
                  <li className="text-sm">Répétez pour tous les défauts</li>
                  <li className="text-sm">Cliquez "Sauvegarder"</li>
                </ol>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="text-xl">
                  Annotations ({boxes.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                {boxes.length === 0 ? (
                  <p className="text-base text-muted-foreground text-center py-8">
                    Aucune annotation
                  </p>
                ) : (
                  <div className="space-y-3">
                    {boxes.map((box, idx) => (
                      <div
                        key={box.id}
                        className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                      >
                        <div className="flex items-center gap-4">
                          <div
                            className="w-6 h-6 rounded flex-shrink-0"
                            style={{ backgroundColor: box.color }}
                          />
                          <div>
                            <p className="text-base font-medium">{box.class_name}</p>
                            <p className="text-sm text-muted-foreground">
                              Boîte #{idx + 1}
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-9 w-9 text-red-600 hover:bg-red-50 flex-shrink-0"
                          onClick={() => handleDelete(box.id)}
                        >
                          <Trash2 className="h-5 w-5" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
