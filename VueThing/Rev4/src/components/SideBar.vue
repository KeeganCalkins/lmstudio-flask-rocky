<template>
    <div id="bar">
        <h3 style="margin-left: 1rem; color: goldenrod">Manage</h3>
        <button id="menuButton" @click="menuMode.setMode('ManUser')">
            User
        </button>
        <button id="menuButton" @click="menuMode.setMode('ManKey')">
            Key
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
    width: 100px;
    background: #003976;
    border-top-right-radius: 20px;
    border-bottom-right-radius: 20px;
    border: 2px solid #efab00;
}

#menuButton {
    height: 40px;
    width: 40px;
    border-radius: 10px;
    color: #efab00;
    background: #003976;
    border-color: #efab00;
    margin: 30px;
    position: inherit
}
</style>
