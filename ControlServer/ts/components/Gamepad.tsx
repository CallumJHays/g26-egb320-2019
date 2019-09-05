import ReactJoystick from "react-joystick";
import styled from "styled-components";

const Container = styled.div`
  display: flex;
  align-items: stretch;
  height: 100vh;
  > * {
    flex-grow: 1;
  }
`;

const ButtonsContainer = styled.div`
  display: flex;
  flex-direction: column;

  button {
    flex-grow: 1;
    font-family: Impact, Charcoal, sans-serif;
    color: white;
    font-size: 2.5em;
    border: 5px solid white;
  }
`;

const KickButton = styled.button`
  background-image: linear-gradient(to bottom left, #f44336, #b71c1c);
  :hover {
    background-image: linear-gradient(to bottom left, #b71c1c, #f44336);
  }
  :active {
    border-color: #b71c1c;
  }
`;

const DribbleButton = styled.button`
  background-image: linear-gradient(to bottom left, #1e88e5, #0d47a1);
  :hover {
    background-image: linear-gradient(to bottom left, #0d47a1, #1e88e5);
  }
  :active {
    border-color: #0d47a1;
  }
`;

export default () => (
  <Container>
    <ReactJoystick
      joyOptions={{
        mode: "semi",
        catchDistance: 100,
        color: "white"
      }}
      containerStyle={{
        position: "relative",
        width: "50%",
        margin: 0,
        background: "radial-gradient(#212121, #212121, #424242)"
      }}
      managerListener={nipple => {
        nipple.on("move", (_e, _stick) => console.log("I moved!"));
        nipple.on("end", () => console.log("I finished moving!"));
      }}
    />
    <ButtonsContainer>
      <KickButton>
        <b>KICK</b>
      </KickButton>
      <DribbleButton>
        <b>DRIBBLE</b>
      </DribbleButton>
    </ButtonsContainer>
  </Container>
);
