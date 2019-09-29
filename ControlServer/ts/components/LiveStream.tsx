import styled from "styled-components";
import { useEffect, createRef } from "react";
import { useApi } from "../api";
import WSAvcPlayer from "ws-avc-player";

const LiveStreamContainer = styled.div`
  position: absolute;
  top: 0;
  right: 0;
  width: 25vw;
  height: 30vh
  v-index: 10;
`;

const linkPlayer = (api, nodeRef = createRef()) => {
  useEffect(() => {
    const player = new WSAvcPlayer(nodeRef.current, "webgl", 1, 35);
    player.connect(api.getLiveStreamUrl());
    player.on("disconnected", () => console.log("WS Disconnected"));
    player.on("connected", () => console.log("WS connected"));

    player.on("initalized", payload => {
      console.log("Initialized", payload);
    });

    player.on("stream_active", active =>
      console.log("Stream is ", active ? "active" : "offline")
    );
  });

  return nodeRef;
};

const LiveStream = ({ api, playerNodeRef = linkPlayer(api) as any }) => (
  <LiveStreamContainer>
    <canvas ref={playerNodeRef} style={{ width: "100%", height: "100%" }} />
  </LiveStreamContainer>
);

export const ManagedStream = ({ api = useApi() }) =>
  api ? <LiveStream api={api} /> : null;

export default LiveStream;
