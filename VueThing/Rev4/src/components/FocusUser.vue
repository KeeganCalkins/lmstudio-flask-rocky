<template>
  <div id="focusUser">

      <h2 v-if="!isKey">Request Key</h2>
      <button id="request" v-if="!isKey" @click="requestKey">
          <b>Click Here!</b>
      </button>

      <h3 v-if="isKey">Key:</h3>
      <input v-if="isKey" placeholder="8675309" v-model="key"><p></p>
      <button id="request" v-if="isKey" @click="requestKey">
          <b>Another?</b>
      </button>

  </div>
</template>

<script>
export default {
  data() {
    return {
      isKey: false,
      key: "8675309",
    }
  },
  methods: {
    requestKey() {
      //keygen and communication go here
      if (this.isKey) {
        this.key += "new"
      }
      this.isKey = true
    }
  }
}
</script>

<style scoped>
#request {
  height: 40px;
  width: 100px;
  color: #efab00;
  background: #003976;
  border-color: #efab00;
  border-width: 4px;
  border-radius: 20px;
}
</style>

