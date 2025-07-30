"use strict";
(self["webpackChunkpergamon_server_extension"] = self["webpackChunkpergamon_server_extension"] || []).push([["lib_index_js"],{

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

const setupCode = `
%load_ext jupyter_ai
%ai register anthropic-chat anthropic-chat:claude-2.0
%ai register native-cohere cohere:command
%ai register bedrock-cohere bedrock:cohere.command-text-v14
%ai register anthropic anthropic:claude-v1
%ai register bedrock bedrock:amazon.titan-text-lite-v1
%ai register gemini gemini:gemini-1.0-pro-001
%ai register gpto openai-chat:gpt-4o
%ai delete ernie-bot
%ai delete ernie-bot-4
%ai delete titan
`;
/**
 * Initialization data for the pergamon_server_extension extension.
 */
const plugin = {
    id: 'pergamon_server_extension:plugin',
    description: 'Calliope server extension',
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker],
    autoStart: true,
    activate: (app, tracker) => {
        console.log('JupyterLab extension pergamon_server_extension is activated!');
        tracker.widgetAdded.connect((sender, notebookPanel) => {
            notebookPanel.sessionContext.ready.then(() => {
                const session = notebookPanel.sessionContext.session;
                if (session === null || session === void 0 ? void 0 : session.kernel) {
                    // loads the extension
                    session.kernel
                        .requestExecute({
                        code: setupCode
                    })
                        .done.then(() => {
                        console.log('Extension loaded successfully');
                    });
                }
            });
        });
        const observer = new MutationObserver((mutationsList, observer) => {
            const splashElement = document.querySelector('.jp-Splash');
            if (splashElement) {
                splashElement.remove();
                observer.disconnect();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.ac92bad0d0b061b96c5a.js.map