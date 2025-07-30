import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IThemeManager, NotificationManager } from '@jupyterlab/apputils';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

/**
 * Function to replace "Jupyternaut" with "Calliope" in rendered markdown paragraphs
 */
function replaceJupyternautWithCalliope() {
  const paragraphs = document.querySelectorAll(
    '.lm-Widget.jp-RenderedHTMLCommon.jp-RenderedMarkdown>p'
  );

  paragraphs.forEach(p => {
    if (p.textContent && p.textContent.includes('Jupyternaut')) {
      p.textContent = p.textContent.replace(/Jupyternaut/g, 'Calliope');
    }
  });
}

/**
 * Initialization data for the pergamon_theme extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'pergamon_theme:plugin',
  description: 'Pergamon Theme Extension.',
  autoStart: true,
  requires: [IThemeManager],
  optional: [ISettingRegistry],
  activate: (app: JupyterFrontEnd, manager: IThemeManager) => {
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
      const restartAndRun = document.querySelector(
        '.jp-Toolbar-item[data-jp-item-name="restart-and-run"]'
      );

      const debug = document.querySelector(
        '.jp-Toolbar-item[data-jp-item-name="debugger-icon"]'
      );

      const spacer = document.querySelector(
        '.jp-NotebookPanel-toolbar .jp-Toolbar-spacer.jp-Toolbar-item[data-jp-item-name="spacer"]'
      );

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
      // Replace Jupyternaut with Calliope in rendered markdown
      replaceJupyternautWithCalliope();

      if (document.querySelector('.pergamon-calliope-avatar') === null) {
        const jupyternaut = document.querySelector('.MuiAvatar-root');

        if (jupyternaut) {
          jupyternaut.classList.add('pergamon-calliope-avatar');
        }

        const jupyternautParent = jupyternaut?.parentElement;
        if (jupyternautParent) {
          const img = jupyternautParent.querySelector('img');
          if (img) {
            img.remove();
          }
          jupyternautParent.classList.add('pergamon-calliope-container');
        }

        const textContent = jupyternautParent?.childNodes?.[1].childNodes?.[0];

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

    // Initial call to replace any existing Jupyternaut references
    replaceJupyternautWithCalliope();

    // @ts-expect-error error
    NotificationManager.prototype.notify = function () {};

    observer.observe(document.body, { childList: true, subtree: true });
  }
};

export default plugin;
