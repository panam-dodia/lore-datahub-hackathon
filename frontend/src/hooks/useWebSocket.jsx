import { useEffect, useRef, useState } from "react";

/**
 * Streams progress messages from /ws/excavation/{jobId}. Returns the
 * accumulated message log plus a `done` flag set when the socket closes.
 */
export function useWebSocket(jobId) {
  const [messages, setMessages] = useState([]);
  const [done, setDone] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    if (!jobId) return;

    setMessages([]);
    setDone(false);

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws/excavation/${jobId}`);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.error) {
        setMessages((prev) => [...prev, `Error: ${payload.error}`]);
        return;
      }
      setMessages((prev) => [...prev, payload.message]);
    };

    socket.onclose = () => setDone(true);

    return () => socket.close();
  }, [jobId]);

  return { messages, done };
}
