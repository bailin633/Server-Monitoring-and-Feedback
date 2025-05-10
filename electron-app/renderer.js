document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    // Realtime Data
    const cpuUsageEl = document.getElementById('cpu-usage');
    const memoryUsageEl = document.getElementById('memory-usage');
    const osInfoEl = document.getElementById('os-info');
    const windowsVersionEl = document.getElementById('windows-version');
    const cpuCoresEl = document.getElementById('cpu-cores');
    const totalMemoryEl = document.getElementById('total-memory');
    const virtualMemoryEl = document.getElementById('virtual-memory');
    const runningProcessesEl = document.getElementById('running-processes');

    // Monitor Settings
    const cpuThresholdInput = document.getElementById('cpu-threshold');
    const memoryThresholdInput = document.getElementById('memory-threshold');
    const checkIntervalInput = document.getElementById('check-interval');

    // Email Config
    const senderEmailInput = document.getElementById('sender-email');
    const senderPasswordInput = document.getElementById('sender-password');
    const receiverEmailInput = document.getElementById('receiver-email');
    const saveConfigBtn = document.getElementById('save-config-btn');

    // Controls
    const startMonitorBtn = document.getElementById('start-monitor-btn');
    const stopMonitorBtn = document.getElementById('stop-monitor-btn');

    // Log and Status
    const logOutputEl = document.getElementById('log-output');
    const statusMessageEl = document.getElementById('status-message');

    // Theme Toggle
    const themeToggleBtn = document.getElementById('theme-toggle-btn');

    let мониторингИнтервалаId = null; // Variable to hold the interval ID for monitoring
    let isMonitoringActive = false;

    // --- Utility Functions ---
    function addLog(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('p');
        logEntry.textContent = `[${timestamp}] ${message}`;
        if (type === 'error') {
            logEntry.style.color = '#F44336'; // Red for errors
        } else if (type === 'warning') {
            logEntry.style.color = '#FFC107'; // Amber for warnings
        }
        logOutputEl.appendChild(logEntry);
        logOutputEl.scrollTop = logOutputEl.scrollHeight; // Auto-scroll to bottom
        updateStatus(message);
    }

    function updateStatus(message) {
        statusMessageEl.textContent = message;
    }

    // --- Initial Data Loading ---
    async function loadInitialData() {
        try {
            addLog('正在加载初始系统信息...');
            const osInfo = await window.electronAPI.getOsInfo();
            if (osInfo && !osInfo.error) {
                osInfoEl.textContent = `${osInfo[0] || 'N/A'} ${osInfo[1] || ''}`;
            } else {
                osInfoEl.textContent = '加载失败';
                addLog(`加载操作系统信息失败: ${osInfo?.error || '未知错误'}`, 'error');
            }

            const winVer = await window.electronAPI.getWindowsVersionInfo();
            windowsVersionEl.textContent = winVer && !winVer.error ? winVer : '加载失败';
            if (winVer?.error) addLog(`加载 Windows 版本失败: ${winVer.error}`, 'error');


            const cpuCores = await window.electronAPI.getCpuCoreCount();
            if (cpuCores && !cpuCores.error) {
                cpuCoresEl.textContent = `${cpuCores[0] || 'N/A'} (逻辑核心: ${cpuCores[1] || 'N/A'})`;
            } else {
                cpuCoresEl.textContent = '加载失败';
                if(cpuCores?.error) addLog(`加载 CPU 核心数失败: ${cpuCores.error}`, 'error');
            }

            const memInfo = await window.electronAPI.getMemInfo();
            totalMemoryEl.textContent = memInfo && !memInfo.error ? memInfo : '加载失败';
            if (memInfo?.error) addLog(`加载总内存失败: ${memInfo.error}`, 'error');
            
            addLog('初始系统信息加载完成。');

            addLog('正在加载邮件配置...');
            const config = await window.electronAPI.readConfig();
            if (config && !config.error) {
                senderEmailInput.value = config.sender_email || '';
                // Do not populate password for security: senderPasswordInput.value = config.sender_password || '';
                receiverEmailInput.value = config.receiver_email || '';
                if (config.check_interval_minutes) {
                    checkIntervalInput.value = config.check_interval_minutes;
                }
                addLog('邮件配置加载完成。');
            } else {
                addLog(`加载邮件配置失败: ${config?.error || '未能读取配置'}`, 'warning');
            }

        } catch (error) {
            addLog(`加载初始数据时发生严重错误: ${error.message}`, 'error');
            console.error("Error loading initial data:", error);
        }
    }

    // --- Event Listeners ---
    saveConfigBtn.addEventListener('click', async () => {
        const configData = {
            sender_email: senderEmailInput.value,
            sender_password: senderPasswordInput.value, // Password will be sent
            receiver_email: receiverEmailInput.value,
            check_interval_minutes: checkIntervalInput.value,
            clear_console_seconds: "3600" // This value is from old config, keep it for python_adapter compatibility
        };
        addLog('正在保存邮件配置...');
        try {
            const result = await window.electronAPI.saveConfig(configData);
            if (result && result.success) {
                addLog('邮件配置已成功保存。');
            } else {
                addLog(`保存邮件配置失败: ${result?.error || '未知错误'}`, 'error');
            }
        } catch (error) {
            addLog(`保存配置时发生错误: ${error.message}`, 'error');
        }
    });

    startMonitorBtn.addEventListener('click', () => {
        if (isMonitoringActive) {
            addLog('监控已经在运行中。', 'warning');
            return;
        }
        isMonitoringActive = true;
        startMonitorBtn.disabled = true;
        stopMonitorBtn.disabled = false;
        addLog('监控已启动。');
        performMonitoring(); // Perform first check immediately
        const intervalSeconds = parseFloat(checkIntervalInput.value) * 60;
        if (isNaN(intervalSeconds) || intervalSeconds <= 0) {
            addLog('无效的检测间隔，请设置为正数。', 'error');
            stopMonitoring(); // Stop if interval is invalid
            return;
        }
        мониторингИнтервалаId = setInterval(performMonitoring, intervalSeconds * 1000);
    });

    function stopMonitoring() {
        if (!isMonitoringActive) return;
        isMonitoringActive = false;
        if (мониторингИнтервалаId) {
            clearInterval(мониторингИнтервалаId);
            мониторингИнтервалаId = null;
        }
        startMonitorBtn.disabled = false;
        stopMonitorBtn.disabled = true;
        addLog('监控已停止。');
        cpuUsageEl.textContent = 'N/A (已停止)';
        memoryUsageEl.textContent = 'N/A (已停止)';
    }
    stopMonitorBtn.addEventListener('click', stopMonitoring);


    // --- Monitoring Logic ---
    async function performMonitoring() {
        if (!isMonitoringActive) return;
        // addLog('正在获取系统资源使用率...'); // Removed to reduce log clutter
        updateStatus('正在更新资源数据...'); // Update status bar instead
        try {
            const cpu = await window.electronAPI.getCpuUsage();
            const mem = await window.electronAPI.getMemoryUsage();
            const vMem = await window.electronAPI.getVirtualMemoryUsage();
            const procCount = await window.electronAPI.getRunningProcessCount();

            cpuUsageEl.textContent = cpu && typeof cpu === 'number' ? `${cpu.toFixed(1)}%` : (cpu?.error || '错误');
            memoryUsageEl.textContent = mem && typeof mem === 'number' ? `${mem.toFixed(1)}%` : (mem?.error || '错误');
            virtualMemoryEl.textContent = vMem && !vMem.error ? vMem : (vMem?.error || '错误');
            runningProcessesEl.textContent = procCount && !procCount.error ? procCount : (procCount?.error || '错误');
            
            if (cpu?.error) addLog(`获取CPU使用率失败: ${cpu.error}`, 'error');
            if (mem?.error) addLog(`获取内存使用率失败: ${mem.error}`, 'error');


            // Check thresholds and send email
            const cpuThreshold = parseFloat(cpuThresholdInput.value);
            const memoryThreshold = parseFloat(memoryThresholdInput.value);

            let alertNeeded = false;
            let emailSubject = "系统资源警报";
            let emailBodyParts = [];

            if (typeof cpu === 'number' && cpu > cpuThreshold) {
                alertNeeded = true;
                emailBodyParts.push(`CPU 使用率 (${cpu.toFixed(1)}%) 超过阈值 (${cpuThreshold}%).`);
                addLog(`警告: CPU 使用率 ${cpu.toFixed(1)}% 超过阈值 ${cpuThreshold}%`, 'warning');
            }
            if (typeof mem === 'number' && mem > memoryThreshold) {
                alertNeeded = true;
                emailBodyParts.push(`内存使用率 (${mem.toFixed(1)}%) 超过阈值 (${memoryThreshold}%).`);
                addLog(`警告: 内存使用率 ${mem.toFixed(1)}% 超过阈值 ${memoryThreshold}%`, 'warning');
            }

            if (alertNeeded) {
                const senderEmail = senderEmailInput.value;
                const senderPassword = senderPasswordInput.value; // Important: Password is read from input here
                const receiverEmail = receiverEmailInput.value;

                if (!senderEmail || !senderPassword || !receiverEmail) {
                    addLog('邮件配置不完整，无法发送警报邮件。', 'error');
                    return;
                }
                
                // Construct a more detailed email body if needed, similar to the Tkinter version
                const osInfoText = osInfoEl.textContent;
                const winVerText = windowsVersionEl.textContent;
                const cpuCoresText = cpuCoresEl.textContent;
                const totalMemText = totalMemoryEl.textContent;

                let fullEmailBody = `<html><body><h1>系统资源警报</h1>`;
                emailBodyParts.forEach(part => {
                    fullEmailBody += `<p>${part}</p>`;
                });
                fullEmailBody += `
                    <hr>
                    <h3>系统快照:</h3>
                    <p>CPU 使用率: ${cpuUsageEl.textContent}</p>
                    <p>内存 使用率: ${memoryUsageEl.textContent}</p>
                    <p>操作系统: ${osInfoText}</p>
                    <p>Windows 版本: ${winVerText}</p>
                    <p>CPU 核心数: ${cpuCoresText}</p>
                    <p>总物理内存: ${totalMemText}</p>
                    <p>虚拟内存: ${virtualMemoryEl.textContent}</p>
                    <p>运行进程数: ${runningProcessesEl.textContent}</p>
                    </body></html>`;

                addLog('检测到资源超限，准备发送邮件...');
                try {
                    const emailData = {
                        subject: emailSubject,
                        body: fullEmailBody,
                        to_email: receiverEmail,
                        from_email: senderEmail,
                        from_password: senderPassword
                    };
                    const emailResult = await window.electronAPI.sendAlertEmail(emailData);
                    if (emailResult && emailResult.success) {
                        addLog('警报邮件已成功发送。');
                    } else {
                        addLog(`发送警报邮件失败: ${emailResult?.error || '未知错误'}`, 'error');
                    }
                } catch (emailError) {
                    addLog(`发送邮件时发生错误: ${emailError.message}`, 'error');
                }
            }

        } catch (error) {
            addLog(`监控执行中发生错误: ${error.message}`, 'error');
            console.error("Error during monitoring:", error);
            // Optionally stop monitoring on critical error
            // stopMonitoring(); 
        }
    }

    // --- Theme Switching Logic ---
    function applyTheme(theme) {
        if (theme === 'light') {
            document.body.classList.add('light-theme');
            themeToggleBtn.textContent = '🌙'; // Show moon, implies current is light, click for dark
            themeToggleBtn.title = '切换到深色主题';
        } else {
            document.body.classList.remove('light-theme');
            themeToggleBtn.textContent = '☀️'; // Show sun, implies current is dark, click for light
            themeToggleBtn.title = '切换到浅色主题';
        }
    }

    themeToggleBtn.addEventListener('click', () => {
        let currentTheme = localStorage.getItem('theme') || 'dark';
        if (document.body.classList.contains('light-theme')) { // If current is light
            currentTheme = 'dark'; // Switch to dark
        } else {
            currentTheme = 'light'; // Switch to light
        }
        localStorage.setItem('theme', currentTheme);
        applyTheme(currentTheme);
        addLog(`主题已切换为: ${currentTheme === 'light' ? '浅色' : '深色'}`);
    });

    function loadThemePreference() {
        const savedTheme = localStorage.getItem('theme') || 'dark'; // Default to dark
        applyTheme(savedTheme);
    }

    // --- Initialize ---
    loadThemePreference(); // Load theme first
    loadInitialData();
    addLog('渲染进程 (renderer.js) 已加载并初始化。');
});