/**
 * lib/gcs/index.ts
 *
 * Tiện ích làm việc với Google Cloud Storage từ phía frontend.
 *
 * NOTE: Upload trực tiếp từ browser lên GCS dùng Signed URL (V4).
 * Signed URL được backend tạo ra → frontend dùng để PUT file thẳng lên GCS
 * mà không cần đi qua backend server (giảm tải, tăng tốc độ upload lớn).
 *
 * Luồng upload:
 *   1. Frontend gọi POST /documents/signed-upload-url { filename, content_type }
 *   2. Backend tạo V4 Signed URL (TTL 15 phút) và trả về
 *   3. Frontend PUT file trực tiếp lên GCS bằng Signed URL
 *   4. Frontend gọi POST /documents/confirm-upload { gcs_path, metadata }
 *   5. Backend tạo record trong PostgreSQL
 */

const GCS_BASE =
  process.env.NEXT_PUBLIC_GCS_BASE_URL ??
  `https://storage.googleapis.com/${process.env.NEXT_PUBLIC_GCS_BUCKET_NAME}`

// ── URL Builders ─────────────────────────────────────────────────────────────

/**
 * Tạo URL public để đọc file từ GCS.
 * Chỉ dùng khi bucket có IAM public hoặc object có allUsers read.
 */
export function gcsPublicUrl(gcsPath: string): string {
  // gcsPath dạng: "documents/group-id/v2/filename.pdf"
  const clean = gcsPath.replace(/^gs:\/\/[^/]+\//, "")
  return `${GCS_BASE}/${clean}`
}

/**
 * Kiểm tra xem file_link có phải GCS path hay không.
 */
export function isGcsPath(link: string): boolean {
  return link.startsWith("gs://") || link.includes("storage.googleapis.com")
}

/**
 * Lấy tên file từ GCS path hoặc URL.
 * "documents/group/v1/my-runbook.pdf" → "my-runbook.pdf"
 */
export function gcsFilename(gcsPath: string): string {
  return gcsPath.split("/").pop() ?? gcsPath
}

/**
 * Lấy extension từ filename.
 */
export function fileExtension(filename: string): string {
  return filename.split(".").pop()?.toLowerCase() ?? ""
}

export function isPdf(filename: string): boolean {
  return fileExtension(filename) === "pdf"
}

export function isDocx(filename: string): boolean {
  return ["docx", "doc"].includes(fileExtension(filename))
}

// ── Direct Upload (Signed URL) ────────────────────────────────────────────────

export interface SignedUploadUrlResponse {
  signed_url:  string   // V4 Signed URL để PUT
  gcs_path:    string   // path trong bucket, dùng để confirm sau khi upload
  expires_at:  string   // ISO timestamp hết hạn
}

/**
 * Upload file trực tiếp lên GCS bằng Signed URL.
 * @param signedUrl   - URL lấy từ backend
 * @param file        - File object từ input/drag-drop
 * @param onProgress  - Callback phần trăm upload (0–100)
 */
export async function uploadToGcs(
  signedUrl: string,
  file: File,
  onProgress?: (pct: number) => void,
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    xhr.upload.addEventListener("progress", (e) => {
      if (onProgress && e.lengthComputable) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    })

    xhr.addEventListener("load", () => {
      // GCS trả về 200 hoặc 201 khi thành công
      if (xhr.status >= 200 && xhr.status < 300) resolve()
      else reject(new Error(`GCS upload failed: ${xhr.status} ${xhr.statusText}`))
    })

    xhr.addEventListener("error", () => reject(new Error("Network error during GCS upload")))

    xhr.open("PUT", signedUrl)
    xhr.setRequestHeader("Content-Type", file.type)
    // GCS Signed URL yêu cầu Content-Type match chính xác lúc ký
    xhr.send(file)
  })
}

// ── File Size Formatter ───────────────────────────────────────────────────────

export function formatFileSize(bytes: number): string {
  if (bytes < 1024)         return `${bytes} B`
  if (bytes < 1024 ** 2)   return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 ** 3)   return `${(bytes / 1024 ** 2).toFixed(1)} MB`
  return `${(bytes / 1024 ** 3).toFixed(2)} GB`
}
