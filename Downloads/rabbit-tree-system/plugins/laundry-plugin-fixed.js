// Laundry Management Plugin for Rabbit Tree System
const LaundryPlugin = {
    name: "laundry-plugin",
    version: "1.0.0",
    description: "Laundry management and tracking",
    async init(System) {
        this.system = System;
        this.laundryTasks = new Map();
        this.inventory = new Map();
        this.initializeFromStorage();
        this.setupUI();
        if (System.appState.debug) {
            console.log("[Laundry Plugin] Loaded for role:", System.appState.currentRole);
        }
    },
    async destroy() {
        this.removeUI();
    },
    initializeFromStorage() {
        const storedTasks = localStorage.getItem("laundry_tasks");
        const storedInventory = localStorage.getItem("laundry_inventory");
        if (storedTasks) {
            this.laundryTasks = new Map(JSON.parse(storedTasks));
        }
        if (storedInventory) {
            this.inventory = new Map(JSON.parse(storedInventory));
        }
    },
    saveToStorage() {
        localStorage.setItem("laundry_tasks", JSON.stringify([...this.laundryTasks]));
        localStorage.setItem("laundry_inventory", JSON.stringify([...this.inventory]));
    },
    setupUI() {
        const tools = document.getElementById("managerTools");
        if (!tools) return;
        const section = document.createElement("div");
        section.className = "plugin-section";
        section.innerHTML = `
            <h3>Laundry Management</h3>
            <div id="laundryTasks"></div>
            <div id="laundryInventory"></div>
        `;
        tools.appendChild(section);
        this.updateUI();
    },
    removeUI() {
        const section = document.querySelector(".plugin-section");
        if (section) section.remove();
    },
    updateUI() {
        const tasksDiv = document.getElementById("laundryTasks");
        const inventoryDiv = document.getElementById("laundryInventory");
        if (tasksDiv) {
            tasksDiv.innerHTML = Array.from(this.laundryTasks.entries())
                .map(([id, task]) => `
                    <div class="laundry-task">
                        <span>${task.description}</span>
                        <span>${task.status}</span>
                    </div>
                `).join("");
        }
        if (inventoryDiv) {
            inventoryDiv.innerHTML = Array.from(this.inventory.entries())
                .map(([id, item]) => `
                    <div class="inventory-item">
                        <span>${item.name}</span>
                        <span>${item.quantity}</span>
                    </div>
                `).join("");
        }
    }
};
if (window.System) {
    window.System.plugins.registerPlugin("laundry-plugin", LaundryPlugin);
}
