<template>
    <AdminListShell
        title="Access Requests"
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

        <div v-if="loading">Loading…</div>
        <div v-else-if="paged.length === 0">No users match.</div>
        <template v-else>
            <div v-for="req in paged" :key="req._id" class="user-entry">
                <span class="user-line">
                    {{ req.firstName }} {{ req.lastName }} —
                    <template v-if="(req.courseInfo || []).length">
                        <div class="courses-inline">
                            <span class="course-chip">
                                {{ req.courseInfo[0].courseID || 'N/A' }}
                                ({{ req.courseInfo[0].term || 'N/A' }}) · CRN: {{ req.courseInfo[0].CRN || 'N/A' }}
                            </span>
                            <button
                                v-if="req.courseInfo.length > 1"
                                class="link-btn"
                                @click="toggleCourses(req._id)"
                            >
                                {{ expandedCourses[req._id] ? 'Hide' : `+${req.courseInfo.length - 1} more` }}
                            </button>
                        </div>
                        <div v-if="expandedCourses[req._id]" class="courses">
                            <span
                                v-for="(c, idx) in req.courseInfo.slice(1)"
                                :key="req._id + '-' + idx"
                                class="course-chip"
                            >
                                {{ c.courseID }} ({{ c.term }}) · CRN: {{ c.CRN }}
                            </span>
                        </div>
                    </template>
                    <br>
                    <small>{{ req.email }}</small>
                </span>
                <div class="actions">
                    <button @click="accept(req.userID)">ACCEPT</button>
                    <button @click="deny(req.userID)">DENY</button>
                </div>
            </div>
        </template>
    </AdminListShell>
</template>

<script>
import AdminListShell from "@/components/AdminListShell.vue";
import { authFetch } from "@/authFetch.js";

export default {
    components: { AdminListShell },
    data() {
        return {
            requests: [],
            expandedCourses: {},
            loading: true,
            search: "",
            page: 1,
            pageSize: 50
        };
    },
    computed: {
        courses() {
            const set = new Set(this.requests.map(r => r.courseID).filter(Boolean));
            return Array.from(set).sort();
        },
        filtered() {
            const q = (this.search || "").toLowerCase();
            return this.requests.filter(r => {
                const hay = [
                    r.firstName,
                    r.lastName,
                    r.email,
                    ...(r.courseInfo || []).map(c => `${c.courseID} ${c.CRN} ${c.term}`)
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
        this.fetchRequests();
    },
    methods: {
        toggleCourses(id) {
            this.expandedCourses[id] = !this.expandedCourses[id];
        },
        async fetchRequests() {
            this.loading = true;
            try {
                const res = await authFetch("/api/access-requests");
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.error || "Failed to fetch requests");
                }
                this.requests = await res.json();
            } catch (err) {
                console.error("Failed to fetch requests:", err);
            } finally {
                this.loading = false;
            }
        },
        async accept(userId) {
            try {
                const res = await authFetch(`/api/users/${userId}/access/accept`, {
                    method: "POST"
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.error || "Accept failed");
                }
                await this.fetchRequests();
            } catch (err) {
                console.error("Accept failed:", err);
            }
        },
        async deny(userId) {
            try {
                const res = await authFetch(`/api/users/${userId}/access`, {
                    method: "DELETE"
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.error || "Deny failed");
                }
                await this.fetchRequests();
            } catch (err) {
                console.error("Deny failed:", err);
            }
        }
    }
};
</script>

<style scoped>
.search-input {
    min-width: 40%;
    padding: 4px 6px;
    border-radius: 4px;
    border: 1px solid #888;
}
</style>