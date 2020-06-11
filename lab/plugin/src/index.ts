import {
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  NotebookActions
} from '@jupyterlab/notebook';

import ky from 'ky';

const extension: JupyterFrontEndPlugin<void> = {
  id: 'panda',
  autoStart: true,
  activate: () => {
    NotebookActions.executed.connect(async(sender, args) => {
      const { notebook, cell } = args;
      console.log("Sending run.");
      await ky.get("http://localhost/pandas");
    });
  }
};

export default extension;
