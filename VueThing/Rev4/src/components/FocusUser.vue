<template>
    <div id="focusUser">
        <h2 v-if="!hasAccess">Request Access</h2>
        <button id="request" v-if="!hasAccess" @click="requestAPIAccess">
            <b>Request Access</b>
        </button>

        <h2 v-if="hasAccess && !isKey">No API Key Found</h2>
        <button id="request" v-if="hasAccess && !isKey" @click="generateNewKey">
            <b>Generate Key</b>
        </button>

        <h3 v-if="isKey">Key:</h3>
        <input v-if="isKey" :value="key" readonly>
        <p></p>
        <button id="request" v-if="isKey" @click="generateNewKey">
            <b>Another?</b>
        </button>

    </div>
</template>

<script>
export default {
    data() {
        return {
            isKey: false,
            key: null,
            hasAccess: false,
            userId: 'PASTE TEST USER ID',
        }
    },
    mounted() {
        this.fetchUserAccessStatus();
    },
    methods: {
        fetchUserAccessStatus() {
        fetch(`/api/users/${this.userId}`)
            .then(res => res.json())
            .then(data => {
            this.hasAccess = data.hasAccess;
                if (this.hasAccess) {
                    this.fetchExistingKey();
                }
            })
            .catch(err => console.error("Failed to get user:", err));
        },
        requestAPIAccess() {
            fetch(`/api/users/${this.userId}/access`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(res => {
                if (!res.ok) throw new Error("Access request failed");
                return res.json();
            })
            .catch(err => {
                console.error("API error:", err);
                alert("Could not request access, you probably already have");
            });
        },
        fetchExistingKey() {
            fetch(`/api/users/${this.userId}/apikey`)
            .then(res => res.json())
            .then(data => {
                if (data.api_key) {
                    this.key = data.api_key;
                    this.isKey = true;
                }
            })
            .catch(err => console.error("Failed to fetch API key:", err));
        },
        generateNewKey() {
            fetch(`/api/users/${this.userId}/apikey`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(res => {
                if (!res.ok) throw new Error("Key request failed");
                return res.json();
            })
            .then(data => {
                this.key = data.api_key;
                this.isKey = true;
            })
            .catch(err => {
                console.error("API error:", err);
                alert("Could not generate key");
            });
        },
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

