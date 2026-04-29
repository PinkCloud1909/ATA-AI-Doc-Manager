import { NextResponse } from "next/server"

// Mock user data
const mockUser = {
  id: "1",
  email: "admin@company.com",
  displayName: "Admin User",
  role: "admin",
  permissions: ["read", "write", "delete", "manage_users"],
}

export async function GET() {
  return NextResponse.json(mockUser)
}