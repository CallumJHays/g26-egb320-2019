import styled from "styled-components";
import { useEffect, createRef, useState } from "react";
import WSAvcPlayer from "ws-avc-player";

const LiveStreamContainer = styled.div`
  position: absolute;
  top: 0;
  right: 0;
  width: 25vw;
  v-index: 10;
`;

const linkPlayer = (api, nodeRef = createRef()) => {
  useEffect(() => {
    console.log("connecting with noderef", nodeRef.current);
    const player = new WSAvcPlayer(nodeRef.current, "webgl", 1, 35);
    player.connect(api.getLivestreamUrl());
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

export default ({ api, playerNodeRef = linkPlayer(api) as any }) => (
  <LiveStreamContainer>
    <canvas ref={playerNodeRef} style={{ width: "100%", height: "100%" }} />
  </LiveStreamContainer>
);
