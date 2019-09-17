import ReactJoystick from "react-joystick";
import styled from "styled-components";
import { useState } from 'react';

import Menu from './Menu';

const App = styled.div`
  font-family: Impact, Charcoal, sans-serif;
`;

const Container = styled.div`
  display: flex;
  align-items: stretch;
  height: 100vh;
  > * {
    flex-grow: 1;
  }
`;

const RightSide = styled.div`
  display: flex;
  flex-direction: column;
`;

const JoystickContainer = styled.div`
  display: flex;
  position: relative;
  align-items: center;
  justify-content: center;

  > span {
    color: #757575;
    position: absolute;
    z-index: 1;

    font-size: 2rem;
    white-space: pre-line;
    text-align: center;

    user-select: none;
    pointer-events: none;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  align-items: stretch;
  height: 50vh;
  button {
    cursor: pointer;
    flex-grow: 1;
    color: white;
    

    border: ${pressed => pressed ? '5px solid #EEEEEE' : '3px solid #424242' };
  }
`;

const KickButton = styled.button`
  flex-grow: 1;
  background-image: linear-gradient(to bottom left, #f44336, #b71c1c);
  font-size: 10vh;

  :hover {
    background-image: linear-gradient(to bottom left, #b71c1c, #f44336);
  }
  :active {
    border-color: #b71c1c;
  }
`;

const ConfigButtons = styled.div`
  display: flex;
  flex-direction: column;
  font-size: 0.75em;
`;

const ToggleDribbleButton = styled.button`
  background-image: linear-gradient(to bottom left, #1e88e5, #0d47a1);
  font-size: 3vh;

  :hover {
    background-image: linear-gradient(to bottom left, #0d47a1, #1e88e5);
  }
  :active {
    border-color: #0d47a1;
  }

  ${({on}) => on ? '' : 'filter: grayscale(100%)'}
`;

const MenuButton = styled.button`
  background-image: linear-gradient(to bottom left, #4CAF50, #1B5E20);
  font-size: 7vh;

  :hover {
    background-image: linear-gradient(to bottom left, #1B5E20, #4CAF50);
  }
  :active {
    border-color: #388E3C;
  }
`;

const Joystick = ({ height: height = 'auto', bgText }) =>
  <JoystickContainer>
    <span>{bgText}</span>
    <ReactJoystick
      joyOptions={{
        mode: "semi",
        catchDistance: 100,
        color: "white"
      }}
      containerStyle={{
        display: "flex",
        position: "relative",
        margin: 0,
        background: "radial-gradient(#212121, #212121, #424242)",
        height,
        width: '50vw',
        justifyContent: 'center',
        alignItems: 'center'
      }}
      managerListener={nipple => {
        nipple.on("move", (_e, _stick) => console.log("I moved!"));
        nipple.on("end", () => console.log("I finished moving!"));
      }}
    />
  </JoystickContainer>

export default ({
  _dribbleState: [isDribbling, setDribbling] = useState(false),
  _menuState: [isMenuOpen, setMenuOpen] = useState(false)
}) => (
  <App>
    {isMenuOpen ? <Menu onClose={() => setMenuOpen(false)} /> : null}
    <Container>
      <div>
        <Joystick height='100vh' bgText={`↑
        ← STRAFE →
        ↓`}/>
      </div>

      <RightSide>
        <Joystick height='50vh' bgText="↶ ROTATE ↷" />

        <ButtonContainer>
          <ConfigButtons>
            <ToggleDribbleButton
              onClick={() => setDribbling(!isDribbling)}
              className={isDribbling ? 'on' : null}
              on={isDribbling}
            >
              TOGGLE<br/>DRIBBLE:<br/>{isDribbling ? "ON" : "OFF"}
            </ToggleDribbleButton>
            <MenuButton onClick={() => setMenuOpen(true)}>
              MENU
            </MenuButton>
          </ConfigButtons>
          <KickButton>
            <b>KICK</b>
          </KickButton>
        </ButtonContainer>
      </RightSide>
    </Container>
  </App>
);
