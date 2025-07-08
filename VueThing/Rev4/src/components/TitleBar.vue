<script>
import {admin} from "../stores/admin.js"
export default {
    computed: {
        admin() {
            return admin
        }
    }
}
</script>

<template>
    <header id="bar">
        <h1 id="title">ROCKY - KSU
            <router-link to="/admin" style="text-decoration: none;">
                <button id="menuButton"><b>Admin</b></button>
            </router-link>
            <router-link to="/user" custom v-slot="{ navigate }">
                <button id="menuButton" @click="navigate"><b>User</b></button>
            </router-link>
            <router-link to="/" custom v-slot="{ navigate }">
                <button id="menuButton" @click="navigate"><b>Log-In</b></button>
            </router-link>
        </h1>
    </header>
</template>

<style scoped>
#bar {
    background: #003976;
    color: #efab00;
    border-color: #efab00;
    border-width: 10px;
}

#title {
    margin: 0px;
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
    position: inherit
}
</style>

