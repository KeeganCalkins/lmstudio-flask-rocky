import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'
import { msalInstance } from './msalInstance.js'
import { pinia } from './pinia'

async function bootstrap() {
    await msalInstance.initialize();
    await msalInstance.handleRedirectPromise();

    const [account] = msalInstance.getAllAccounts();
    if (account) {
        const idTokenClaims = account.idTokenClaims
        const email = idTokenClaims.preferred_username
                    || idTokenClaims.upn
                    || idTokenClaims.email
        const { accessToken } = await msalInstance.acquireTokenSilent({
            account,
            scopes: [import.meta.env.VITE_API_SCOPE]
        });
        
        await fetch("/api/users", {
            method: "POST",
            headers: {
                "Content-Type":  "application/json",
                "Authorization": `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                email,
                firstName:  account.name.split(" ")[0] || "*",
                lastName:   account.name.split(" ").slice(1).join(" ") || "*",
                courseInfo: [],
            })
        });

        createApp(App).use(router).mount("#app");
        return;
    }
    const app = createApp(App);
    app.use(router);
    app.use(pinia);
    app.mount('#app');
}

bootstrap()