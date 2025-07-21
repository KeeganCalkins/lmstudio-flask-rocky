<template>
    <div id="container">
        <div id="context">
            <h3>Key Management</h3>
        </div>

        <div id="list">
            <div v-if="loading">Loading...</div>
            <div v-else-if="users.length === 0">No eligible users found.</div>
            <div v-else>
                <div v-for="user in users" :key="user._id" class="user-entry">
                    <span class="user-line">
                        {{ user.firstName }} {{ user.lastName }} ({{ user.email }}) - {{ user.term }}
                        <br v-if="user.apiKey">
                        <small v-if="user.apiKey">Key: {{ user.apiKey }}</small>
                    </span>
                    <button @click="generateKey(user._id)">🔑 Generate</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { authFetch } from '@/authFetch.js';

export default {
    data() {
        return {
            users: [],
            loading: true,
        }
    },
    mounted() {
        this.fetchUsers();
    },
    methods: {
        async fetchUsers() {
            try {
                const res = await authFetch("/api/users");
                if (!res.ok) throw new Error("Failed to fetch users");
                const allUsers = await res.json();
                const filtered = allUsers.filter(u => u.hasAccess || u.isAdmin);
                
                // Fetch keys for each user in parallel
                for (const user of filtered) {
                    const keyRes = await authFetch(`/api/users/${user._id}/apikey`);
                    if (keyRes.ok) {
                        const { api_key } = await keyRes.json();
                        user.apiKey = api_key;
                    } else {
                        user.apiKey = null;
                    }
                }

                this.users = filtered;
                this.loading = false;
            } catch (err) {
                console.error("Failed to load users or keys:", err);
            }
        },
        async generateKey(userId) {
            if (!confirm("Generate new key for this user?")) return;
            try {
                const res = await authFetch(`/api/users/${userId}/apikey`, {
                    method: "POST"
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.error || "Key generation failed");
                }

                const { api_key } = await res.json();
                this.users = this.users.map(u =>
                    u._id === userId ? { ...u, apiKey: api_key } : u
                );
            } catch (err) {
                console.error("Failed to generate key:", err);
                alert("Could not generate key: " + err.message);
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

.user-line small {
    display: block;
    margin: 4px 0 0 0;
    text-align: left;
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