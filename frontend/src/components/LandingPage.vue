<template>
  <div class="landing-page">
    <h1>Welcome to Rocky!</h1>
    <p>KSU's hometown AI API.</p>
    <button @click="goToApp">Request a key</button>
  </div>
</template>

<script>
export default {
  name: 'LandingPage',
  methods: {
    goToApp() {
      this.$router.push('/login');
    }
  }
}
</script>

<style scoped>
.landing-page {
  text-align: center;
  margin-top: 100px;
}
button {
  padding: 10px 20px;
  font-size: 18px;
  margin-top: 20px;
}
</style>
