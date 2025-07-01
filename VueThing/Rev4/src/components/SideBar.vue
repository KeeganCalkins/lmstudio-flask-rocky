<template>
    <div id="bar">
        <button id="menuButton">
            User
        </button>
        <button id="menuButton">
            Key
        </button>
        <button id="menuButton">
            Set
        </button>
        <button id="menuButton">
            Quit
        </button>
    </div>
</template>

<script>
  export default {
    data() {
      return {

      }
    },
  methods: {

  }
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
