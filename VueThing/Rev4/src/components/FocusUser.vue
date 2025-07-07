<template>
    <div id="focusUser">
        <template v-if="!hasAccess">
            <h2 v-if="!isPending">Request Access</h2>
            <button id="request" v-if="!isPending" @click="requestAPIAccess">
                <b>Request Access</b>
            </button>
            <h2 v-else>Waiting for access…</h2>
        </template>

        <template v-else-if="hasAccess && !isKey">
            <h2>No API Key Found</h2>
            <button id="request" @click="generateNewKey">
                <b>Generate Key</b>
            </button>
        </template>

        <template v-else>
            <h3>Key:</h3>
            <input :value="key" readonly>
            <p></p>
            <button id="request" @click="generateNewKey">
                <b>Another?</b>
            </button>
        </template>

    </div>
</template>

<script>
export default {
    data() {
        return {
            isKey: false,
            key: null,
            hasAccess: false,
            isPending: false,
            userId: '686b65e07c314d3ef59113fc',
        }
    },
    async mounted() {
        await this.fetchUserAccessStatus();
    },
    methods: {
        async fetchUserAccessStatus() {
            try {
                const resUser = await fetch(`/api/users/${this.userId}`);
                const dataUser = await resUser.json();
                this.hasAccess = dataUser.hasAccess;

                const resPending = await fetch(`/api/users/${this.userId}/access/pending`);
                const dataPending = await resPending.json();
                this.isPending = dataPending.pending;

                if (this.hasAccess) {
                    await this.fetchExistingKey();
               }
            } catch (err) {
                console.error("Error fetching user status:", err);
            }
        },
        async requestAPIAccess() {
            try {
                const res = await fetch(`/api/users/${this.userId}/access`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" }
                });
                if (!res.ok) throw new Error("Access request failed");
                this.isPending = true;
            } catch (err) {
                console.error("API error:", err);
                alert("Could not request access, issue with account log-in");
            }
        },
        async fetchExistingKey() {
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

