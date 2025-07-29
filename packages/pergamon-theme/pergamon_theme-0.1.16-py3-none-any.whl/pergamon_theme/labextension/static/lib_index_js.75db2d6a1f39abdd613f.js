"use strict";
(self["webpackChunkpergamon_theme"] = self["webpackChunkpergamon_theme"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Initialization data for the pergamon_theme extension.
 */
const plugin = {
    id: 'pergamon_theme:plugin',
    description: 'Pergamon Theme Extension.',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.IThemeManager],
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__.ISettingRegistry],
    activate: (app, manager) => {
        console.log('JupyterLab extension pergamon_theme is activated!!');
        const style = 'pergamon_theme/index.css';
        manager.register({
            name: 'pergamon_theme',
            isLight: true,
            load: () => manager.loadCSS(style),
            unload: () => Promise.resolve(undefined)
        });
        manager.setTheme('pergamon_theme');
        const id = setInterval(() => {
            const restartAndRun = document.querySelector('.jp-Toolbar-item[data-jp-item-name="restart-and-run"]');
            const debug = document.querySelector('.jp-Toolbar-item[data-jp-item-name="debugger-icon"]');
            const spacer = document.querySelector('.jp-NotebookPanel-toolbar .jp-Toolbar-spacer.jp-Toolbar-item[data-jp-item-name="spacer"]');
            if (debug) {
                if (restartAndRun) {
                    restartAndRun.after(debug);
                }
                if (spacer) {
                    debug.after(spacer);
                }
                clearInterval(id);
            }
        }, 100);
        // Create a custom loading screen element
        const customLoadingScreen = document.createElement('div');
        customLoadingScreen.className = 'custom-loading-screen';
        customLoadingScreen.textContent = 'Loading, please wait...';
        // Add the custom loading screen to the document
        document.body.appendChild(customLoadingScreen);
        const splashElement = document.querySelector('.jp-Splash');
        if (splashElement) {
            splashElement.remove();
        }
        // Remove the custom loading screen once JupyterLab is fully loaded
        app.restored.then(() => {
            document.body.removeChild(customLoadingScreen);
        });
        const observer = new MutationObserver((mutationsList, observer) => {
            var _a, _b;
            if (document.querySelector('.pergamon-calliope-avatar') === null) {
                const jupyternaut = document.querySelector('.MuiAvatar-root');
                if (jupyternaut) {
                    jupyternaut.classList.add('pergamon-calliope-avatar');
                }
                const jupyternautParent = jupyternaut === null || jupyternaut === void 0 ? void 0 : jupyternaut.parentElement;
                if (jupyternautParent) {
                    const img = jupyternautParent.querySelector('img');
                    if (img) {
                        img.remove();
                    }
                    jupyternautParent.classList.add('pergamon-calliope-container');
                }
                const textContent = (_b = (_a = jupyternautParent === null || jupyternautParent === void 0 ? void 0 : jupyternautParent.childNodes) === null || _a === void 0 ? void 0 : _a[1].childNodes) === null || _b === void 0 ? void 0 : _b[0];
                if (textContent) {
                    textContent.textContent = '';
                    const text = document.createElement('p');
                    text.className = 'pergamon-calliope-text';
                    text.textContent =
                        "Hi there! I'm Calliope, your programming assistant. You can ask me a question using the text box below.";
                    const command = document.createElement('p');
                    command.className = 'pergamon-calliope-text';
                    command.textContent = 'You can also use these commands:';
                    textContent.appendChild(text);
                    textContent.appendChild(command);
                }
            }
            const splashElement = document.querySelector('.jp-Splash');
            if (splashElement) {
                splashElement.remove();
                observer.disconnect();
            }
        });
        // @ts-expect-error error
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.NotificationManager.prototype.notify = function () { };
        observer.observe(document.body, { childList: true, subtree: true });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.75db2d6a1f39abdd613f.js.map