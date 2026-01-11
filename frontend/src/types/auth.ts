import { UserRole, Permission } from "./roles";

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  updated_at?: string;
  last_login?: string;
}

export interface LoginDto {
  email: string;
  password: string;
}

export interface RegisterDto {
  email: string;
  password: string;
  role?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface UserListItem {
  id: string;
  email: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface UpdateUserDto {
  email?: string;
  full_name?: string;
  is_active?: boolean;
}

export interface ChangeRoleDto {
  new_role: UserRole;
}

export interface RoleInfo {
  name: UserRole;
  label: string;
  description: string;
  permissions: Permission[];
}

export interface PromotionCheckResult {
  can_promote: boolean;
  current_role: UserRole;
  target_role: UserRole;
  reason?: string;
}
