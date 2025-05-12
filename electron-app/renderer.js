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
    const emailCooldownInput = document.getElementById('emailCooldownInput'); // 修正 ID 以匹配 HTML
    const saveConfigBtn = document.getElementById('save-config-btn');

    // Controls
    const startMonitorBtn = document.getElementById('start-monitor-btn');
    const stopMonitorBtn = document.getElementById('stop-monitor-btn');

    // Log and Status
    const logOutputEl = document.getElementById('log-output');
    const statusMessageEl = document.getElementById('status-message');
    const clearLogBtn = document.getElementById('clear-log-btn'); // 新增：清除日志按钮
    const toggleAutoClearBtn = document.getElementById('toggle-auto-clear-btn'); // 新增：切换自动清除设置按钮
    const autoClearSettingsDiv = document.getElementById('auto-clear-settings'); // 新增：自动清除设置区域
    const autoClearIntervalInput = document.getElementById('auto-clear-interval'); // 新增：自动清除间隔输入
    const saveAutoClearBtn = document.getElementById('save-auto-clear-btn'); // 新增：保存自动清除设置按钮


    // Theme Toggle
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const togglePasswordVisibilityBtn = document.getElementById('toggle-password-visibility'); // 新增：密码可见性切换按钮

    let мониторингИнтервалаId = null; // Variable to hold the interval ID for monitoring
    let isMonitoringActive = false;
    let lastCpuAlertTime = 0; // 上次发送 CPU 警报的时间戳 (ms)
    let lastMemoryAlertTime = 0; // 上次发送内存警报的时间戳 (ms)
    let autoClearTimerId = null; // 自动清除日志的计时器 ID
    let currentAutoClearInterval = 0; // 当前自动清除间隔 (秒), 0 = 禁用

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

    function clearLogs() {
        logOutputEl.innerHTML = ''; // 清空日志区域
        addLog('日志已手动清除。', 'info'); // 添加一条清除记录
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
                senderPasswordInput.value = config.sender_password || ''; // 启用密码自动填充
                receiverEmailInput.value = config.receiver_email || '';
                if (config.check_interval_minutes) {
                    checkIntervalInput.value = config.check_interval_minutes;
                }
                // 加载监控阈值
                if (config.cpu_threshold) {
                    cpuThresholdInput.value = config.cpu_threshold;
                }
                if (config.memory_threshold) {
                    memoryThresholdInput.value = config.memory_threshold;
                }
                // 加载邮件冷却时间
                if (config.email_cooldown) {
                    emailCooldownInput.value = config.email_cooldown;
                }
                addLog('邮件和监控配置加载完成。');
            } else {
                addLog(`加载配置失败: ${config?.error || '未能读取配置'}`, 'warning');
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
            clear_console_seconds: "3600", // This value is from old config, keep it for python_adapter compatibility
            cpu_threshold: cpuThresholdInput.value,
            memory_threshold: memoryThresholdInput.value,
            email_cooldown: emailCooldownInput.value // 新增
        };
        addLog('正在保存配置...');
        try {
            const result = await window.electronAPI.saveConfig(configData);
            if (result && result.success) {
                addLog('配置已成功保存。');
            } else {
                addLog(`保存配置失败: ${result?.error || '未知错误'}`, 'error');
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
            let sendCpuAlert = false;
            let sendMemoryAlert = false;
            const now = Date.now();
            const cooldownSeconds = parseInt(emailCooldownInput.value, 10);
            const cooldownMillis = isNaN(cooldownSeconds) ? 600 * 1000 : cooldownSeconds * 1000; // 默认10分钟冷却

            // 检查 CPU 阈值和冷却时间
            if (typeof cpu === 'number' && cpu > cpuThreshold) {
                addLog(`警告: CPU 使用率 ${cpu.toFixed(1)}% 超过阈值 ${cpuThreshold}%`, 'warning');
                if (now - lastCpuAlertTime > cooldownMillis) {
                    sendCpuAlert = true;
                    lastCpuAlertTime = now; // 立即更新时间戳以启动冷却
                    addLog('CPU 警报条件触发，冷却计时器已启动。', 'info');
                    emailBodyParts.push(`CPU 使用率 (${cpu.toFixed(1)}%) 超过阈值 (${cpuThreshold}%).`);
                } else {
                    // 仅在实际处于冷却状态时记录日志，避免每次检查都输出
                    if(lastCpuAlertTime !== 0) { // 确保不是初始状态
                       addLog(`CPU 警报冷却中，剩余 ${Math.ceil((cooldownMillis - (now - lastCpuAlertTime)) / 1000)} 秒。`, 'info');
                    }
                }
            }

            // 检查内存阈值和冷却时间
            if (typeof mem === 'number' && mem > memoryThreshold) {
                addLog(`警告: 内存使用率 ${mem.toFixed(1)}% 超过阈值 ${memoryThreshold}%`, 'warning');
                if (now - lastMemoryAlertTime > cooldownMillis) {
                    sendMemoryAlert = true;
                    lastMemoryAlertTime = now; // 立即更新时间戳以启动冷却
                    addLog('内存警报条件触发，冷却计时器已启动。', 'info');
                    // 如果 CPU 警报也要发送，避免重复添加通用信息
                    if (!sendCpuAlert) {
                         emailBodyParts.push(`内存使用率 (${mem.toFixed(1)}%) 超过阈值 (${memoryThreshold}%).`);
                    } else {
                         // 如果 CPU 警报已添加，只补充内存信息
                         emailBodyParts.push(`同时，内存使用率 (${mem.toFixed(1)}%) 也超过阈值 (${memoryThreshold}%).`);
                    }
                } else {
                     // 仅在实际处于冷却状态时记录日志
                     if(lastMemoryAlertTime !== 0) { // 确保不是初始状态
                        addLog(`内存警报冷却中，剩余 ${Math.ceil((cooldownMillis - (now - lastMemoryAlertTime)) / 1000)} 秒。`, 'info');
                     }
                }
            }

            // 如果需要发送任一警报
            if (sendCpuAlert || sendMemoryAlert) {
                const senderEmail = senderEmailInput.value;
                const senderPassword = senderPasswordInput.value;
                const receiverEmail = receiverEmailInput.value;

                if (!senderEmail || !senderPassword || !receiverEmail) {
                    addLog('邮件配置不完整，无法发送警报邮件。', 'error');
                    return; // 不发送邮件，但冷却时间不会更新
                }

                // 构建邮件正文
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

                addLog('检测到资源超限且冷却时间已过，准备发送邮件...');
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
                        // 时间戳已在决定发送时更新，此处无需重复更新
                        // if (sendCpuAlert) {
                        //     // lastCpuAlertTime = now; // 已提前更新
                        //     // addLog('CPU 警报冷却计时器已重置。', 'info');
                        // }
                        // if (sendMemoryAlert) {
                        //     // lastMemoryAlertTime = now; // 已提前更新
                        //     // addLog('内存警报冷却计时器已重置。', 'info');
                        // }
                    } else {
                        addLog(`发送警报邮件失败: ${emailResult?.error || '未知错误'}`, 'error');
                        // 发送失败，不更新时间戳，下次还会尝试
                    }
                } catch (emailError) {
                    addLog(`发送邮件时发生错误: ${emailError.message}`, 'error');
                     // 发送失败，不更新时间戳
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

    // --- Password Visibility Toggle ---
    togglePasswordVisibilityBtn.addEventListener('click', () => {
        const isPassword = senderPasswordInput.type === 'password';
        senderPasswordInput.type = isPassword ? 'text' : 'password';
        togglePasswordVisibilityBtn.textContent = isPassword ? '🙈' : '👁️'; // Change icon
        togglePasswordVisibilityBtn.title = isPassword ? '隐藏密码' : '显示密码';
    });


    function loadThemePreference() {
        const savedTheme = localStorage.getItem('theme') || 'dark'; // Default to dark
        applyTheme(savedTheme);
    }

    // --- Log Clearing Logic ---
    clearLogBtn.addEventListener('click', clearLogs);

    toggleAutoClearBtn.addEventListener('click', () => {
        const isHidden = autoClearSettingsDiv.classList.toggle('hidden');
        toggleAutoClearBtn.textContent = isHidden ? '▼' : '▲'; // Toggle arrow icon
    });

    function stopAutoClearTimer() {
        if (autoClearTimerId) {
            clearInterval(autoClearTimerId);
            autoClearTimerId = null;
            addLog('自动清除日志已停止。', 'info');
        }
    }

    function startAutoClearTimer(intervalSeconds) {
        stopAutoClearTimer(); // Stop any existing timer first
        if (intervalSeconds > 0) {
            currentAutoClearInterval = intervalSeconds;
            const intervalMillis = intervalSeconds * 1000;
            autoClearTimerId = setInterval(() => {
                addLog(`根据设置 (${intervalSeconds}秒)，自动清除日志...`, 'info');
                logOutputEl.innerHTML = ''; // Clear logs
            }, intervalMillis);
            addLog(`自动清除日志已启动，间隔 ${intervalSeconds} 秒。`, 'info');
        } else {
             currentAutoClearInterval = 0; // Ensure interval is 0 if disabled
        }
    }

    saveAutoClearBtn.addEventListener('click', () => {
        const intervalValue = parseInt(autoClearIntervalInput.value, 10);
        if (isNaN(intervalValue) || intervalValue < 0) {
            addLog('无效的自动清除间隔，请输入一个非负整数。', 'error');
            return;
        }
        localStorage.setItem('autoClearLogInterval', intervalValue); // Save to localStorage
        startAutoClearTimer(intervalValue);
        addLog(`自动清除间隔已保存为 ${intervalValue} 秒 ${intervalValue === 0 ? '(已禁用)' : ''}。`, 'info');
        autoClearSettingsDiv.classList.add('hidden'); // Hide settings after saving
        toggleAutoClearBtn.textContent = '▼';
    });

    function loadAutoClearSetting() {
        const savedInterval = localStorage.getItem('autoClearLogInterval');
        const intervalSeconds = parseInt(savedInterval, 10);
        if (!isNaN(intervalSeconds) && intervalSeconds >= 0) {
            autoClearIntervalInput.value = intervalSeconds;
            startAutoClearTimer(intervalSeconds); // Start timer based on saved value
        } else {
            autoClearIntervalInput.value = 0; // Default to 0 if not saved or invalid
            startAutoClearTimer(0); // Ensure timer is stopped if default
        }
    }


    // --- Initialize ---
    loadThemePreference(); // Load theme first
    loadInitialData();
    loadAutoClearSetting(); // Load auto-clear setting
    addLog('渲染进程 (renderer.js) 已加载并初始化。');
});