// Plugin system for Rabbit Tree System
class PluginSystem {
    constructor() {
        this.plugins = new Map();
        this.enabledPlugins = new Set();
        this.initializeFromStorage();
    }
    initializeFromStorage() {
        const stored = localStorage.getItem("enabled_plugins");
        if (stored) {
            this.enabledPlugins = new Set(JSON.parse(stored));
        }
    }
    saveToStorage() {
        localStorage.setItem("enabled_plugins", JSON.stringify([...this.enabledPlugins]));
    }
    async loadPlugin(pluginName, scriptPath) {
        if (this.plugins.has(pluginName)) {
            console.warn(`Plugin ${pluginName} is already loaded`);
            return false;
        }
        try {
            const script = document.createElement("script");
            script.src = scriptPath;
            script.async = true;
            await new Promise((resolve, reject) => {
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
            return true;
        } catch (error) {
            console.error(`Failed to load plugin ${pluginName}:`, error);
            return false;
        }
    }
    async initializePlugin(pluginName) {
        const plugin = this.plugins.get(pluginName);
        if (!plugin) return false;
        try {
            if (typeof plugin.init === "function") {
                await plugin.init(window.System);
            }
            this.enabledPlugins.add(pluginName);
            this.saveToStorage();
            return true;
        } catch (error) {
            console.error(`Failed to initialize plugin ${pluginName}:`, error);
            return false;
        }
    }
    async disablePlugin(pluginName) {
        const plugin = this.plugins.get(pluginName);
        if (!plugin) return false;
        try {
            if (typeof plugin.destroy === "function") {
                await plugin.destroy();
            }
            this.enabledPlugins.delete(pluginName);
            this.saveToStorage();
            return true;
        } catch (error) {
            console.error(`Failed to disable plugin ${pluginName}:`, error);
            return false;
        }
    }
    registerPlugin(pluginName, plugin) {
        if (this.plugins.has(pluginName)) {
            console.warn(`Plugin ${pluginName} is already registered`);
            return false;
        }
        if (typeof plugin !== "object") {
            console.error(`Invalid plugin structure for ${pluginName}`);
            return false;
        }
        this.plugins.set(pluginName, plugin);
        return true;
    }
    getLoadedPlugins() {
        return Array.from(this.plugins.keys());
    }
    getEnabledPlugins() {
        return Array.from(this.enabledPlugins);
    }
    isPluginEnabled(pluginName) {
        return this.enabledPlugins.has(pluginName);
    }
}
window.PluginSystem = PluginSystem;
