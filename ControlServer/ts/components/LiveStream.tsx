import styled from "styled-components";

const LiveStream = styled.img`
  position: absolute;
  top: 0;
  right: 0;
  width: 25vw;
`;

export default () => (
  <LiveStream src="http://localhost:8080/live_stream.mjpg" />
);
