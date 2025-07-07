<template>
    <div id="container">
        <div id="context">
            <h3>Key Management</h3>
        </div>

        <div id="list">
            <div v-if="users.length === 0">No users with access found.</div>
            <div v-for="user in users" :key="user._id" class="user-entry">
                <span class="user-line">
                    {{ user.firstName }} {{ user.lastName }} ({{ user.email }})
                    <span v-if="user.apiKey"> — Key: {{ user.apiKey }}</span>
                </span>
                <button @click="generateKey(user._id)">🔑 Generate</button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            users: []
        }
    },
    mounted() {
        this.fetchUsers();
    },
    methods: {
        async fetchUsers() {
            try {
                const res = await fetch("/api/users");
                const allUsers = await res.json();
                const filtered = allUsers.filter(u => u.hasAccess);
                
                // Fetch keys for each user in parallel
                for (const user of filtered) {
                    const keyRes = await fetch(`/api/users/${user._id}/apikey`);
                    if (keyRes.ok) {
                        const { api_key } = await keyRes.json();
                        user.apiKey = api_key;
                    } else {
                        user.apiKey = null;
                    }
                }

                this.users = filtered;
            } catch (err) {
                console.error("Failed to load users or keys:", err);
            }
        },
        async generateKey(userId) {
            if (!confirm("Generate new key for this user?")) return;
            try {
                const res = await fetch(`/api/users/${userId}/apikey`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" }
                });
                if (!res.ok) throw new Error("Key generation failed");

                const { api_key } = await res.json();
                this.users = this.users.map(u =>
                    u._id === userId ? { ...u, apiKey: api_key } : u
                );
            } catch (err) {
                console.error("Failed to generate key:", err);
                alert("Could not generate key.");
            }
        }
    }
}
</script>

<style scoped>
#container {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
}

#context {
    margin: 20px;
    padding: 5px;
    font-size: 16px;
    font-weight: bold;
    color: white;
}

.user-entry {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    padding: 4px 0;
    border-bottom: 1px solid #444;
}

.user-line {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 80%;
}

#list {
    overflow-y: auto;
    max-height: 250px;
    width: 100%;
    background: #002f61;
    margin: 10px auto 0 auto;
    padding: 10px;
    border-radius: 5px;
    color: white;
    font-family: sans-serif;
    box-sizing: border-box;
}
</style>