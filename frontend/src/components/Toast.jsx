import { createContext, useCallback, useContext, useState } from "react";

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [items, setItems] = useState([]);

  const dismiss = useCallback((id) => {
    setItems((arr) => arr.filter((t) => t.id !== id));
  }, []);

  const push = useCallback((message, kind = "info") => {
    const id = Math.random().toString(36).slice(2);
    setItems((arr) => [...arr, { id, message, kind }]);
    setTimeout(() => dismiss(id), 4000);
  }, [dismiss]);

  return (
    <ToastContext.Provider value={{ push, dismiss }}>
      {children}
      <div style={{
        position: "fixed", right: 16, bottom: 16, display: "flex",
        flexDirection: "column", gap: 8, zIndex: 100, maxWidth: 360,
      }}>
        {items.map((t) => (
          <div
            key={t.id}
            onClick={() => dismiss(t.id)}
            className={`toast toast-${t.kind}`}
            style={{
              background: t.kind === "error" ? "#3a1a1a" : t.kind === "success" ? "#143923" : "#15202d",
              border: `1px solid ${t.kind === "error" ? "#ef4444" : t.kind === "success" ? "#22c55e" : "#243447"}`,
              color: "#e6edf3", padding: "10px 14px", borderRadius: 8, cursor: "pointer",
              boxShadow: "0 6px 18px rgba(0,0,0,0.35)", fontSize: 14,
            }}
          >
            {t.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used inside <ToastProvider>");
  return ctx;
}
