/**
 * Types et définitions pour le système de rôles et permissions
 * Correspond aux définitions du backend (backend/models/roles.py)
 */

export enum UserRole {
  ADMIN = "ADMIN",
  CHEF_OPERATOR = "CHEF_OPERATOR",
  OPERATOR = "OPERATOR",
  VIEWER = "VIEWER",
}

export enum Permission {
  // Projets
  PROJECT_CREATE = "PROJECT_CREATE",
  PROJECT_READ = "PROJECT_READ",
  PROJECT_UPDATE = "PROJECT_UPDATE",
  PROJECT_DELETE = "PROJECT_DELETE",
  PROJECT_ARCHIVE = "PROJECT_ARCHIVE",

  // Images
  IMAGE_UPLOAD = "IMAGE_UPLOAD",
  IMAGE_READ = "IMAGE_READ",
  IMAGE_UPDATE = "IMAGE_UPDATE",
  IMAGE_DELETE = "IMAGE_DELETE",
  IMAGE_BULK_DELETE = "IMAGE_BULK_DELETE",

  // Annotations
  ANNOTATION_CREATE = "ANNOTATION_CREATE",
  ANNOTATION_READ = "ANNOTATION_READ",
  ANNOTATION_UPDATE = "ANNOTATION_UPDATE",
  ANNOTATION_DELETE = "ANNOTATION_DELETE",
  ANNOTATION_REVIEW = "ANNOTATION_REVIEW",
  ANNOTATION_VALIDATE = "ANNOTATION_VALIDATE",

  // Modèles
  MODEL_READ = "MODEL_READ",
  MODEL_UPLOAD = "MODEL_UPLOAD",
  MODEL_DELETE = "MODEL_DELETE",
  MODEL_DEPLOY = "MODEL_DEPLOY",

  // Entraînement
  TRAINING_START = "TRAINING_START",
  TRAINING_READ = "TRAINING_READ",
  TRAINING_CANCEL = "TRAINING_CANCEL",
  TRAINING_DELETE = "TRAINING_DELETE",

  // Inférence
  INFERENCE_RUN = "INFERENCE_RUN",
  INFERENCE_READ = "INFERENCE_READ",
  INFERENCE_DELETE = "INFERENCE_DELETE",

  // XAI (Explainability)
  XAI_GENERATE = "XAI_GENERATE",
  XAI_READ = "XAI_READ",

  // Feedback
  FEEDBACK_CREATE = "FEEDBACK_CREATE",
  FEEDBACK_READ = "FEEDBACK_READ",
  FEEDBACK_RESOLVE = "FEEDBACK_RESOLVE",

  // Rapports
  REPORT_GENERATE = "REPORT_GENERATE",
  REPORT_READ = "REPORT_READ",
  REPORT_EXPORT = "REPORT_EXPORT",

  // Utilisateurs (Admin uniquement)
  USER_READ = "USER_READ",
  USER_CREATE = "USER_CREATE",
  USER_UPDATE = "USER_UPDATE",
  USER_DELETE = "USER_DELETE",
  USER_MANAGE_ROLES = "USER_MANAGE_ROLES",

  // Audit
  AUDIT_READ = "AUDIT_READ",
}

// Matrice des permissions par rôle (correspond au backend)
export const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  [UserRole.ADMIN]: Object.values(Permission), // Toutes les permissions

  [UserRole.CHEF_OPERATOR]: [
    // Projets
    Permission.PROJECT_CREATE,
    Permission.PROJECT_READ,
    Permission.PROJECT_UPDATE,
    Permission.PROJECT_DELETE,
    Permission.PROJECT_ARCHIVE,
    // Images
    Permission.IMAGE_UPLOAD,
    Permission.IMAGE_READ,
    Permission.IMAGE_UPDATE,
    Permission.IMAGE_DELETE,
    Permission.IMAGE_BULK_DELETE,
    // Annotations
    Permission.ANNOTATION_CREATE,
    Permission.ANNOTATION_READ,
    Permission.ANNOTATION_UPDATE,
    Permission.ANNOTATION_DELETE,
    Permission.ANNOTATION_REVIEW,
    Permission.ANNOTATION_VALIDATE,
    // Modèles
    Permission.MODEL_READ,
    Permission.MODEL_UPLOAD,
    Permission.MODEL_DELETE,
    Permission.MODEL_DEPLOY,
    // Entraînement
    Permission.TRAINING_START,
    Permission.TRAINING_READ,
    Permission.TRAINING_CANCEL,
    Permission.TRAINING_DELETE,
    // Inférence
    Permission.INFERENCE_RUN,
    Permission.INFERENCE_READ,
    Permission.INFERENCE_DELETE,
    // XAI
    Permission.XAI_GENERATE,
    Permission.XAI_READ,
    // Feedback
    Permission.FEEDBACK_CREATE,
    Permission.FEEDBACK_READ,
    Permission.FEEDBACK_RESOLVE,
    // Rapports
    Permission.REPORT_GENERATE,
    Permission.REPORT_READ,
    Permission.REPORT_EXPORT,
    // Audit
    Permission.AUDIT_READ,
  ],

  [UserRole.OPERATOR]: [
    // Projets (lecture seule)
    Permission.PROJECT_READ,
    // Images
    Permission.IMAGE_UPLOAD,
    Permission.IMAGE_READ,
    Permission.IMAGE_UPDATE,
    Permission.IMAGE_DELETE,
    // Annotations
    Permission.ANNOTATION_CREATE,
    Permission.ANNOTATION_READ,
    Permission.ANNOTATION_UPDATE,
    Permission.ANNOTATION_DELETE,
    // Modèles (lecture seule)
    Permission.MODEL_READ,
    // Entraînement
    Permission.TRAINING_START,
    Permission.TRAINING_READ,
    // Inférence
    Permission.INFERENCE_RUN,
    Permission.INFERENCE_READ,
    // XAI
    Permission.XAI_GENERATE,
    Permission.XAI_READ,
    // Feedback
    Permission.FEEDBACK_CREATE,
    Permission.FEEDBACK_READ,
    // Rapports (lecture seule)
    Permission.REPORT_READ,
  ],

  [UserRole.VIEWER]: [
    // Projets (lecture seule)
    Permission.PROJECT_READ,
    // Images (lecture seule)
    Permission.IMAGE_READ,
    // Annotations (lecture seule)
    Permission.ANNOTATION_READ,
    // Modèles (lecture seule)
    Permission.MODEL_READ,
    // Entraînement (lecture seule)
    Permission.TRAINING_READ,
    // Inférence (lecture seule)
    Permission.INFERENCE_READ,
    // XAI (lecture seule)
    Permission.XAI_READ,
    // Rapports (lecture seule)
    Permission.REPORT_READ,
  ],
};

