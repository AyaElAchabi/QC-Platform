"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ExternalLink } from "lucide-react";
import axios from "axios";

interface LabelStudioButtonProps {
  projectId: string;
}

export function LabelStudioButton({ projectId }: LabelStudioButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const openLabelStudio = async () => {
    setIsLoading(true);
    
    try {
      const token = localStorage.getItem("mlops_access_token");
      
      // Essayer de récupérer l'URL existante
      let response = await axios.get(
        `http://localhost:8000/api/projects/${projectId}/labelstudio-url`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Ouvrir Label Studio dans un nouvel onglet
      window.open(response.data.url, "_blank");
      
    } catch (error: any) {
      if (error.response?.status === 404) {
        // Label Studio pas encore configuré
        if (confirm("Label Studio n'est pas encore configuré pour ce projet. Voulez-vous le configurer maintenant ?")) {
          await setupLabelStudio();
        }
      } else {
        alert("Erreur lors de l'ouverture de Label Studio");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const setupLabelStudio = async () => {
    try {
      const token = localStorage.getItem("mlops_access_token");
      const response = await axios.post(
        `http://localhost:8000/api/projects/${projectId}/setup-labelstudio`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Ouvrir Label Studio
      window.open(response.data.labelstudio_url, "_blank");
    } catch (error) {
      alert("Erreur lors de la configuration de Label Studio");
    }
  };

  return (
    <Button onClick={openLabelStudio} disabled={isLoading} variant="outline">
      <ExternalLink className="mr-2 h-4 w-4" />
      {isLoading ? "Chargement..." : "Annoter avec Label Studio"}
    </Button>
  );
}
