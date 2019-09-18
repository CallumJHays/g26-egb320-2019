
import styled from "styled-components";

const LiveStream = styled.img`
    position: absolute;
    top: 0;
    right: 0;
    max-width: 50%;
`

export default () => <LiveStream src="http://localhost:8000/live_stream.mjpg" />