// Core System initialization
window.System = {
    appState: {
        currentRole: null,
        debug: false
    },
    initialize() {
        this.notifications = new NotificationSystem();
        this.plugins = new PluginSystem();
        const savedRole = localStorage.getItem("role");
        if (savedRole) {
            this.appState.currentRole = savedRole;
            this.updateUIForRole(savedRole);
        }
    },
    updateUIForRole(role) {
        const roleDisplay = document.getElementById("roleDisplay");
        const roleSelect = document.getElementById("roleSelect");
        const staffView = document.getElementById("staffView");
        const managerTools = document.getElementById("managerTools");
        if (roleDisplay) roleDisplay.classList.remove("hidden");
        if (roleSelect) roleSelect.value = role;
        if (staffView) {
            staffView.classList.toggle("hidden", !["staff", "supervisor"].includes(role));
        }
        if (managerTools) {
            managerTools.classList.toggle("hidden", !["manager", "owner"].includes(role));
        }
    },
    showNotification(message, type = "info") {
        if (this.notifications) {
            this.notifications.show(message, type);
        }
    }
};
