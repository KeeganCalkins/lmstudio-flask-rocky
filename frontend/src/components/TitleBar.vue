<template>
    <header id="bar">
        <h1 id="title">ROCKY - KSU
            <router-link 
                to="/" 
                custom v-slot="{ navigate }"
            >
                <button id="menuButton" @click="navigate"><b>Home</b></button>
            </router-link>
            <router-link
                v-if="isLoggedIn"
                to="/user"
                custom v-slot="{ navigate }"
            >
                <button id="menuButton" @click="navigate"><b>User</b></button>
            </router-link>
            <router-link
                v-if="isAdmin"
                to="/admin"
                custom v-slot="{ navigate }"
            >
                <button id="menuButton" @click="navigate"><b>Admin</b></button>
            </router-link>
        </h1>
    </header>
</template>

<script>
import { useUserStore } from '@/stores/userStores.js'

export default {
    data() {
        return {
            store: null
        }
    },
    async mounted() {
        if (this.store.isAuthed) {
            await this.store.refreshMe()
        }
   },
    created() {
        this.store = useUserStore()
    },
    computed: {
        isLoggedIn() {
            return this.store.isAuthed
        },
        isAdmin() {
            return this.store.isAdmin
        }
    }
}
</script>

<style scoped>
#bar {
    background: #003976;
    color: #efab00;
    border-color: #efab00;
    border-width: 10px;
}
#title {
    margin: 0;
    padding: 10px;
}
#menuButton {
    height: 40px;
    width: 80px;
    border-radius: 10px;
    color: #efab00;
    background: #003976;
    border-color: #efab00;
    float: right;
    position: inherit;
    margin-left: 8px;
}
</style>

