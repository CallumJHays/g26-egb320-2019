import styled, { css } from "styled-components";
import { useEffect, createRef, useState } from "react";
import { useApi } from "../api";
import WSAvcPlayer from "ws-avc-player";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faExpand } from "@fortawesome/free-solid-svg-icons";
import { Stage, Layer, Rect, Text } from "react-konva";

const CATEGORICAL_COLORS = [
  "#d32f2f", // red
  "#1976d2", // blue
  "##388e3c", // green
  "#fbc02d", // yellow
  "#455a64", // bluegray
  "#c2185b", // pink
  "#7b1fa2", // purple
  "#e64a19", // orange
  "#00796b" // teal
];

const LiveStreamContainer = styled.div`
  position: absolute;
  top: 0;
  z-index: 10;
  background-color: black;

  transition: all 0.5s;
  ${props =>
    props.fullscreen
      ? css`
          left: 0;
          right: 0;
          bottom: 0;
        `
      : css`
          left: 25vw;
          right: 50vw;
          bottom: 70vh;
        `}
`;

const FullscreenButton = styled.button`
  position: absolute;
  bottom: 0;
  right: 0;
  background-color: transparent;
  border: none;
  color: white;
  cursor: pointer;
  z-index: 20;
`;

const LiveStreamErrorMessage = styled.p`
  position: absolute;
  bottom: 0;
  left: 0;
  color: white;
  margin: 4px;
  font-family: Tahoma, Verdana, Segoe, sans-serif;
  font-size: 10px;
`;

const linkPlayer = (
  api,
  reactRef = createRef(),
  [domRef, setDomRef] = useState(null),
  [streamActive, setStreamActive] = useState(false)
) => {
  useEffect(() => {
    if (domRef === null) {
      const canvas = reactRef.current;
      setDomRef(canvas);
      const player = new WSAvcPlayer(canvas, "webgl", 1, 35);
      player.connect(api.getLiveStreamUrl());
      player.on("frame_shift", () => setStreamActive(true));
    }
  });

  return { reactRef, domRef, streamActive };
};

const linkVisionSystem = (
  api,
  [visionResults, setVisionResults] = useState(null)
) =>
  visionResults === null
    ? api.onVisionSystemResult(setVisionResults) || {}
    : visionResults;

const LiveStream = ({
  api,
  _playerState: { reactRef, domRef, streamActive } = linkPlayer(api) as any,
  _visionState: visionResults = linkVisionSystem(api),
  _fullscreenState: [fullscreen, setFullscreen] = useState(false)
}) => (
  <LiveStreamContainer fullscreen={fullscreen}>
    <FullscreenButton onClick={() => setFullscreen(!fullscreen)}>
      <FontAwesomeIcon icon={faExpand} />
    </FullscreenButton>

    {streamActive ? null : (
      <LiveStreamErrorMessage>LOADING</LiveStreamErrorMessage>
    )}

    {domRef ? (
      <Stage
        width={domRef.width}
        height={domRef.height}
        style={{ top: 0, right: 0, bottom: 0, left: 0, position: "absolute" }}
      >
        <Layer>
          {Object.keys(visionResults).map(
            (objName, colorIdx, _, color = CATEGORICAL_COLORS[colorIdx]) =>
              visionResults[objName].map(
                ([[[x1, y1], [x2, y2]], bearing, distance]) => (
                  <>
                    <Rect
                      x={x1}
                      y={domRef.height - y2}
                      width={x2 - x1}
                      height={y2 - y1}
                      stroke={color}
                      strokeWidth={1}
                    />
                    {fullscreen ? (
                      <Text
                        x={x1}
                        y={domRef.height - y2}
                        fill={color}
                        text={`${objName}: ${distance}@${bearing}`}
                      />
                    ) : null}
                  </>
                )
              )
          )}
        </Layer>
      </Stage>
    ) : null}

    <canvas ref={reactRef} style={{ width: "100%", height: "100%" }} />
  </LiveStreamContainer>
);

export const ManagedStream = ({ api = useApi() }) =>
  api ? <LiveStream api={api} /> : null;

export default LiveStream;
