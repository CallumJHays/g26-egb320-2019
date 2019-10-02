import { useState } from "react";

class VisionSystemResult {}

export class API {
  ws: WebSocket;
  results_cbs: ((VisionSystemResult) => void)[];

  constructor(ws: WebSocket) {
    this.ws = ws;
    this.results_cbs = [];
    this.ws.onmessage = event => {
      const results = JSON.parse(event.data);
      this.results_cbs.forEach(cb => cb(results));
    };
  }

  async setDesiredMotion(x, y, omega) {
    this.ws.send(JSON.stringify({ x, y, omega }));
  }

  getLiveStreamUrl = () => _wsUrl("live_stream");

  onVisionSystemResult(cb) {
    this.results_cbs.push(cb);
  }
}

export const useApi = ([api, setApi] = useState(null)) =>
  api
    ? api
    : (() => {
        const ws = new WebSocket(_wsUrl("remote_control"));
        ws.onopen = _event => setApi(new API(ws));
      })();

const _wsUrl = uri => {
  const url = new URL(`ws://localhost:8000/${uri}`, window.location.href);
  url.protocol = url.protocol.replace("http", "ws");
  return url.href;
};
