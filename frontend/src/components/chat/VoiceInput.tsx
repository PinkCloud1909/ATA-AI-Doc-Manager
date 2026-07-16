"use client"

import { useState, useRef } from "react"
import { toast } from "sonner"

// Web Speech API type declarations
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList
  resultIndex: number
}

interface SpeechRecognitionResultList {
  length: number
  item(index: number): SpeechRecognitionResult
  [index: number]: SpeechRecognitionResult
}

interface SpeechRecognitionResult {
  length: number
  item(index: number): SpeechRecognitionAlternative
  [index: number]: SpeechRecognitionAlternative
  isFinal: boolean
}

interface SpeechRecognitionAlternative {
  transcript: string
  confidence: number
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string
  message: string
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition
    webkitSpeechRecognition: new () => SpeechRecognition
  }
}

interface SpeechRecognition extends EventTarget {
  lang: string
  continuous: boolean
  interimResults: boolean
  onresult: ((event: SpeechRecognitionEvent) => void) | null
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null
  onend: (() => void) | null
  start(): void
  stop(): void
  abort(): void
}

interface Props {
  onTranscript: (text: string) => void
}

export function VoiceInput({ onTranscript }: Props) {
  const [isRecording, setIsRecording] = useState(false)
  const recognitionRef = useRef<SpeechRecognition | null>(null)

  const toggle = () => {
    if (isRecording) {
      recognitionRef.current?.stop()
      setIsRecording(false)
      return
    }

    const SpeechRecognition =
      window.SpeechRecognition ?? window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      toast.error("Trình duyệt không hỗ trợ nhận giọng nói")
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang       = "vi-VN"
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript
      onTranscript(transcript)
    }

    recognition.onerror = () => {
      toast.error("Lỗi nhận giọng nói. Vui lòng thử lại.")
      setIsRecording(false)
    }

    recognition.onend = () => setIsRecording(false)

    recognitionRef.current = recognition
    recognition.start()
    setIsRecording(true)
  }

  return (
    <button
      type="button"
      onClick={toggle}
      title={isRecording ? "Dừng ghi âm" : "Nhấn để nói"}
      className={`p-2 rounded-lg transition-colors shrink-0
        ${isRecording
          ? "bg-red-100 text-red-600 animate-pulse"
          : "text-slate-400 hover:text-slate-600 hover:bg-slate-100"
        }`}
    >
      🎙
    </button>
  )
}
