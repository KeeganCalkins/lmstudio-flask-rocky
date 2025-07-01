<script>
import ManUser from "./ManUser.vue"
import ManKey from "./ManKey.vue"
  export default {
    components: {
      ManUser,
      ManKey
    },
    data() {
      return {
        activeComp: "ManUser",
      }
    },
      methods: {

    }
}
</script>

<template>
   <div id="focusAdmin"> 
    <component :is="activeComp"></component>
  </div>
</template>

<style scoped>
#list {
  overflow: scroll;
  height: 350px;
  width: 225px;
  background: #002f61;
  float: right;
  margin: 20px;
  padding:5px;
  border-radius: 5px;
}

#context {
  height:350px;
  width:250px;
  float: left;
  border-width: 5px;
  border-color:black;
  margin: 20px;
  padding:5px;
}
</style>

