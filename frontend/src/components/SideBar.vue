<template>
    <div id="bar">
        <h3 style="margin-left: 1.5rem; color: goldenrod">Manage</h3>
        <button id="menuButton" @click="menuMode.setMode('ManUser')">
            Users
        </button>
        <button id="menuButton" @click="menuMode.setMode('ManKey')">
            Keys
        </button>
        <button id="menuButton" @click="menuMode.setMode('ManRequests')">
            Requests
        </button>
    </div>
</template>

<script>
import {menuMode} from "../stores/menuMode.js"
  export default {
    computed: {
        menuMode() {
            return menuMode
        }
    },
}
</script>

<style scoped>
#bar {
    float: left;
    height: 400px;
    width: 110px;
    background: #003976;
    border-top-right-radius: 20px;
    border-bottom-right-radius: 20px;
    border: 2px solid #efab00;
}

#menuButton {
    height: 50px;
    width: 70px;
    border-radius: 10px;
    color: #efab00;
    background: #003976;
    border-color: #efab00;
    margin: 20px;
    position: inherit
}
</style>
