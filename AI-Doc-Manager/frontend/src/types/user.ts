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
  firebase_uid:         string   // Google UID từ Firebase
  username:             string
  email:                string
  last_password_changed: string
  roles:                UserRole[]
}
