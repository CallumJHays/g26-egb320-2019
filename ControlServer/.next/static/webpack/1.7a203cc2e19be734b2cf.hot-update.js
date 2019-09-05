webpackHotUpdate(1,{

/***/ "./ts/components/Gamepad.tsx":
/*!***********************************!*\
  !*** ./ts/components/Gamepad.tsx ***!
  \***********************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _babel_runtime_corejs2_helpers_esm_taggedTemplateLiteral__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @babel/runtime-corejs2/helpers/esm/taggedTemplateLiteral */ "./node_modules/@babel/runtime-corejs2/helpers/esm/taggedTemplateLiteral.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "./node_modules/react/index.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_joystick__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-joystick */ "./node_modules/react-joystick/lib/index.js");
/* harmony import */ var react_joystick__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_joystick__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var styled_components__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! styled-components */ "./node_modules/styled-components/dist/styled-components.browser.esm.js");

var _jsxFileName = "/home/cal/uni/egb320/g26-egb320-2019/ControlServer/ts/components/Gamepad.tsx";

var __jsx = react__WEBPACK_IMPORTED_MODULE_1___default.a.createElement;

function _templateObject4() {
  var data = Object(_babel_runtime_corejs2_helpers_esm_taggedTemplateLiteral__WEBPACK_IMPORTED_MODULE_0__["default"])(["\n  background-image: linear-gradient(to bottom left, #1e88e5, #0d47a1);\n  :hover {\n    background-image: linear-gradient(to bottom left, #0d47a1, #1e88e5);\n  }\n"]);

  _templateObject4 = function _templateObject4() {
    return data;
  };

  return data;
}

function _templateObject3() {
  var data = Object(_babel_runtime_corejs2_helpers_esm_taggedTemplateLiteral__WEBPACK_IMPORTED_MODULE_0__["default"])(["\n  background-image: linear-gradient(to bottom left, #f44336, #b71c1c);\n  :hover {\n    background-image: linear-gradient(to bottom left, #b71c1c, #f44336);\n  }\n"]);

  _templateObject3 = function _templateObject3() {
    return data;
  };

  return data;
}

function _templateObject2() {
  var data = Object(_babel_runtime_corejs2_helpers_esm_taggedTemplateLiteral__WEBPACK_IMPORTED_MODULE_0__["default"])(["\n  display: flex;\n  flex-direction: column;\n\n  button {\n    flex-grow: 1;\n    font-family: Impact, Charcoal, sans-serif;\n    color: white;\n    font-size: 2.5em;\n    border: 5px solid white;\n    border-radius: 10px;\n    transition: all 0.3s;\n    :active {\n      font-size: 1em;\n    }\n  }\n"]);

  _templateObject2 = function _templateObject2() {
    return data;
  };

  return data;
}

function _templateObject() {
  var data = Object(_babel_runtime_corejs2_helpers_esm_taggedTemplateLiteral__WEBPACK_IMPORTED_MODULE_0__["default"])(["\n  display: flex;\n  align-items: stretch;\n  height: 100vh;\n  > * {\n    flex-grow: 1;\n  }\n"]);

  _templateObject = function _templateObject() {
    return data;
  };

  return data;
}



var Container = styled_components__WEBPACK_IMPORTED_MODULE_3__["default"].div(_templateObject());
var ButtonsContainer = styled_components__WEBPACK_IMPORTED_MODULE_3__["default"].div(_templateObject2());
var KickButton = styled_components__WEBPACK_IMPORTED_MODULE_3__["default"].button(_templateObject3());
var DribbleButton = styled_components__WEBPACK_IMPORTED_MODULE_3__["default"].button(_templateObject4());
/* harmony default export */ __webpack_exports__["default"] = (function () {
  return __jsx(Container, {
    __source: {
      fileName: _jsxFileName,
      lineNumber: 46
    },
    __self: this
  }, __jsx(react_joystick__WEBPACK_IMPORTED_MODULE_2___default.a, {
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
    managerListener: function managerListener(nipple) {
      nipple.on("move", function (_e, _stick) {
        return console.log("I moved!");
      });
      nipple.on("end", function () {
        return console.log("I finished moving!");
      });
    },
    __source: {
      fileName: _jsxFileName,
      lineNumber: 47
    },
    __self: this
  }), __jsx(ButtonsContainer, {
    __source: {
      fileName: _jsxFileName,
      lineNumber: 64
    },
    __self: this
  }, __jsx(KickButton, {
    __source: {
      fileName: _jsxFileName,
      lineNumber: 65
    },
    __self: this
  }, __jsx("b", {
    __source: {
      fileName: _jsxFileName,
      lineNumber: 66
    },
    __self: this
  }, "KICK")), __jsx(DribbleButton, {
    __source: {
      fileName: _jsxFileName,
      lineNumber: 68
    },
    __self: this
  }, __jsx("b", {
    __source: {
      fileName: _jsxFileName,
      lineNumber: 69
    },
    __self: this
  }, "DRIBBLE"))));
});

/***/ })

})
//# sourceMappingURL=1.7a203cc2e19be734b2cf.hot-update.js.map