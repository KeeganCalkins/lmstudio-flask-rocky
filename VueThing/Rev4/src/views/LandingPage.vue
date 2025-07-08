<template>
    <TitleBar />
    <div style="max-width: 400px; margin: 2rem auto; color: #fff">
        <h2>Register New User</h2>
        <form @submit.prevent="submitForm">
            <div style="margin-bottom: 1rem;">
                <label>Email:</label><br>
                <input v-model="form.email" type="email" required style="width: 100%;"/>
            </div>
            <div style="margin-bottom: 1rem;">
                <label>First Name:</label><br>
                <input v-model="form.firstName" required style="width: 100%;"/>
            </div>
            <div style="margin-bottom: 1rem;">
                <label>Last Name:</label><br>
                <input v-model="form.lastName" required style="width: 100%;"/>
            </div>
            <div style="margin-bottom: 1rem;">
                <label>CRN:</label><br>
                <input v-model="form.CRN" required style="width: 100%;"/>
            </div>
            <div style="margin-bottom: 1rem;">
                <label>Course ID:</label><br>
                <input v-model="form.courseID" required style="width: 100%;"/>
            </div>
            <div style="margin-bottom: 1rem;">
                <label>Term:</label><br>
                <input v-model="form.term" required style="width: 100%;"/>
            </div>
            <div style="margin-bottom: 1rem;">
                <label>
                    <input type="checkbox" v-model="form.isAdmin" />
                    Admin?
                </label>
            </div>
            <button type="submit" style="background: #003976; color: #efab00; padding: 0.5rem 1rem; border: none; border-radius: 4px;">
                Register
            </button>
        </form>
        <p v-if="success" style="margin-top: 1rem; color: green;">
            User registered! ID: {{ newUserId }}
        </p>
        <p v-if="error" style="margin-top: 1rem; color: red;">
            Error: {{ error }}
        </p>
    </div>
</template>

<script>
import TitleBar from '@/components/TitleBar.vue'

export default {
    components: { TitleBar },
    data() {
        return {
            form: {
                email:    '',
                firstName:'',
                lastName: '',
                CRN:      '',
                courseID: '',
                term:     '',
                isAdmin:  false
            },
            success:   false,
            newUserId: null,
            error:     null
        };
    },
    methods: {
        async submitForm() {
            this.success = this.error = false;
            try {
                const payload = {
                    email:    this.form.email,
                    firstName:this.form.firstName,
                    lastName: this.form.lastName,
                    courseInfo: [{
                        CRN:      this.form.CRN,
                        courseID: this.form.courseID,
                        term:     this.form.term
                    }],
                    isAdmin:  this.form.isAdmin,
                    hasAccess:false
                };
                const res = await fetch('/api/users', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (!res.ok) {
                    const body = await res.json();
                    throw new Error(body.error || res.statusText);
                }
                const data = await res.json();
                this.newUserId = data._id;
                this.success   = true;

                // test storing for example
                localStorage.setItem('currentUserId', data._id);
            } catch (err) {
                console.error(err);
                this.error = err.message;
            }
        }
    }
};
</script>

<style scoped>
input {
    padding: 0.4rem;
    border: 1px solid #ccc;
    border-radius: 4px;
}
label {
    font-weight: bold;
}
</style>
