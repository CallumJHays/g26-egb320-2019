import { useState } from "react";

export class API {
  ws: WebSocket;

  constructor(ws: WebSocket) {
    this.ws = ws;
  }

  async setDesiredMotion(x, y, omega) {
    this.ws.send(JSON.stringify({ x, y, omega }));
  }

  getLivestreamUrl = () => _wsUrl("live_stream");
}

export const useAPI = ([api, setApi] = useState(null)) =>
  api
    ? api
    : (() => {
        const ws = new WebSocket(_wsUrl("remote_control"));
        ws.onopen = _event => setApi(new API(ws));
      })();

const _wsUrl = uri => {
  const url = new URL(`ws://localhost:8080/${uri}`, window.location.href);
  url.protocol = url.protocol.replace("http", "ws");
  return url.href;
};
