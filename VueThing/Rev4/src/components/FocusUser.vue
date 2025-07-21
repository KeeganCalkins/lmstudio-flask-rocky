<template>
    <div id="focusUser">
        <div v-if="loading">Loading...</div>

        <template v-else-if="!hasAccess">
            <h2 v-if="!isPending">Request Access</h2>
            <div v-if="!isPending">
                <h4>Course Information</h4>
                <p class="hint">Which course(s) do you need this for?</p>

                <div
                    v-for="(c, idx) in courses"
                    :key="idx"
                    class="course-row"
                >
                    <input
                        v-model="c.CRN"
                        placeholder="CRN"
                        required
                    />
                    <input
                        v-model="c.courseID"
                        placeholder="Course ID (e.g. CS101)"
                        required
                    />
                    <input
                        v-model="c.term"
                        placeholder="Term (e.g. Fall2025)"
                        required
                    />
                    <button
                        type="button"
                        @click="removeCourse(idx)"
                        v-if="courses.length > 1"
                    >
                        ✕
                    </button>
                </div>

                <button 
                    id="add-course" 
                    type="button" 
                    @click="addCourse"
                    v-if="courses.length < 3"
                >
                    + Add Course
                </button>

                <br />

                <button id="request" @click="requestAPIAccess">
                    <b>Request Access</b>
                </button>
            </div>
            <h2 v-else>Waiting for access…</h2>
        </template>

        <template v-else-if="hasAccess && !isKey">
            <h2>No API Key Found</h2>
            <button id="request" @click="generateNewKey">
                <b>Generate Key</b>
            </button>
        </template>

        <template v-else>
            <h3>Key:</h3>
            <input :value="key" readonly>
            <p></p>
            <button id="request" @click="generateNewKey">
                <b>Another?</b>
            </button>
        </template>

    </div>
</template>

<script>
import { authFetch } from '@/authFetch.js';

export default {
    data() {
        return {
            isKey: false,
            key: null,
            hasAccess: false,
            isPending: false,
            userId: null,
            loading: true,
            courses: [
                {
                    CRN: '',
                    courseID: '',
                    term: ''
                }
            ]
        }
    },
    async mounted() {
        await this.fetchUserAccessStatus();
    },
    methods: {
        addCourse() {
            if (this.courses.length < 3) {
                this.courses.push({ CRN: '', courseID: '', term: '' });
            }
        },
        removeCourse(idx) {
            this.courses.splice(idx, 1);
        },
        async fetchUserAccessStatus() {
            try {
                const resUser = await authFetch(`/api/me`);
                if (!resUser.ok) throw new Error("Not signed in");
                const dataUser = await resUser.json();
                
                // get user id and hasAccess flag
                this.userId = dataUser._id;
                this.hasAccess = dataUser.hasAccess;

                const resPending = await authFetch(`/api/users/${this.userId}/access/pending`);
                if (!resPending.ok) throw new Error("Pending check failed");
                const dataPending = await resPending.json();
                this.isPending = dataPending.pending;

                if (this.hasAccess) {
                    await this.fetchExistingKey();
                }
                this.loading = false;
            } catch (err) {
                console.error("Error fetching user status:", err);
            }
        },
        async requestAPIAccess() {
            try {
                if (
                    this.courses.length === 0 ||
                    this.courses.some(
                        c => !c.CRN.trim() || !c.courseID.trim() || !c.term.trim()
                    )
                ) {
                    alert('Please fill all course fields (CRN, Course ID, Term).');
                    return;
                }
                const res = await authFetch(`/api/users/${this.userId}/access`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ courses: this.courses })
                });
                if (!res.ok) { 
                    const err = await res.json();
                    throw new Error(err.error || "Access request failed");
                }
                this.isPending = true;
            } catch (err) {
                console.error("API error:", err);
                alert("Could not request access: " + err.message);
            }
        },
        async fetchExistingKey() {
            try {
                const res = await authFetch(`/api/users/${this.userId}/apikey`);
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.error || 'Failed to fetch API key');
                }
                    const data = await res.json();
                if (data.api_key) {
                    this.key   = data.api_key;
                    this.isKey = true;
                }
            } catch (err) {
                console.error('Failed to fetch API key:', err);
            }
        },
        async generateNewKey() {
            try {
                const res = await authFetch(`/api/users/${this.userId}/apikey`, {
                    method: 'POST'
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.error || 'Key request failed');
                }
                const data = await res.json();
                this.key   = data.api_key;
                this.isKey = true;
            } catch (err) {
                console.error('API error:', err);
                alert('Could not generate key: ' + err.message);
            }
        },
    }
}
</script>

<style scoped>
#request {
    height: 40px;
    width: 140px;
    color: #efab00;
    background: #003976;
    border-color: #efab00;
    border-width: 4px;
    border-radius: 20px;
    margin-top: 10px;
}

#add-course {
    margin-top: 6px;
    background: #225b9e;
    color: #fff;
    border: none;
    padding: 4px 10px;
    border-radius: 4px;
}
.course-row {
    display: flex;
    gap: 6px;
    margin-bottom: 4px;
}
.course-row input {
    flex: 1;
}
.hint {
    font-size: 12px;
    color: #ccc;
}
</style>

