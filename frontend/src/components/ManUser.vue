<template>
    <AdminListShell
        title="User Management"
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
            <label>
                <input type="checkbox" v-model="filters.hasAccess">
                Has Access
            </label>
            <label>
                <input type="checkbox" v-model="filters.isAdmin">
                Admins
            </label>
        </template>

        <div v-if="loading">Loading…</div>
        <div v-else-if="paged.length === 0">No users match.</div>
        <template v-else>
            <div v-for="user in paged" :key="user._id" class="user-entry">
                <span class="user-line">
                    {{ user.firstName }} {{ user.lastName }}
                    <template v-if="(user.courseInfo || []).length">
                        <div class="courses-inline">
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
                        </div>
                        <div v-if="expandedCourses[user._id]" class="courses">
                            <span
                                v-for="c in user.courseInfo.slice(1)"
                                :key="c.CRN + c.courseID + c.term"
                                class="course-chip"
                            >
                                {{ c.courseID }} ({{ c.term }}) · CRN: {{ c.CRN }}
                            </span>
                        </div>
                    </template>
                    Access: <strong>{{ user.hasAccess ? "Yes" : "No" }}</strong>
                    <br>
                    <small>{{ user.email }}</small>
                </span>
                <div class="actions">
                    <button
                        v-if="user.hasAccess"
                        @click="revokeAccess(user._id)"
                    >
                        Remove Access
                    </button>
                    <button v-else disabled>No Access</button>

                    <button
                        v-if="!user.isAdmin"
                        @click="makeAdmin(user._id)"
                    >
                        Set Admin
                    </button>
                    <button
                        v-else
                        @click="removeAdmin(user._id)"
                    >
                        Remove Admin
                    </button>
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
                expandedCourses: {},
                loading: true,
                search: "",
                filters: {
                    hasAccess: false,
                    isAdmin: false
                },
                page: 1,
                pageSize: 50,
            };
        },
        computed: {
            filtered() {
                const q = this.search.toLowerCase();
                return this.users.filter(u => {
                    const hit =
                        !q ||
                        (
                            `${u.firstName} ${u.lastName} ${u.email}` + ' ' +
                            (u.courseInfo || [])
                                .map(c => `${c.courseID} ${c.CRN} ${c.term}`)
                                .join(' ')
                        ).toLowerCase().includes(q);

                    const accessOK = !this.filters.hasAccess || u.hasAccess;
                    const adminOK = !this.filters.isAdmin || u.isAdmin;

                    return hit && accessOK && adminOK;
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
                    const res = await authFetch('/api/users');
                    if (!res.ok) {
                        const err = await res.json();
                        throw new Error(err.error || 'Failed to fetch users');
                    }
                    this.users = await res.json();
                    this.loading = false;
                } catch (err) {
                    console.error('Failed to fetch users:', err);
                }
            },
            async revokeAccess(userId) {
                if (!confirm('Revoke access for this user?')) return;
                try {
                    const res = await authFetch(`/api/users/${userId}/access/revoke`, { method: 'POST' });
                    if (!res.ok) throw new Error((await res.json()).error || 'Failed to revoke');
                    await this.fetchUsers();
                } catch (e) {
                    console.error(e);
                    alert('Could not revoke access: ' + e.message);
                }
            },
            async makeAdmin(userId) {
                if (!confirm('Make this user an admin?')) return;
                try {
                    const res = await authFetch(`/api/users/${userId}/admin`, { method: 'POST' });
                    if (!res.ok) throw new Error((await res.json()).error || 'Failed to set admin');
                    await this.fetchUsers();
                } catch (e) {
                    console.error(e);
                    alert('Could not set admin: ' + e.message);
                }
            },
            async removeAdmin(userId) {
                if (!confirm('Remove admin from this user?')) return;
                try {
                    const res = await authFetch(`/api/users/${userId}/admin`, { method: 'DELETE' });
                    if (!res.ok) throw new Error((await res.json()).error || 'Failed to remove admin');
                    await this.fetchUsers();
                } catch (e) {
                    console.error(e);
                    alert('Could not remove admin: ' + e.message);
                }
            }
        },
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