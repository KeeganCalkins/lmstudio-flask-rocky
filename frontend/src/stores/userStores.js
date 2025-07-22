import { defineStore } from 'pinia'
import { authFetch }   from '@/authFetch.js'

export const useUserStore = defineStore('user', {
    state: () => ({
        loaded: false,          // was /api/me called
        _id: null,
        email: null,
        hasAccess: false,
        isAdmin: false,
        courseInfo: [],
        apiKey: null,           // cached key for display
        pending: false
    }),

    getters: {
        isAuthed: (s) => !!s._id,
        hasKey:   (s) => !!s.apiKey
    },

    actions: {
        setMe(me) {
            this._id        = me._id
            this.email      = me.email
            this.hasAccess  = me.hasAccess
            this.isAdmin    = me.isAdmin
            this.courseInfo = me.courseInfo || []
        },
        setLoaded(flag) {
            this.loaded = !!flag
        },
        setPending(flag) {
            this.pending = !!flag
        },
        setKey(k) {
            this.apiKey = k || null
        },
        async init() {
            if (this.loaded) return
            await this.refreshMe()
            if (this._id) {
                await Promise.all([
                    this.refreshPending(),
                    this.refreshKey()
                ])
            }
            this.loaded = true
        },

        async refreshMe() {
            const res = await authFetch('/api/me')
            if (!res.ok) {
                this.$reset()
                return
            }
            const me = await res.json()
            this._id        = me._id
            this.email      = me.email
            this.hasAccess  = me.hasAccess
            this.isAdmin    = me.isAdmin
            this.courseInfo = me.courseInfo || []
        },

        async refreshPending() {
            if (!this._id) return
            const res = await authFetch(`/api/users/${this._id}/access/pending`)
            if (res.ok) {
                const data = await res.json()
                this.pending = !!data.pending
            }
        },

        async refreshKey() {
            if (!this._id) return
            const res = await authFetch(`/api/users/${this._id}/apikey`)
            if (res.ok) {
                const data = await res.json()
                this.apiKey = data.api_key || null
            }
        },

        async requestAccess(courses = []) {
            if (!Array.isArray(courses) || courses.length === 0) {
                throw new Error('Please add at least one course.')
            }
            const clean = courses.map(c => ({
                CRN:      (c.CRN || '').trim(),
                courseID: (c.courseID || '').trim(),
                term:     (c.term || '').trim()
            }));
            if (clean.some(c => !c.CRN || !c.courseID || !c.term)) {           
                throw new Error('Fill all fields: CRN, Course ID, and Term.')
            }

            const res = await authFetch(`/api/users/${this._id}/access`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ courses })
            })
            if (!res.ok) {
                const err = await res.json().catch(() => ({}))
                throw new Error(err.error || 'Access request failed')
            }
            this.pending = true
        },

        async generateKey(forUserId = null) {
            const target = forUserId || this._id
            const res = await authFetch(`/api/users/${target}/apikey`, {
                method: 'POST'
            })
            if (!res.ok) {
                const err = await res.json().catch(() => ({}))
                throw new Error(err.error || 'Key generation failed')
            }
            const data = await res.json()
            if (target === this._id) {
                this.apiKey = data.api_key
            }
            return data.api_key
        },

        resetKeyCache() {
            this.apiKey = null
        },

        $reset() {
            this.loaded    = false
            this._id       = null
            this.email     = null
            this.hasAccess = false
            this.isAdmin   = false
            this.courseInfo = []
            this.apiKey    = null
            this.pending   = false
        }
    }
})