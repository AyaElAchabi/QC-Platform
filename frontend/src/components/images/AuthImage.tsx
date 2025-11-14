"use client";

import { useEffect, useState } from "react";

interface AuthImageProps {
  imageId: string;
  alt: string;
  className?: string;
}

export function AuthImage({ imageId, alt, className }: AuthImageProps) {
  const [imageSrc, setImageSrc] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const loadImage = async () => {
      try {
        const token = localStorage.getItem("mlops_access_token");
        
        const response = await fetch(
          `http://localhost:8000/api/images/${imageId}/file`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to load image");
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setImageSrc(url);
        setIsLoading(false);
      } catch (err) {
        console.error("Error loading image:", err);
        setError(true);
        setIsLoading(false);
      }
    };

    loadImage();

    // Cleanup
    return () => {
      if (imageSrc) {
        URL.revokeObjectURL(imageSrc);
      }
    };
  }, [imageId]);

  if (isLoading) {
    return (
      <div className={`${className} bg-gray-200 animate-pulse flex items-center justify-center`}>
        <span className="text-gray-400">Chargement...</span>
      </div>
    );
  }

  if (error || !imageSrc) {
    return (
      <div className={`${className} bg-gray-100 flex items-center justify-center`}>
        <span className="text-gray-400">❌</span>
      </div>
    );
  }

  return <img src={imageSrc} alt={alt} className={className} />;
}
