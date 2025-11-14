export interface User {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
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
