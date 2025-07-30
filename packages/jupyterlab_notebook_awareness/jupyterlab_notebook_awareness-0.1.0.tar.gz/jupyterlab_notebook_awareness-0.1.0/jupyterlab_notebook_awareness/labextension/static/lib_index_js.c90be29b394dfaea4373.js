"use strict";
(self["webpackChunkjupyterlab_notebook_awareness"] = self["webpackChunkjupyterlab_notebook_awareness"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);

/**
 * Initialization data for the jupyterlab-notebook-awareness extension.
 */
const plugin = {
    id: 'jupyterlab-notebook-awareness:plugin',
    description: 'A JupyterLab extension that tracks a user\'s current notebook and cell.',
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker],
    autoStart: true,
    activate: (app, notebookTracker) => {
        console.log('JupyterLab extension jupyterlab-notebook-awareness is activated!');
        notebookTracker.activeCellChanged.connect((notebook) => {
            var _a, _b, _c;
            const cellId = (_a = notebook.activeCell) === null || _a === void 0 ? void 0 : _a.model.sharedModel.getId();
            (_c = (_b = notebook.currentWidget) === null || _b === void 0 ? void 0 : _b.model) === null || _c === void 0 ? void 0 : _c.sharedModel.awareness.setLocalStateField('activeCellId', cellId);
        });
        notebookTracker.currentChanged.connect((notebook) => {
            var _a, _b, _c;
            const nbPath = (_a = notebook.currentWidget) === null || _a === void 0 ? void 0 : _a.context.path;
            (_c = (_b = notebook.currentWidget) === null || _b === void 0 ? void 0 : _b.model) === null || _c === void 0 ? void 0 : _c.sharedModel.awareness.setLocalStateField('notebookPath', nbPath);
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.c90be29b394dfaea4373.js.map