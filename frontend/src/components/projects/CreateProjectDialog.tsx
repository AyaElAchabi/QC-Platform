"use client";

import { useState } from "react";
import { useCreateProject } from "@/lib/hooks/useProjects";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, X } from "lucide-react";

interface CreateProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const DEFAULT_COLORS = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#14b8a6"];

export function CreateProjectDialog({ open, onOpenChange }: CreateProjectDialogProps) {
  const createProject = useCreateProject();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [classes, setClasses] = useState<{ name: string; color: string }[]>([]);
  const [newClassName, setNewClassName] = useState("");

  const handleAddClass = () => {
    if (newClassName.trim()) {
      const color = DEFAULT_COLORS[classes.length % DEFAULT_COLORS.length];
      setClasses([...classes, { name: newClassName.trim(), color }]);
      setNewClassName("");
    }
  };

  const handleRemoveClass = (index: number) => {
    setClasses(classes.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await createProject.mutateAsync({
        name,
        description,
        task_type: "detection",
        classes,
      });
      
      setName("");
      setDescription("");
      setClasses([]);
      onOpenChange(false);
    } catch (error) {
      console.error("Error creating project:", error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Créer un nouveau projet</DialogTitle>
          <DialogDescription>
            Définissez les informations et les classes de défauts pour votre projet
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name">Nom du projet *</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Détection Fissures - Pièces Métalliques"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Décrivez brièvement votre projet..."
              rows={3}
            />
          </div>

          <div className="space-y-4">
            <Label>Classes de défauts *</Label>
            <p className="text-sm text-muted-foreground">
              Définissez les types de défauts que vous souhaitez détecter
            </p>
            
            <div className="flex gap-2">
              <Input
                value={newClassName}
                onChange={(e) => setNewClassName(e.target.value)}
                placeholder="Ex: crack, rust, scratch..."
                onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), handleAddClass())}
              />
              <Button type="button" onClick={handleAddClass} variant="outline">
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            {classes.length > 0 && (
              <div className="space-y-2 border rounded-lg p-4">
                {classes.map((cls, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 border rounded hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-6 h-6 rounded"
                        style={{ backgroundColor: cls.color }}
                      />
                      <span className="font-medium">{cls.name}</span>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => handleRemoveClass(index)}
                      className="h-8 w-8 text-red-600 hover:text-red-700"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}

            {classes.length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-4 border rounded-lg">
                Ajoutez au moins une classe de défaut
              </p>
            )}
          </div>

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Annuler
            </Button>
            <Button type="submit" disabled={!name || classes.length === 0}>
              Créer le projet
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
