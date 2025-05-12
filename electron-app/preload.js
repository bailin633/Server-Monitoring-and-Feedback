const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // --- System Info ---
  getCpuUsage: () => ipcRenderer.invoke('get-cpu-usage'),
  getMemoryUsage: () => ipcRenderer.invoke('get-memory-usage'),
  getOsInfo: () => ipcRenderer.invoke('get-os-info'),
  getWindowsVersionInfo: () => ipcRenderer.invoke('get-windows-version-info'),
  getCpuCoreCount: () => ipcRenderer.invoke('get-cpu-core-count'),
  getVirtualMemoryUsage: () => ipcRenderer.invoke('get-virtual-memory-usage'),
  getRunningProcessCount: () => ipcRenderer.invoke('get-running-process-count'),
  getMemInfo: () => ipcRenderer.invoke('get-mem-info'),

  // --- Config ---
  readConfig: () => ipcRenderer.invoke('read-config'),
  saveConfig: (configData) => ipcRenderer.invoke('save-config', configData), // configData will be passed as JSON string in sys.argv[2]

  // --- Email ---
  sendAlertEmail: (emailData) => ipcRenderer.invoke('send-alert-email', emailData), // emailData for subject, body, to_email etc.

  // --- Potentially other functions ---
  // Example: handle a response from main process if needed (though invoke handles responses)
  // on: (channel, callback) => {
  //   ipcRenderer.on(channel, (event, ...args) => callback(...args));
  // },
  // Example: one-way message to main
  // send: (channel, data) => {
  //   ipcRenderer.send(channel, data);
  // }
});

console.log('Preload script (preload.js) loaded.');