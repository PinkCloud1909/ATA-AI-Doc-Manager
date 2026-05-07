"use client";

import { useEffect, useRef } from "react";
import { useChat } from "@/hooks/useChat";
import MessageBubble from "./MessageBubble";
import { VoiceInput } from "./VoiceInput";
import { useState, KeyboardEvent } from "react";

interface ChatInputProps {
  onSendMessage: (text: string) => void;
}

export default function ChatInput({ onSendMessage }: ChatInputProps) {
  const [text, setText] = useState("");
  const [isRecording, setIsRecording] = useState(false);

  // Hàm xử lý khi bấm gửi
  const handleSend = () => {
    if (text.trim() === "") return;
    onSendMessage(text);
    setText(""); // Xóa trắng ô nhập liệu sau khi gửi
  };

  // Bắt sự kiện nhấn Enter (nhưng cho phép Shift+Enter để xuống dòng)
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Ngăn việc tự động xuống dòng
      handleSend();
    }
  };

  // Giả lập tính năng Voice (Web Speech API thực tế sẽ cần nhiều code hơn)
  const handleVoiceInput = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      // Giả lập việc nhận diện giọng nói sau 2 giây
      setTimeout(() => {
        setText((prev) => prev + " (Nội dung giọng nói mô phỏng) ");
        setIsRecording(false);
      }, 2000);
    }
  };

  return (
    <div className="p-6 bg-gradient-to-t from-background via-background to-transparent">
      <div className="max-w-3xl mx-auto">
        <div
          className={`relative group bg-surface-container-low focus-within:bg-surface-container-lowest focus-within:shadow-xl transition-all duration-300 rounded-2xl p-2 border ${isRecording ? "border-error/50 shadow-error/10" : "border-surface-container-high/50 focus-within:border-tertiary/20"}`}
        >
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full bg-transparent border-none focus:ring-0 text-on-surface placeholder:text-on-surface-variant/50 px-4 py-3 pr-24 resize-none min-h-[56px] custom-scrollbar"
            placeholder={
              isRecording
                ? "Đang nghe..."
                : "Hỏi AI về tài liệu hoặc yêu cầu chấm điểm (Nhấn Enter để gửi)..."
            }
            rows={1}
          />
          <div className="absolute right-4 bottom-4 flex items-center gap-2">
            {/* Nút Micro */}
            <button
              onClick={handleVoiceInput}
              className={`w-10 h-10 flex items-center justify-center rounded-full transition-all ${isRecording ? "bg-error/10 text-error animate-pulse" : "text-on-surface-variant hover:text-tertiary hover:bg-tertiary/10"}`}
            >
              <span className="material-symbols-outlined">mic</span>
            </button>
            {/* Nút Gửi */}
            <button
              onClick={handleSend}
              disabled={text.trim() === ""}
              className="w-10 h-10 flex items-center justify-center bg-tertiary text-on-tertiary rounded-xl shadow-lg shadow-tertiary/20 hover:bg-tertiary-dim transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span
                className="material-symbols-outlined"
                style={{ fontVariationSettings: '"FILL" 1' }}
              >
                send
              </span>
            </button>
          </div>
        </div>
        <div className="flex justify-center mt-3">
          <p className="text-[10px] text-on-surface-variant/60 font-medium">
            Architect AI có thể mắc lỗi. Vui lòng kiểm tra lại các thông tin
            quan trọng.
          </p>
        </div>
      </div>
    </div>
  );
}
