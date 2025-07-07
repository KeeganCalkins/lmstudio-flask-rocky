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
      <button id="menuButton" @click="admin.toggleAdmin()"><b>=</b></button>
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
  width: 40px;
  border-radius: 10px;
  color: #efab00;
  background: #003976;
  border-color: #efab00;
  float: right;
  position: inherit
}
</style>