// Hiérarchie des rôles (pour les promotions)
export const ROLE_HIERARCHY: Record<UserRole, number> = {
  [UserRole.VIEWER]: 0,
  [UserRole.OPERATOR]: 1,
  [UserRole.CHEF_OPERATOR]: 2,
  [UserRole.ADMIN]: 3,
};

// Badges de couleur par rôle
export const ROLE_COLORS: Record<UserRole, string> = {
  [UserRole.ADMIN]: "bg-violet-100 text-violet-600 border-violet-200",
  [UserRole.CHEF_OPERATOR]: "bg-indigo-100 text-indigo-600 border-indigo-200",
  [UserRole.OPERATOR]: "bg-emerald-100 text-emerald-600 border-emerald-200",
  [UserRole.VIEWER]: "bg-slate-100 text-slate-600 border-slate-200",
};

// Labels lisibles pour les rôles
export const ROLE_LABELS: Record<UserRole, string> = {
  [UserRole.ADMIN]: "Administrateur",
  [UserRole.CHEF_OPERATOR]: "Chef Opérateur",
  [UserRole.OPERATOR]: "Opérateur",
  [UserRole.VIEWER]: "Visualiseur",
};

// Descriptions des rôles
export const ROLE_DESCRIPTIONS: Record<UserRole, string> = {
  [UserRole.ADMIN]: "Accès complet à toutes les fonctionnalités, gestion des utilisateurs",
  [UserRole.CHEF_OPERATOR]: "Gestion complète des projets, modèles et entraînements",
  [UserRole.OPERATOR]: "Annotation, entraînement et inférence sur les projets",
  [UserRole.VIEWER]: "Consultation des projets, modèles et résultats",
};

/**
 * Vérifier si un utilisateur a une permission
 */
export function hasPermission(userRole: UserRole, permission: Permission): boolean {
  return ROLE_PERMISSIONS[userRole].includes(permission);
}

/**
 * Vérifier si un utilisateur a toutes les permissions spécifiées
 */
export function hasAllPermissions(userRole: UserRole, permissions: Permission[]): boolean {
  return permissions.every(p => hasPermission(userRole, p));
}

/**
 * Vérifier si un utilisateur a au moins une des permissions spécifiées
 */
export function hasAnyPermission(userRole: UserRole, permissions: Permission[]): boolean {
  return permissions.some(p => hasPermission(userRole, p));
}

/**
 * Vérifier si un rôle peut être promu vers un autre rôle
 */
export function canPromoteTo(currentRole: UserRole, targetRole: UserRole): boolean {
  return ROLE_HIERARCHY[targetRole] > ROLE_HIERARCHY[currentRole];
}

/**
 * Vérifier si un rôle peut être rétrogradé vers un autre rôle
 */
export function canDemoteTo(currentRole: UserRole, targetRole: UserRole): boolean {
  return ROLE_HIERARCHY[targetRole] < ROLE_HIERARCHY[currentRole];
}

/**
 * Obtenir toutes les permissions d'un rôle
 */
export function getPermissionsForRole(role: UserRole): Permission[] {
  return ROLE_PERMISSIONS[role];
}

/**
 * Obtenir les rôles disponibles pour la promotion (supérieurs au rôle actuel)
 */
export function getPromotableRoles(currentRole: UserRole): UserRole[] {
  const currentLevel = ROLE_HIERARCHY[currentRole];
  return Object.entries(ROLE_HIERARCHY)
    .filter(([_, level]) => level > currentLevel)
    .map(([role, _]) => role as UserRole);
}

/**
 * Obtenir les rôles disponibles pour la rétrogradation (inférieurs au rôle actuel)
 */
export function getDemotableRoles(currentRole: UserRole): UserRole[] {
  const currentLevel = ROLE_HIERARCHY[currentRole];
  return Object.entries(ROLE_HIERARCHY)
    .filter(([_, level]) => level < currentLevel)
    .map(([role, _]) => role as UserRole);
}
