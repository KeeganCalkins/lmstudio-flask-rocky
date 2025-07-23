export const msalConfig = {
    auth: {
        clientId: import.meta.env.VITE_AZURE_CLIENT_ID,
        authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_TENANT_ID}`,
        redirectUri: window.location.origin,
    },
    cache: {
        cacheLocation: "localStorage",
        storeAuthStateInCookie: false,
    }
};

export const loginRequest = {
    scopes: [
        "openid",
        "profile",
        import.meta.env.VITE_API_SCOPE
    ]
};
