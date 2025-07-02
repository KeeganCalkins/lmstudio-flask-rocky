<script>
import TitleBar from './TitleBar.vue'
import FocusUser from './FocusUser.vue'
import FocusAdmin from './FocusAdmin.vue'
import SideBar from './SideBar.vue'
import {admin} from "../stores/admin.js"
export default {
  components: {
    TitleBar,
    SideBar,
    FocusUser,
    FocusAdmin
  },
  computed: {
    admin() {
      return admin
    }
  }
}
</script>

<template>

    <div style="height:100%">

        <TitleBar></TitleBar>

        <div id="main">

            <component :is="admin.getAdmin() ? 'SideBar' : ''"></component>

            <div id="frame">

                <component :is="admin.getAdmin() ? 'FocusAdmin' : 'FocusUser'"></component>

            </div>

        </div>

    </div>

</template>

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
  width: 600px;
  height: 400px;
  text-align: center;
  align-content: center;
}
</style>

