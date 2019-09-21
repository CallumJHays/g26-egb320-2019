import { useState } from "react";

export class API {
  ws: WebSocket;

  constructor(ws: WebSocket) {
    this.ws = ws;
  }

  async setDesiredMotion(x, y, omega) {
    this.ws.send(JSON.stringify({ x, y, omega }));
  }
}

export const useAPI = ([api, setApi] = useState(null)) =>
  api
    ? api
    : (() => {
        const url = new URL(
          "ws://localhost:8080/remote_control",
          window.location.href
        );
        url.protocol = url.protocol.replace("http", "ws");
        const ws = new WebSocket(url.href);
        ws.onopen = _event => setApi(new API(ws));
      })();
