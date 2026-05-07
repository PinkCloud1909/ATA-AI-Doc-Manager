"use client";

import { useState, useRef, useEffect } from "react";
import MessageBubble from "@/components/chat/MessageBubble";
import ChatInput from "@/components/chat/ChatInput";
import ChatSidebar from "@/components/chat/ChatSidebar";

// Định nghĩa cấu trúc 1 tin nhắn
/*
// === DỮ LIỆU MOCK HỘI THOẠI ===
const MOCK_CHAT_HISTORY: ChatMessage[] = [
  {
    id: "welcome-1",
    role: "ai",
    text: "Chào bạn! Mình là AI Curator của Architect SOC. Bạn cần hỗ trợ phân tích hay tìm kiếm tài liệu nào hôm nay?",
    timestamp: "09:00 AM",
    badgeType: "generated",
  },
  {
    id: "user-1",
    role: "user",
    text: "Hãy phân tích tài liệu 'Kiến trúc hệ thống quản lý dân cư v1.2' và đánh giá mức độ bảo mật của các API.",
    timestamp: "09:05 AM",
  },
  {
    id: "ai-1",
    role: "ai",
    text: "Đã nhận diện tài liệu 'Kiến trúc hệ thống quản lý dân cư v1.2'. Qua phân tích kiến trúc ReactJS frontend và SpringBoot backend, hệ thống tổ chức luồng dữ liệu khá tốt. Tuy nhiên, phần kết nối đến MySQL hiện tại chưa thấy đề cập đến việc mã hóa dữ liệu nhạy cảm ở tầng Database.",
    timestamp: "09:06 AM",
    badgeType: "generated",
  },
  {
    id: "ai-2",
    role: "ai",
    text: "Trích xuất từ 'Tiêu chuẩn bảo mật Data nội bộ': Mọi kết nối đến cơ sở dữ liệu MySQL chứa thông tin người dùng đều phải cấu hình SSL/TLS và các API SpringBoot cần có cơ chế rate-limiting. \n\nĐiểm đánh giá hiện tại: 7.5/10. Bạn có muốn tạo Runbook để bổ sung cấu hình bảo mật này không?",
    timestamp: "09:06 AM",
    badgeType: "trusted",
  },
  {
    id: "user-2",
    role: "user",
    text: "Có, hãy tạo một kịch bản cập nhật cấu hình bảo mật và gen sẵn đoạn code config cho SpringBoot nhé.",
    timestamp: "09:08 AM",
  },
];*/
/*
export default function ChatPage() {
  // Khởi tạo state với dữ liệu mock
  const [messages, setMessages] = useState<ChatMessage[]>(MOCK_CHAT_HISTORY);

  // Ref để tự động cuộn xuống cuối đoạn chat
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Hàm xử lý khi nhận được tin nhắn từ ChatInput
  const handleSendMessage = (text: string) => {
    const currentTime = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    // 1. Lưu tin nhắn của User
    const newUserMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      text: text,
      timestamp: currentTime,
    };

    setMessages((prev) => [...prev, newUserMsg]);

    // 2. Giả lập AI phản hồi sau 1 giây
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        text: `Đã nhận được yêu cầu: "${text}". Hệ thống đang xử lý và tổng hợp thông tin, vui lòng đợi trong giây lát...`,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        badgeType: "generated",
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  };

  return (
    // Bọc toàn bộ trang bằng Flex ngang (row) để Sidebar nằm bên trái, Chat nằm bên phải
    <div className="flex h-full w-full overflow-hidden">
      {/* Cột 1: Lịch sử Chat */ /*}
      <ChatSidebar />

      {/* Cột 2: Không gian Chat chính */ /*}
      <main className="flex-1 flex flex-col h-full relative bg-background overflow-hidden">
        {/* Messages Area */ /*}
        <div className="flex-1 overflow-y-auto px-6 py-8 space-y-10 custom-scrollbar">
          {messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              role={msg.role}
              timestamp={msg.timestamp}
              badgeType={msg.badgeType}
            >
              <p className="text-[15px] leading-relaxed text-on-surface whitespace-pre-wrap">
                {msg.text}
              </p>
            </MessageBubble>
          ))}

          {/* Điểm neo để tự động cuộn tới */ /*}
          <div ref={messagesEndRef} />
        </div>

        {/* Truyền hàm handleSendMessage xuống Input */ /*}
        <ChatInput onSendMessage={handleSendMessage} />
      </main>
    </div>
  );
}
*/

