import { NextResponse } from "next/server"

export async function GET(request: Request) {
  const backendUrl = process.env.BACKEND_URL || "http://localhost:8000"
  const authorization = request.headers.get("authorization")

  const response = await fetch(`${backendUrl}/api/v1/auth/me`, {
    headers: authorization ? { Authorization: authorization } : undefined,
    cache: "no-store",
  })

  const data = await response.json().catch(() => null)
  return NextResponse.json(data, { status: response.status })
}
