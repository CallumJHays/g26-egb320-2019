exports.ids = [0];
exports.modules = {

/***/ "./node_modules/rodal/lib/rodal.css":
/*!******************************************!*\
  !*** ./node_modules/rodal/lib/rodal.css ***!
  \******************************************/
/*! no static exports found */
/***/ (function(module, exports) {



/***/ }),

/***/ "./ts/components/Gamepad.tsx":
/*!***********************************!*\
  !*** ./ts/components/Gamepad.tsx ***!
  \***********************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react_joystick__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-joystick */ "react-joystick");
/* harmony import */ var react_joystick__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react_joystick__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var styled_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! styled-components */ "styled-components");
/* harmony import */ var styled_components__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(styled_components__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _Menu__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./Menu */ "./ts/components/Menu.tsx");
var _jsxFileName = "/home/cal/uni/egb320/g26-egb320-2019/ControlServer/ts/components/Gamepad.tsx";

var __jsx = react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement;




const App = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.div`
  font-family: Impact, Charcoal, sans-serif;
`;
const Container = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.div`
  display: flex;
  align-items: stretch;
  height: 100vh;
  > * {
    flex-grow: 1;
  }
`;
const RightSide = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.div`
  display: flex;
  flex-direction: column;
`;
const JoystickContainer = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.div`
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
const ButtonContainer = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.div`
  display: flex;
  align-items: stretch;
  height: 50vh;
  button {
    cursor: pointer;
    flex-grow: 1;
    color: white;
    

    border: ${pressed => pressed ? '5px solid #EEEEEE' : '3px solid #424242'};
  }
`;
const KickButton = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.button`
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
const ConfigButtons = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.div`
  display: flex;
  flex-direction: column;
  font-size: 0.75em;
`;
const ToggleDribbleButton = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.button`
  background-image: linear-gradient(to bottom left, #1e88e5, #0d47a1);
  font-size: 3vh;

  :hover {
    background-image: linear-gradient(to bottom left, #0d47a1, #1e88e5);
  }
  :active {
    border-color: #0d47a1;
  }

  ${({
  on
}) => on ? '' : 'filter: grayscale(100%)'}
`;
const MenuButton = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.button`
  background-image: linear-gradient(to bottom left, #4CAF50, #1B5E20);
  font-size: 7vh;

  :hover {
    background-image: linear-gradient(to bottom left, #1B5E20, #4CAF50);
  }
  :active {
    border-color: #388E3C;
  }
`;

const Joystick = ({
  height = 'auto',
  bgText
}) => __jsx(JoystickContainer, {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 105
  },
  __self: undefined
}, __jsx("span", {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 106
  },
  __self: undefined
}, bgText), __jsx(react_joystick__WEBPACK_IMPORTED_MODULE_1___default.a, {
  joyOptions: {
    mode: "semi",
    catchDistance: 100,
    color: "white"
  },
  containerStyle: {
    display: "flex",
    position: "relative",
    margin: 0,
    background: "radial-gradient(#212121, #212121, #424242)",
    height,
    width: '50vw',
    justifyContent: 'center',
    alignItems: 'center'
  },
  managerListener: nipple => {
    nipple.on("move", (_e, _stick) => console.log("I moved!"));
    nipple.on("end", () => console.log("I finished moving!"));
  },
  __source: {
    fileName: _jsxFileName,
    lineNumber: 107
  },
  __self: undefined
}));

/* harmony default export */ __webpack_exports__["default"] = (({
  _dribbleState: [isDribbling, setDribbling] = Object(react__WEBPACK_IMPORTED_MODULE_0__["useState"])(false),
  _menuState: [isMenuOpen, setMenuOpen] = Object(react__WEBPACK_IMPORTED_MODULE_0__["useState"])(false)
}) => __jsx(App, {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 134
  },
  __self: undefined
}, isMenuOpen ? __jsx(_Menu__WEBPACK_IMPORTED_MODULE_3__["default"], {
  onClose: () => setMenuOpen(false),
  __source: {
    fileName: _jsxFileName,
    lineNumber: 135
  },
  __self: undefined
}) : null, __jsx(Container, {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 136
  },
  __self: undefined
}, __jsx(Joystick, {
  height: "100vh",
  bgText: `↑
      ← STRAFE →
      ↓`,
  __source: {
    fileName: _jsxFileName,
    lineNumber: 138
  },
  __self: undefined
}), __jsx(RightSide, {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 142
  },
  __self: undefined
}, __jsx(Joystick, {
  height: "50vh",
  bgText: "\u21B6 ROTATE \u21B7",
  __source: {
    fileName: _jsxFileName,
    lineNumber: 143
  },
  __self: undefined
}), __jsx(ButtonContainer, {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 145
  },
  __self: undefined
}, __jsx(ConfigButtons, {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 146
  },
  __self: undefined
}, __jsx(ToggleDribbleButton, {
  onClick: () => setDribbling(!isDribbling),
  className: isDribbling ? 'on' : null,
  on: isDribbling,
  __source: {
    fileName: _jsxFileName,
    lineNumber: 147
  },
  __self: undefined
}, "TOGGLE", __jsx("br", {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 152
  },
  __self: undefined
}), "DRIBBLE:", __jsx("br", {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 152
  },
  __self: undefined
}), isDribbling ? "ON" : "OFF"), __jsx(MenuButton, {
  onClick: () => setMenuOpen(true),
  __source: {
    fileName: _jsxFileName,
    lineNumber: 154
  },
  __self: undefined
}, "MENU")), __jsx(KickButton, {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 158
  },
  __self: undefined
}, __jsx("b", {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 159
  },
  __self: undefined
}, "KICK")))))));

/***/ }),

/***/ "./ts/components/Menu.tsx":
/*!********************************!*\
  !*** ./ts/components/Menu.tsx ***!
  \********************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var rodal__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! rodal */ "rodal");
/* harmony import */ var rodal__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(rodal__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var rodal_lib_rodal_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! rodal/lib/rodal.css */ "./node_modules/rodal/lib/rodal.css");
/* harmony import */ var rodal_lib_rodal_css__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(rodal_lib_rodal_css__WEBPACK_IMPORTED_MODULE_2__);
var _jsxFileName = "/home/cal/uni/egb320/g26-egb320-2019/ControlServer/ts/components/Menu.tsx";

var __jsx = react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement;




const Menu = ({
  onClose,
  aiParams: {
    _aimYellowGoal: [aimYellowGoal, setAimYellowGoal] = Object(react__WEBPACK_IMPORTED_MODULE_0__["useState"])(true)
  } = {}
}) => __jsx(rodal__WEBPACK_IMPORTED_MODULE_1___default.a, {
  visible: true,
  onClose: onClose,
  width: 550,
  height: 300,
  __source: {
    fileName: _jsxFileName,
    lineNumber: 12
  },
  __self: undefined
}, __jsx("h4", {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 13
  },
  __self: undefined
}, "Menu"), __jsx("button", {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 14
  },
  __self: undefined
}, "Play Imperial March"), __jsx("hr", {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 16
  },
  __self: undefined
}), __jsx("h4", {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 17
  },
  __self: undefined
}, "AI"), "Current goal: ", aimYellowGoal ? 'Yellow' : 'Blue', " ", __jsx("button", {
  onClick: () => setAimYellowGoal(!aimYellowGoal),
  __source: {
    fileName: _jsxFileName,
    lineNumber: 21
  },
  __self: undefined
}, "Switch"));

/* harmony default export */ __webpack_exports__["default"] = (Menu);

/***/ })

};;
//# sourceMappingURL=0.js.map