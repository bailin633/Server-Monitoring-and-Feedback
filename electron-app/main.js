const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow;

function createWindow() {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'), // Path to preload script
      contextIsolation: true, // Recommended for security
      nodeIntegration: false, // Recommended for security
    },
  });

  // and load the index.html of the app.
  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  // Remove the default menu bar
  mainWindow.setMenu(null);

  // Open the DevTools (optional)
  // mainWindow.webContents.openDevTools();

  // Emitted when the window is closed.
  mainWindow.on('closed', function () {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null;
  });
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(async () => { // Make the callback async
  // Run initial Python setup before creating the window
  console.log('Attempting to run initial Python setup...');
  try {
    const setupResult = await runPythonScript('run_initial_setup');
    if (setupResult && setupResult.success) {
      console.log('Initial Python setup successful:', setupResult.message);
    } else {
      console.error('Initial Python setup failed:', setupResult ? setupResult.error : 'Unknown error from python_adapter.py');
      // Optionally, inform the user via a dialog if setup is critical.
      // For now, we'll log and continue.
      // const { dialog } = require('electron');
      // dialog.showErrorBox('Python Setup Error', `Initial Python setup failed: ${setupResult?.error || 'Unknown error'}`);
    }
  } catch (err) {
    console.error('Critical error during initial Python setup execution in main.js:', err);
    // const { dialog } = require('electron');
    // dialog.showErrorBox('Python Setup Critical Error', `Critical error during initial Python setup: ${err.message}`);
  }

  createWindow();

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.

// --- IPC Handlers for Python interaction ---

// Helper function to run Python scripts
async function runPythonScript(action, scriptArgs = null) {
  try {
    const pythonArgs = [action];
    if (scriptArgs) {
      pythonArgs.push(JSON.stringify(scriptArgs));
    }

    const options = {
      mode: 'json',
      pythonPath: 'python', // Adjust if your python executable is not in PATH or named differently
      pythonOptions: ['-u'], // Unbuffered stdout
      scriptPath: path.join(__dirname, '..'), // Points to the project root where python_adapter.py is
      args: pythonArgs,
    };

    const results = await PythonShell.run('python_adapter.py', options);
    if (results && results.length > 0) {
      // python_adapter.py should print a single JSON object which python-shell collects in results[0]
      return results[0];
    }
    // This case should ideally be handled by python_adapter.py returning an error JSON
    return { error: `No result from Python script for action: ${action}` };
  } catch (err) {
    console.error(`Error running python script (action: ${action}):`, err);
    // err might be an array of strings if python-shell collected stderr
    let errorMessage = 'Failed to run python script';
    if (err.message) {
        errorMessage = err.message;
    } else if (Array.isArray(err) && err.length > 0) {
        errorMessage = err.join('\n');
    } else if (typeof err === 'string') {
        errorMessage = err;
    }
    return { error: errorMessage, action: action };
  }
}

// --- System Info IPC Handlers ---
ipcMain.handle('get-cpu-usage', async () => runPythonScript('get_cpu_usage'));
ipcMain.handle('get-memory-usage', async () => runPythonScript('get_memory_usage'));
ipcMain.handle('get-os-info', async () => runPythonScript('get_os_info'));
ipcMain.handle('get-windows-version-info', async () => runPythonScript('get_windows_version_info'));
ipcMain.handle('get-cpu-core-count', async () => runPythonScript('get_cpu_core_count'));
ipcMain.handle('get-virtual-memory-usage', async () => runPythonScript('get_virtual_memory_usage'));
ipcMain.handle('get-running-process-count', async () => runPythonScript('get_running_process_count'));
ipcMain.handle('get-mem-info', async () => runPythonScript('get_mem_info'));

// --- Config IPC Handlers ---
ipcMain.handle('read-config', async () => runPythonScript('read_config'));
ipcMain.handle('save-config', async (event, configData) => runPythonScript('save_config', configData));

// --- Email IPC Handler ---
ipcMain.handle('send-alert-email', async (event, emailData) => runPythonScript('send_alert_email', emailData));


console.log("Main process (main.js) started and IPC handlers registered.");