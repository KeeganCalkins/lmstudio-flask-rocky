<template>
    <div id="container">
        <div id="context">
            <h3>Access Requests</h3>
        </div>

        <div id="list">
            <div v-if="loading">Loading...</div>
            <div v-else-if="requests.length === 0">No pending requests.</div>
            <div v-else>
                <div v-for="req in requests" :key="req._id" class="user-entry">
                    <span class="user-line">
                        {{ req.firstName }} {{ req.lastName }} ({{ req.email }}) — {{ req.courseID }}<br>
                    </span>
                    <div>
                        <button @click="accept(req.userID)">ACCEPT</button>
                        <button @click="deny(req.userID)">DENY</button>
                    </div>
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
            requests: [],
            loading: true,
        };
    },
    mounted() {
            this.fetchRequests();
    },
    methods: {
        async fetchRequests() {
            this.loading = true;
            try {
                const res = await authFetch('/api/access-requests');
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.error || 'Failed to fetch requests');
                }
                this.requests = await res.json();
            } catch (err) {
                console.error('Failed to fetch requests:', err);
            } finally {
                this.loading = false;
            }
        },
        async accept(userId) {
            try {
                const res = await authFetch(`/api/users/${userId}/access/accept`, {
                    method: 'POST'
                })
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.error || 'Accept failed');
                }
                await this.fetchRequests();
            } catch (err) {
                console.error('Accept failed:', err);
            }
        },
        async deny(userId) {
            try {
                const res = await authFetch(`/api/users/${userId}/access`, {
                    method: 'DELETE'
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.error || 'Deny failed');
                }
                await this.fetchRequests();
            } catch (err) {
                console.error('Deny failed:', err);
            }
        },
    }
};
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