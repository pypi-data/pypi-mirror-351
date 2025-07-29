"use strict";
(self["webpackChunkjupyter_leaflet"] = self["webpackChunkjupyter_leaflet"] || []).push([[330,869],{

/***/ 1869:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyter_widgets_base__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(4488);
/* harmony import */ var _jupyter_widgets_base__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyter_widgets_base__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _package_json__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(8330);
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.


const { /* version */ "rE": version } = _package_json__WEBPACK_IMPORTED_MODULE_1__;
const extension = {
    id: 'jupyter-leaflet',
    requires: [_jupyter_widgets_base__WEBPACK_IMPORTED_MODULE_0__.IJupyterWidgetRegistry],
    activate: (app, widgets) => {
        widgets.registerWidget({
            name: 'jupyter-leaflet',
            version: version,
            exports: async () => Promise.all(/* import() */[__webpack_require__.e(82), __webpack_require__.e(800), __webpack_require__.e(672)]).then(__webpack_require__.bind(__webpack_require__, 3553)),
        });
    },
    autoStart: true,
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (extension);
//# sourceMappingURL=jupyterlab-plugin.js.map

/***/ }),

/***/ 8330:
/***/ ((module) => {

module.exports = {"rE":"0.20.2"};

/***/ })

}]);
//# sourceMappingURL=869.6671ca0d624ff8c809de.js.map?v=6671ca0d624ff8c809de