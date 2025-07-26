<template>
    <div class="history-page">
        <h2>Student Access History</h2>

        <div class="toolbar">
            <input
                v-model.trim="search"
                placeholder="Search name, email or course…"
                class="search-input"
            />
        </div>

        <div v-if="loading" class="loading">Loading…</div>
        <div v-else-if="filtered.length === 0" class="empty">
            No history records match.
        </div>
        <div v-else>
            <div class="table-wrapper">
                <table class="history-table">
                    <colgroup>
                        <col class="col-name"/>
                        <col class="col-email"/>
                        <col class="col-courses"/>
                    </colgroup>
                    <thead>
                        <tr>
                            <th @click="sortBy('lastName')">Name</th>
                            <th @click="sortBy('email')">Email</th>
                            <th>Courses</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="rec in paged" :key="rec._id">
                            <td>{{ rec.firstName }} {{ rec.lastName }}</td>
                            <td>{{ rec.email }}</td>
                            <td>
                            <div class="course-chips">
                                <span
                                    v-for="(c, i) in rec.courseInfo"
                                    :key="i"
                                    class="chip"
                                    :title="`${c.courseID} (${c.term}) — CRN: ${c.CRN}`"
                                >
                                    {{ c.courseID }} ({{ c.term }})
                                </span>
                            </div>
                        </td>
                        </tr>
                    </tbody>
                </table>

                
            </div>
            <div class="man-pager" v-if="totalPages > 1">
                <button :disabled="page===1" @click="page--">‹ Prev</button>
                <span>{{ page }}/{{ totalPages }}</span>
                <button :disabled="page===totalPages" @click="page++">Next ›</button>
            </div>
        </div>
    </div>
</template>

<script>
import { authFetch } from "@/authFetch.js";

export default {
    name: "HistoryPage",
    data() {
        return {
            records: [],
            loading: true,
            search: "",
            sortKey: "acceptedOn",
            sortAsc: false,
            page: 1,
            pageSize: 25,
        };
    },
    computed: {
        sorted() {
            return [...this.records].sort((a, b) => {
                let va = a[this.sortKey], vb = b[this.sortKey];
                if (this.sortKey === "acceptedOn") {
                    va = new Date(va); vb = new Date(vb);
                } else {
                    va = (va || "").toString().toLowerCase();
                    vb = (vb || "").toString().toLowerCase();
                }
                if (va < vb) return this.sortAsc ? -1 : 1;
                if (va > vb) return this.sortAsc ? 1 : -1;
                return 0;
            });
        },
        filtered() {
            const q = this.search.toLowerCase();
            return this.sorted.filter(r => {
                const courses = Array.isArray(r.courseInfo) ? r.courseInfo : [];
                const hay = [
                    r.firstName, r.lastName, r.email,
                    ...courses.map(c => `${c.courseID} ${c.term} ${c.CRN}`)
                ].join(" ").toLowerCase();
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
    methods: {
        async fetchHistory() {
            this.loading = true;
            try {
                const res = await authFetch("/api/history");
                if (!res.ok) throw new Error("Failed to load history");
                this.records = (await res.json()).map(rec => ({
                    ...rec,
                    courseInfo: Array.isArray(rec.courseInfo) ? rec.courseInfo : []
                }));
            } catch (err) {
                console.error(err);
            } finally {
                this.loading = false;
            }
        },
        formatDate(d) {
            return new Date(d).toLocaleString();
        },
        sortBy(key) {
            if (this.sortKey === key) {
                this.sortAsc = !this.sortAsc;
            } else {
                this.sortKey = key;
                this.sortAsc = true;
            }
        }
    },
    watch: {
        search() { this.page = 1 },
        sortKey()  { this.page = 1 },
        sortAsc()  { this.page = 1 },
    },
    mounted() {
        this.fetchHistory();
    }
};
</script>

<style scoped>
.history-page {
    padding: 20px;
    color: #fff;
}
.toolbar {
    margin-bottom: 12px;
}
.search-input {
    width: 50%;
    padding: 6px 8px;
    border-radius: 4px;
    border: 1px solid #666;
    color: #222;
}
.table-wrapper {
    overflow-y: auto;
    max-height: 50vh;
    background: #002f61;
    border-radius: 5px;
    box-sizing: border-box;
}
.history-table {
    width: 100%;
    border-collapse: collapse;
    background: #002f61;
}
.history-table th,
.history-table td {
    padding: 8px;
    border-bottom: 1px solid #444;
    text-align: left;
    font-size: 14px;
}
.history-table th {
    cursor: pointer;
    background: #003976;
    position: sticky;
    top: 0;
}
.course-chips {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 6px;
}
.chip {
    background: rgba(255, 255, 255, 0.1);
    padding: 4px 8px;
    border-radius: 3px;
    font-size: 12px;
    white-space: normal;
    overflow: visible;
    text-overflow: unset;
    cursor: default;
}
.man-pager {
    margin: 10px auto;
    display: flex;
    gap: 12px;
    align-items: center;
    justify-content: center;
    color: #fff;
}
.loading, .empty {
    margin: 20px 0;
    font-size: 16px;
}
</style>