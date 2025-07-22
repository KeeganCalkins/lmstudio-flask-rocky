<template>
    <AdminListShell
        title="Key Management"
        :page="page"
        :pages="totalPages"
        @update:page="page = $event"
    >
        <template #toolbar>
            <input
                v-model.trim="search"
                placeholder="Search name/email/course..."
                class="search-input"
            />
        </template>

            <div v-if="loading">Loading...</div>
            <div v-else-if="paged.length === 0">No users match.</div>
            <template v-else>
                <div v-for="user in paged" :key="user._id" class="user-entry">
                    <span class="user-line">
                        {{ user.firstName }} {{ user.lastName }} —
                        <template v-if="(user.courseInfo || []).length">
                            <span class="courses-inline">
                                <span class="course-chip">
                                    {{ user.courseInfo[0].courseID || 'N/A' }}
                                    ({{ user.courseInfo[0].term || 'N/A' }}) · CRN: {{ user.courseInfo[0].CRN || 'N/A' }}
                                </span>
                                <button
                                    v-if="user.courseInfo.length > 1"
                                    class="link-btn"
                                    @click="toggleCourses(user._id)"
                                >
                                    {{ expandedCourses[user._id] ? 'Hide' : `+${user.courseInfo.length - 1} more` }}
                                </button>
                            </span>
                            <div v-if="expandedCourses[user._id]" class="courses">
                                <span
                                    v-for="(c, idx) in user.courseInfo.slice(1)"
                                    :key="user._id + '-' + idx"
                                    class="course-chip"
                                >
                                    {{ c.courseID }} ({{ c.term }}) · CRN: {{ c.CRN }}
                                </span>
                            </div>
                        </template>
                        <br>
                        <small>
                            {{ user.email }}
                            <span v-if="keyState[user._id]?.visible">
                                &nbsp;—&nbsp;
                                <span v-if="keyState[user._id].loading">Loading key…</span>
                                <span v-else-if="keyState[user._id].value">Key: {{ keyState[user._id].value }}</span>
                                <span v-else>No key generated</span>
                            </span>
                        </small>
                    </span>
                    <div class="actions">
                        <button
                            v-if="!keyState[user._id]?.visible"
                            @click="showKey(user._id)"
                        >Show Key</button>

                        <button
                            v-else
                            @click="hideKey(user._id)"
                        >Hide</button>

                      <button @click="generateKey(user._id)">🔑 Generate</button>
                    </div>
                </div>
            </template>
    </AdminListShell>
</template>

<script>
import AdminListShell from "@/components/AdminListShell.vue";
import { authFetch } from '@/authFetch.js';

export default {
    components: { AdminListShell },
    data() {
        return {
            users: [],
            loading: true,
            keyState: {}, // { [userId]: {visible:boolean, loading:boolean, value:string|null} }
            expandedCourses: {},
            search: "",
            page: 1,
            pageSize: 50
        }
    },
    computed: {
        filtered() {
            const q = this.search.toLowerCase();
            return this.users.filter(u => {
                const hay = [
                    u.firstName,
                    u.lastName,
                    u.email,
                    ...(u.courseInfo || []).map(c => `${c.courseID} ${c.CRN} ${c.term}`)
                ].filter(Boolean).join(" ").toLowerCase();
                return !q || hay.includes(q);
            });
        },
        totalPages() {
            return Math.max(1, Math.ceil(this.filtered.length / this.pageSize));
        },
        paged() {
            const start = (this.page - 1) * this.pageSize;
            return this.filtered.slice(start, start + this.pageSize);
        }
    },
    watch: {
        filtered() {
            this.page = 1;
        }
    },
    mounted() {
        this.fetchUsers();
    },
    methods: {
        toggleCourses(id) {
            this.expandedCourses[id] = !this.expandedCourses[id];
        },
        async fetchUsers() {
            try {
                const res = await authFetch("/api/users");
                if (!res.ok) throw new Error("Failed to fetch users");
                const allUsers = await res.json();
                this.users = allUsers.filter(u => u.hasAccess || u.isAdmin);
                this.loading = false;
            } catch (err) {
                console.error("Failed to load users or keys:", err);
            }
        },
        async showKey(userId) {
            // init state
            if (!this.keyState[userId]) {
                this.keyState[userId] = { visible: true, loading: true, value: null };
            } else {
                this.keyState[userId].visible = true;
                this.keyState[userId].loading = true;
            }

            try {
                const res = await authFetch(`/api/users/${userId}/apikey`);
                if (!res.ok) throw new Error((await res.json()).error || "Fetch failed");
                const { api_key } = await res.json();
                this.keyState[userId].value = api_key || null;
            } catch (e) {
                console.error(e);
                this.keyState[userId].value = null;
            } finally {
                this.keyState[userId].loading = false;
            }
        },
        hideKey(userId) {
            if (this.keyState[userId]) {
                this.keyState[userId].visible = false;
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
                // Update local state if the key is currently visible
                if (this.keyState[userId]) {
                    this.keyState[userId].value = api_key;
                }
            } catch (err) {
                console.error("Failed to generate key:", err);
                alert("Could not generate key: " + err.message);
            }
        }
    }
}
</script>

<style scoped>
.search-input {
    min-width: 40%;
    padding: 4px 6px;
    border-radius: 4px;
    border: 1px solid #888;
}
</style>