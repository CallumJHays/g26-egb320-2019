exports.ids = [0];
exports.modules = {

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
var _jsxFileName = "/home/cal/uni/egb320/g26-egb320-2019/ControlServer/ts/components/Gamepad.tsx";

var __jsx = react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement;


const Container = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.div`
  display: flex;
  align-items: stretch;
  height: 100vh;
  > * {
    flex-grow: 1;
  }
`;
const ButtonsContainer = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.div`
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
const KickButton = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.button`
  background-image: linear-gradient(to bottom left, #f44336, #b71c1c);
  :hover {
    background-image: linear-gradient(to bottom left, #b71c1c, #f44336);
  }
  :active {
    border-color: #b71c1c;
  }
`;
const DribbleButton = styled_components__WEBPACK_IMPORTED_MODULE_2___default.a.button`
  background-image: linear-gradient(to bottom left, #1e88e5, #0d47a1);
  :hover {
    background-image: linear-gradient(to bottom left, #0d47a1, #1e88e5);
  }
  :active {
    border-color: #0d47a1;
  }
`;
/* harmony default export */ __webpack_exports__["default"] = (() => __jsx(Container, {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 47
  },
  __self: undefined
}, __jsx(react_joystick__WEBPACK_IMPORTED_MODULE_1___default.a, {
  joyOptions: {
    mode: "semi",
    catchDistance: 100,
    color: "white"
  },
  containerStyle: {
    position: "relative",
    width: "50%",
    margin: 0,
    background: "radial-gradient(#212121, #212121, #424242)"
  },
  managerListener: nipple => {
    nipple.on("move", (_e, _stick) => console.log("I moved!"));
    nipple.on("end", () => console.log("I finished moving!"));
  },
  __source: {
    fileName: _jsxFileName,
    lineNumber: 48
  },
  __self: undefined
}), __jsx(ButtonsContainer, {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 65
  },
  __self: undefined
}, __jsx(KickButton, {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 66
  },
  __self: undefined
}, __jsx("b", {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 67
  },
  __self: undefined
}, "KICK")), __jsx(DribbleButton, {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 69
  },
  __self: undefined
}, __jsx("b", {
  __source: {
    fileName: _jsxFileName,
    lineNumber: 70
  },
  __self: undefined
}, "DRIBBLE")))));

/***/ })

};;
//# sourceMappingURL=0.js.map