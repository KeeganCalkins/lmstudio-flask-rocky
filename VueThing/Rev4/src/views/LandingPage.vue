<template>
    <TitleBar />
    <div id="container">
        <div id="context">
            Welcome! Please log in to continue.
        </div>
        <div id="list">
            <LoginButton />
        </div>
    </div>
</template>

<script>
import TitleBar   from '@/components/TitleBar.vue'
import LoginButton from '@/components/LoginButton.vue'

export default {
    components: { TitleBar, LoginButton }
}
</script>

<style scoped>
#container {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
}

#context {
    margin: 20px;
    padding: 5px;
    font-size: 16px;
    font-weight: bold;
    color: white;
}

#list {
    overflow-y: auto;
    max-height: 250px;
    width: 100%;
    background: #002f61;
    margin: 10px auto 0 auto;
    padding: 10px;
    border-radius: 5px;
    color: white;
    font-family: sans-serif;
    box-sizing: border-box;
}
</style>