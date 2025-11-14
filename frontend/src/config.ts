export const config = {
  site: {
    name: "MLOps QC Platform",
    description: "Plateforme de Contrôle Qualité Visuel par IA",
    url: process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000",
  },
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    timeout: 30000,
  },
  features: {
    enableAnnotation: true,
    enableTraining: true,
    enableXAI: true,
  },
  storage: {
    tokenKey: "mlops_access_token",
    refreshTokenKey: "mlops_refresh_token",
  },
} as const;

export type Config = typeof config;
