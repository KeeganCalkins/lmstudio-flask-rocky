<template>
    <div id="container">
        <div id="context">
            <h3>User Management</h3>
        </div>

        <div id="list">
            <div v-if="users.length === 0">No users found.</div>
            <div v-for="user in users" :key="user._id" class="user-entry">
                <span class="user-line">
                    {{ user.firstName }} {{ user.lastName }} — CRN: {{ user.CRN }}, Course: {{ user.courseID }} ({{ user.term }}) — Access: 
                    <strong>{{ user.hasAccess ? "Yes" : "No" }}</strong>
                    <br>
                    <small>{{ user.email }}</small>
                    
                </span>
                <button @click="removeUser(user._id)">DELETE USER</button>
            </div>
        </div>
    </div>
</template>
<script>
    export default {
        data() {
            return {
            users: [],
            };
        },
        mounted() {
            this.fetchUsers();
        },
        methods: {
            fetchUsers() {
                fetch('/api/users')
                    .then(res => res.json())
                    .then(data => {
                        this.users = data;
                    })
                    .catch(err => {
                        console.error("Failed to fetch users:", err);
                    });
            },
            removeUser(userId) {
                if (!confirm("Are you sure you want to remove this user?")) return;

                fetch(`/api/users/${userId}`, {
                    method: "DELETE",
                })
                    .then(res => res.json())
                    .then(() => {
                        // Refresh the user list 
                        this.fetchUsers();
                    })
                    .catch(err => {
                        console.error("Failed to remove user:", err);
                        alert("Could not remove user.");
                    });
            },
        },
    };
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

    .user-entry {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        padding: 4px 0;
        border-bottom: 1px solid #444;
    }

    .user-line {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 80%;
    }

    #list {
        overflow-y: auto;
        max-height: 250px;           /* prevent it from overflowing down */
        width: 100%;                 /* use all available width */
        background: #002f61;
        margin: 10px auto 0 auto;    /* centered with top spacing */
        padding: 10px;
        border-radius: 5px;
        color: white;
        font-family: sans-serif;
        box-sizing: border-box;
    }
</style>