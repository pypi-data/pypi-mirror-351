import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
import { CodeCell } from '@jupyterlab/cells';
import { NotebookActions } from '@jupyterlab/notebook';

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
%load_ext pergamon_server_extension
`;

/**
 * Initialization data for the pergamon_server_extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'pergamon_server_extension:plugin',
  description: 'Calliope server extension',
  requires: [INotebookTracker],
  autoStart: true,
  activate: (app: JupyterFrontEnd, tracker: INotebookTracker) => {
    tracker.widgetAdded.connect((sender, notebookPanel) => {
      notebookPanel.sessionContext.ready.then(() => {
        const session = notebookPanel.sessionContext.session;

        if (session?.kernel) {
          session.kernel.registerCommTarget('toggle_fixing', comm => {
            comm.onMsg = msg => {
              const targetCell = notebookPanel.content.activeCell;
              if (targetCell) {
                const codeCell = targetCell as CodeCell;
                if (codeCell.model.sharedModel) {
                  codeCell.node.classList.toggle('calliope-thinking');
                }
              }
            };
          });

          session?.kernel?.registerCommTarget('replace_cell', comm => {
            comm.onMsg = msg => {
              const newCode = msg.content.data.replace_with as string;
              const activeCell = notebookPanel.content.activeCell;

              if (activeCell && activeCell.model.type === 'code') {
                const codeCell = activeCell as CodeCell;
                if (codeCell.editor) {
                  codeCell.model.sharedModel.setSource(newCode);
                  NotebookActions.run(
                    notebookPanel.content,
                    notebookPanel.sessionContext
                  );
                }
              }
            };
          });

          session.kernel.registerCommTarget('insert_new_cell', comm => {
            comm.onMsg = msg => {
              const cellContent = msg.content.data.cell_content as string;
              const shouldExecute = msg.content.data.execute_cell as boolean;

              NotebookActions.insertBelow(notebookPanel.content);

              NotebookActions.changeCellType(notebookPanel.content, 'code');

              const activeCell = notebookPanel.content.activeCell as CodeCell;
              activeCell.model.sharedModel.setSource(cellContent);

              if (shouldExecute) {
                NotebookActions.run(
                  notebookPanel.content,
                  notebookPanel.sessionContext
                );
              }
            };
          });

          session.kernel
            .requestExecute({
              code: setupCode
            })
            .done.then(() => {});
        }

        // Use NotebookActions signals to track executing cells instead of status changes
        NotebookActions.executionScheduled.connect((_, args) => {
          const { cell } = args;

          // Add executing class to the specific cell that was scheduled
          if (cell.model.type === 'code') {
            const codeCell = cell as CodeCell;
            codeCell.node.classList.add('executing');

            // Check if this specific cell has calliope magic
            const cellContent = codeCell.model.sharedModel.source || '';
            const hasMagic =
              cellContent.trim().startsWith('%%calliope') ||
              cellContent.trim().startsWith('%calliope');

            if (hasMagic) {
              codeCell.node.classList.add('calliope-thinking');
            }
          }
        });

        NotebookActions.executed.connect((_, args) => {
          const { cell } = args;

          // Remove executing and thinking classes from the specific cell that finished
          if (cell.model.type === 'code') {
            const codeCell = cell as CodeCell;
            codeCell.node.classList.remove('executing');
            codeCell.node.classList.remove('calliope-thinking');
          }
        });
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

export default plugin;
