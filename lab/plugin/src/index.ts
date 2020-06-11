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
      const reg = /.*\/jupyter\/user\/(.*)\/lab.*/g; // in lieu of identifying a proper variable for a user's name.
      const user = reg.exec(window.location.href)[1];
      await ky.post("https://localhost/panda/add", {json:{user:user, notebook:notebook.model.toJSON(), cell:cell.model.toJSON()}});
    });
  }
};

export default extension;
