'use client';

import { useEffect } from "react";

export function useRealtime(docId: string, onUpdate: (data: any) => void) {
  useEffect(() => {
    if (!docId) return;

    const ws = new WebSocket(ws://localhost:8000/ws/);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onUpdate(data);
    };

    return () => ws.close();
  }, [docId]);
}
