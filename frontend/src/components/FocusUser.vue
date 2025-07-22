<template>
    <div id="focusUser">
        <div v-if="loading">Loading...</div>

        <template v-else-if="!hasAccess">
            <h2 v-if="!isPending">Request Access</h2>
            <div v-if="!isPending">
                <h4>Course Information</h4>
                <p class="hint">Which course(s) do you need Rocky for?</p>

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
                    <select v-model="c.term" class="term-select" required>
                        <option disabled value="">Select term</option>
                        <option v-for="t in termOptions" :key="t" :value="t">{{ t }}</option>
                    </select>
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
import { useUserStore }   from '@/stores/userStores.js'

export default {
    data() {
        return {
            store: useUserStore(),
            courses: [
                { CRN: '', courseID: '', term: '' }
            ]
        }
    },
    async mounted() {
        await this.store.init()
    },
    computed: {
        loading()    { return !this.store.loaded },
        hasAccess()  { return this.store.hasAccess },
        isPending()  { return this.store.pending },
        isKey()      { return this.store.hasKey },
        key()        { return this.store.apiKey },
        userId()     { return this.store._id },
        termOptions() {
            const seasons = ["Spring", "Summer", "Fall"];
            const now = new Date();
            const m = now.getMonth(); // 0-11
            let curIdx = m < 4 ? 0 : m < 8 ? 1 : 2; // Spring Jan–Apr, Summer May–Aug, Fall Sep–Dec
            let year = now.getFullYear();
            const opts = [];
            for (let off = -1; off <= 2; off++) {
                let idx = curIdx + off;
                let y = year;
                if (idx < 0) { idx += seasons.length; y--; }
                if (idx >= seasons.length) { idx -= seasons.length; y++; }
                opts.push(`${seasons[idx]} ${y}`);
            }
            return opts; // [prev, current, next1, next2]
        }
    },
    methods: {
        addCourse() {
            if (this.courses.length < 3) {
                this.courses.push({ CRN:'', courseID:'', term: this.termOptions[1] });
            }
        },
        removeCourse(idx) {
            this.courses.splice(idx, 1);
        },
        async requestAPIAccess() {
            try {
                await this.store.requestAccess(this.courses)
            } catch (e) {
                console.error('API error:', e)
                alert(e.message)
            }
        },
        async generateNewKey() {
            try {
                await this.store.generateKey()
            } catch (e) {
                console.error('API error:', e)
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

