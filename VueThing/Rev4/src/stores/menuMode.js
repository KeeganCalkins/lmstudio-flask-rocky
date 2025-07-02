import {reactive} from "vue"

export const menuMode = reactive({
    mode: "ManUser",
    setMode(value) {
        this.mode = value
    },
    getMode() {
        return this.mode 
    }
});