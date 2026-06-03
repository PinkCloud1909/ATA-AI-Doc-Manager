"use client"

import { KeyboardEvent, useRef, useState } from "react"
import { Mic, MicOff, Send } from "lucide-react"

type InputMode = "text" | "voice"

interface ChatInputProps {
  onSendMessage: (text: string, mode?: InputMode) => void
}

interface SpeechRecognitionEventLike extends Event {
  results: SpeechRecognitionResultList
}

interface SpeechRecognitionErrorEventLike extends Event {
  error?: string
}

interface SpeechRecognitionLike extends EventTarget {
  continuous: boolean
  interimResults: boolean
  lang: string
  onresult:
    | ((event: SpeechRecognitionEventLike) => void)
    | null
  onerror:
    | ((event: SpeechRecognitionErrorEventLike) => void)
    | null
  onend: (() => void) | null
  start: () => void
  stop: () => void
}

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike

function getSpeechRecognition(): SpeechRecognitionConstructor | null {
  if (typeof window === "undefined") return null
  const browserWindow = window as typeof window & {
    SpeechRecognition?: SpeechRecognitionConstructor
    webkitSpeechRecognition?: SpeechRecognitionConstructor
  }
  return browserWindow.SpeechRecognition ?? browserWindow.webkitSpeechRecognition ?? null
}

export default function ChatInput({ onSendMessage }: ChatInputProps) {
  const [text, setText] = useState("")
  const [isRecording, setIsRecording] = useState(false)
  const [voiceSupported, setVoiceSupported] = useState(true)
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null)

  const handleSend = (mode: InputMode = "text") => {
    const trimmed = text.trim()
    if (!trimmed) return
    onSendMessage(trimmed, mode)
    setText("")
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      handleSend("text")
    }
  }

  const stopRecording = () => {
    recognitionRef.current?.stop()
    recognitionRef.current = null
    setIsRecording(false)
  }

  const handleVoiceInput = () => {
    if (isRecording) {
      stopRecording()
      return
    }

    const Recognition = getSpeechRecognition()
    if (!Recognition) {
      setVoiceSupported(false)
      return
    }

    const recognition = new Recognition()
    recognition.lang = "vi-VN"
    recognition.continuous = false
    recognition.interimResults = true
    recognitionRef.current = recognition
    setIsRecording(true)

    let finalTranscript = ""
    recognition.onresult = (event) => {
      let interimTranscript = ""
      for (let i = event.results.length - 1; i >= 0; i -= 1) {
        const result = event.results[i]
        const transcript = result[0]?.transcript ?? ""
        if (result.isFinal) {
          finalTranscript = `${finalTranscript} ${transcript}`.trim()
        } else {
          interimTranscript = transcript
        }
      }
      setText((finalTranscript || interimTranscript).trim())
    }
    recognition.onerror = () => {
      setIsRecording(false)
    }
    recognition.onend = () => {
      setIsRecording(false)
      recognitionRef.current = null
      if (finalTranscript.trim()) {
        onSendMessage(finalTranscript.trim(), "voice")
        setText("")
      }
    }
    recognition.start()
  }

  return (
    <div className="bg-gradient-to-t from-background via-background to-transparent p-6">
      <div className="mx-auto max-w-3xl">
        <div
          className={`group relative rounded-2xl border bg-surface-container-low p-2 transition-all duration-300 focus-within:bg-surface-container-lowest focus-within:shadow-xl ${
            isRecording
              ? "border-error/50 shadow-error/10"
              : "border-surface-container-high/50 focus-within:border-tertiary/20"
          }`}
        >
          <textarea
            value={text}
            onChange={(event) => setText(event.target.value)}
            onKeyDown={handleKeyDown}
            className="custom-scrollbar min-h-[56px] w-full resize-none border-none bg-transparent px-4 py-3 pr-24 text-on-surface placeholder:text-on-surface-variant/50 focus:ring-0"
            placeholder={isRecording ? "Đang nghe..." : "Hỏi AI về tài liệu hoặc yêu cầu tạo runbook..."}
            rows={1}
          />
          <div className="absolute bottom-4 right-4 flex items-center gap-2">
            <button
              type="button"
              onClick={handleVoiceInput}
              title={voiceSupported ? "Nhập bằng giọng nói" : "Trình duyệt không hỗ trợ ghi âm"}
              className={`flex h-10 w-10 items-center justify-center rounded-full transition-all ${
                isRecording
                  ? "animate-pulse bg-error/10 text-error"
                  : "text-on-surface-variant hover:bg-tertiary/10 hover:text-tertiary"
              }`}
            >
              {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
            <button
              type="button"
              onClick={() => handleSend("text")}
              disabled={text.trim() === ""}
              title="Gửi"
              className="flex h-10 w-10 items-center justify-center rounded-xl bg-tertiary text-on-tertiary shadow-lg shadow-tertiary/20 transition-all hover:bg-tertiary-dim disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Send size={18} fill="currentColor" />
            </button>
          </div>
        </div>
        {!voiceSupported && (
          <div className="mt-3 text-center text-xs text-error">
            Trình duyệt hiện tại chưa hỗ trợ nhập giọng nói.
          </div>
        )}
      </div>
    </div>
  )
}
