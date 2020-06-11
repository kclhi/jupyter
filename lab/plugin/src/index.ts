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
      const {notebook, cell} = args;
      console.log("Sending run.");
      await ky.post("https://localhost/panda/add", {json:{notebook:notebook.model.toJSON(), cell:cell.model.toJSON()}});
    });
  }
};

export default extension;
