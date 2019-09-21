import styled from "styled-components";
import { useEffect, createRef } from "react";
import WSAvcPlayer from "ws-avc-player";

const LiveStream = styled.canvas`
  position: absolute;
  top: 0;
  right: 0;
  width: 25vw;
`;

const linkPlayer = (api, nodeRef = createRef()) => {
  useEffect(() => {
    const player = new WSAvcPlayer(nodeRef.current, "webgl", 1, 35);
    player.connect(api.getLivestreamUrl());
  }, []);

  return nodeRef;
};

export default ({ api, playerNodeRef = linkPlayer(api) }) => (
  <LiveStream ref={playerNodeRef} />
);
