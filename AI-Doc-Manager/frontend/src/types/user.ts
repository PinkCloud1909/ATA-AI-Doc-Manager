// types/user.ts

export interface Privilege {
  id:           string
  role_id:      string
  api_endpoint: string
  is_allowed:   boolean
}

export interface Role {
  id:           string
  role_name:    string
  description:  string
  privileges?:  Privilege[]
}

export interface UserRole {
  id:          string
  user_id:     string
  role_id:     string
  role:        Role
  assigned_by: string
  assigned_at: string
}

export interface User {
  id:                   string
  firebase_uid?:        string   // Chỉ có khi dùng Firebase Auth
  username:             string
  email?:               string
  last_password_changed?: string
  roles:                Array<UserRole | string>

  // Optional fields for UI display and auth profile
  displayName?:        string
  photoURL?:           string
  phoneNumber?:        string
  role?:               string
  permissions?:        string[]
}
