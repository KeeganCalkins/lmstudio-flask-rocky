<template>
    <TitleBar />
    <div class="welcome-shell">
        <AdminListShell :title="''" :page="1" :pages="1">
            <template #toolbar></template>

            <div class="welcome-body">
                <div v-if="loading">Loading…</div>

                <template v-else>
                    <h2 class="greeting">
                        {{ isAuthenticated ? `Hi, ${displayName}` : 'Welcome!' }}
                    </h2>

                    <p v-if="isAuthenticated" class="email-line">
                        You’re signed in under <strong>{{ email }}</strong>.
                    </p>
                    <p v-else class="hint">Please log in to continue.</p>

                    <LoginButton />
                </template>
            </div>
        </AdminListShell>
    </div>
</template>

<script>
    import TitleBar        from '@/components/TitleBar.vue';
    import AdminListShell  from '@/components/AdminListShell.vue';
    import LoginButton     from '@/components/LoginButton.vue';
    import { msalInstance } from '@/msalInstance.js';
    import { authFetch }    from '@/authFetch.js';

export default {
    name: 'WelcomePage',
    components: { TitleBar, AdminListShell, LoginButton },

    data() {
        return {
            user: null,
            loading: true
        };
    },

    computed: {
        accounts() {
            return msalInstance.getAllAccounts();
        },
        isAuthenticated() {
            return this.accounts.length > 0;
        },
        displayName() {
            if (this.user?.firstName) {
                return `${this.user.firstName} ${this.user.lastName}`;
            }
            return this.accounts[0]?.name || '';
        },
        email() {
            return this.user?.email || this.accounts[0]?.username || '';
        },
        headerText() {
            return this.isAuthenticated ? `Hi, ${this.displayName || 'there'}` : 'Welcome!';
        }
    },

    async mounted() {
        if (!this.isAuthenticated) {
            this.loading = false;
            return;
        }
        try {
            const res = await authFetch('/api/me');
            if (res.ok) this.user = await res.json();
        } catch (e) {
            console.error('fetch /api/me failed:', e);
        } finally {
            this.loading = false;
        }
    }
};
</script>

<style scoped>
    .welcome-shell {
        max-width: 620px;
        width: 100%;
        margin: 40px auto;
    }

    .welcome-shell :deep(.man-list) {
        max-height: none;
        padding: 20px;
        text-align: center;
    }

    .welcome-body {
        color: #fff;
    }

    .greeting {
        margin: 0 0 12px;
        font-size: 22px;
        font-weight: 600;
    }

    .email-line {
        margin-bottom: 16px;
    }

    .hint {
        font-size: 12px;
        color: #ccc;
        margin-bottom: 12px;
    }
</style>