// Khai báo component UI cho thẻ chấm điểm (Tách nhỏ ra cho dễ nhìn)
const ScoringCard = () => (
  <div className="mt-4 bg-white rounded-xl p-6 border border-surface-container-high shadow-sm w-full max-w-2xl">
    <div className="flex justify-between items-start mb-6">
      <div>
        <h4 className="font-headline font-bold text-lg text-on-surface">
          Chấm điểm tài liệu
        </h4>
        <p className="text-xs text-on-surface-variant mt-1">
          Phân tích bởi Architect AI v4.2
        </p>
      </div>
      <div className="px-3 py-1.5 rounded-xl border border-surface-container-high shadow-sm flex items-baseline gap-1 bg-white">
        <span className="text-2xl font-black font-headline text-tertiary">
          8.5
        </span>
        <span className="text-sm text-on-surface-variant font-bold">/10</span>
      </div>
    </div>

    <div className="space-y-3">
      <div className="flex gap-3 items-start">
        <span
          className="material-symbols-outlined text-[#4caf50] text-[20px] mt-0.5"
          style={{ fontVariationSettings: '"FILL" 1' }}
        >
          check_circle
        </span>
        <p className="text-sm text-on-surface-variant">
          Cấu trúc rõ ràng, đầy đủ các bước phân loại sự cố Tier 1 và Tier 2.
        </p>
      </div>
      <div className="flex gap-3 items-start">
        <span
          className="material-symbols-outlined text-[#4caf50] text-[20px] mt-0.5"
          style={{ fontVariationSettings: '"FILL" 1' }}
        >
          check_circle
        </span>
        <p className="text-sm text-on-surface-variant">
          Danh sách liên hệ khẩn cấp đã được cập nhật mới nhất (Verified).
        </p>
      </div>
      <div className="flex gap-3 items-start">
        <span className="material-symbols-outlined text-[#ff9800] text-[20px] mt-0.5">
          info
        </span>
        <p className="text-sm text-on-surface-variant">
          Cần bổ sung thêm kịch bản cho sự cố lỗi API bên thứ 3.
        </p>
      </div>
    </div>

    <div className="mt-6 flex flex-wrap gap-3">
      <button className="bg-[#2b3437] text-white px-5 py-2 rounded-lg text-sm font-semibold hover:opacity-90 transition-opacity">
        Lưu điểm vào hệ thống
      </button>
      <button className="bg-white border border-surface-container-high text-on-surface px-5 py-2 rounded-lg text-sm font-semibold hover:bg-surface-container-low transition-colors">
        Tạo Runbook từ hội thoại
      </button>
    </div>
  </div>
);

// Cấu trúc tin nhắn giờ cho phép text là ReactNode để nhúng UI phức tạp
interface ChatMessage {
  id: string;
  role: "user" | "ai";
  text: React.ReactNode;
  timestamp: string;
  badgeType?: "generated" | "trusted";
}

// === DỮ LIỆU MOCK HỘI THOẠI CHỨA SCORING CARD ===
const MOCK_CHAT_HISTORY: ChatMessage[] = [
  {
    id: "user-1",
    role: "user",
    text: 'Hãy phân tích tài liệu "Quy trình ứng cứu sự cố hạ tầng v2" và cho tôi biết điểm chất lượng của nó.',
    timestamp: "10:42 AM",
  },
  {
    id: "ai-1",
    role: "ai",
    text: (
      <>
        <p className="text-[15px] leading-relaxed text-on-surface mb-2">
          Đã nhận diện tài liệu. Tôi đang tiến hành phân tích dựa trên khung
          tiêu chuẩn ISO 27001 và các bài học kinh nghiệm từ Network Status tuần
          trước.
        </p>
        <ScoringCard />
      </>
    ),
    timestamp: "10:43 AM",
    badgeType: "generated",
  },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(MOCK_CHAT_HISTORY);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (text: string) => {
    const currentTime = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    const newUserMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      text: text,
      timestamp: currentTime,
    };

    setMessages((prev) => [...prev, newUserMsg]);

    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "ai",
        text: `Đang xử lý yêu cầu mới của bạn...`,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        badgeType: "generated",
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  };

  return (
    <div className="flex h-full w-full overflow-hidden bg-background">
      <ChatSidebar />
      <main className="flex-1 flex flex-col h-full relative overflow-hidden">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-8 space-y-10 custom-scrollbar">
          {messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              role={msg.role}
              timestamp={msg.timestamp}
              badgeType={msg.badgeType}
            >
              {/* Render trực tiếp ReactNode thay vì chỉ string */}
              {msg.text}
            </MessageBubble>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <ChatInput onSendMessage={handleSendMessage} />
      </main>
    </div>
  );
}
