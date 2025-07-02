import {reactive} from "vue"

export const admin = reactive({
    isAdmin: false,
    toggleAdmin() {
        this.isAdmin = !this.isAdmin
    },
    getAdmin() {
        return this.isAdmin 
    }
});