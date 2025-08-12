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
        
        const oidcRequest = {
            account,
            scopes: ["openid", "profile"]
        };
        const response = await msalInstance.acquireTokenSilent(oidcRequest);
        const idToken = response.idToken;

        let firstName = claims.given_name || "";
        let lastName  = claims.family_name || "";

        if (!firstName || !lastName) {
            const raw = (account.name || claims.name || "").replace(/\s+/g, " ").trim();
            if (raw.includes(",")) {
                const [last, rest] = raw.split(",", 2).map(s => s.trim());
                if (!firstName) firstName = (rest || "").split(" ")[0] || "";
                if (!lastName)  lastName  = last || "";
            } else if (raw) {
                const parts = raw.split(" ");
                if (!firstName) firstName = parts[0] || "";
                if (!lastName)  lastName  = parts.slice(1).join(" ");
            }
        }

        firstName = firstName || "*";
        lastName  = lastName  || "*";
        
        await fetch("/api/users", {
            method: "POST",
            headers: {
                "Content-Type":  "application/json",
                "Authorization": `Bearer ${idToken}`
            },
            body: JSON.stringify({
                email,
                firstName,
                lastName,
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