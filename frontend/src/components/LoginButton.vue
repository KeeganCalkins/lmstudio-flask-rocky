<script setup>
    import { computed } from 'vue';
    import { msalInstance }    from '@/msalInstance.js'
    import { loginRequest }    from '@/authConfig.js'

    const accounts        = computed(() => msalInstance.getAllAccounts())
    const isAuthenticated = computed(() => accounts.value.length > 0)

    function login() {
        sessionStorage.removeItem('msal.interaction.status')
        msalInstance.loginRedirect(loginRequest)
            .catch(err => console.error('loginRedirect failed:', err))
    }
    function logout() { 
        msalInstance.logoutRedirect()
    }
</script>

<template>
    <button v-if="!isAuthenticated" @click="login">Log-In</button>
    <button v-else @click="logout">Log-Out</button>
</template>