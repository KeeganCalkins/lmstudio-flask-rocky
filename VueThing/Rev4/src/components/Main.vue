<template>
    <div style="height:100%">
        <TitleBar />

        <div id="main">
            <!-- sidebar only appears when child route is /admin -->
            <SideBar v-if="$route.path.startsWith('/admin')" />

            <div id="frame">
                <router-view />
            </div>
        </div>
    </div>
</template>

<script>
import TitleBar from './TitleBar.vue'
import SideBar  from './SideBar.vue'

export default {
    components: { TitleBar, SideBar }
}
</script>

<style scoped>
#main {
    height: 90%;
    align-content: center;
}
#frame {
    background-color: #003976;
    color: #efab00;
    border: 4px solid #efab00;
    padding: 6px;
    font-size: 18px;
    border-radius: 20px;
    margin: auto;
    width: 60%;
    height: 80%;
    text-align: center;
    align-content: center;
}
</style>