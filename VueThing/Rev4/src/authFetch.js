import { msalInstance } from './msalInstance.js';
import { loginRequest } from './authConfig.js';

export async function authFetch(input, init = {}) {
    const [account] = msalInstance.getAllAccounts()
    
    if (account) {
        const { accessToken } = await msalInstance.acquireTokenSilent({
            ...loginRequest,
            account
        })
        init.headers = {
            ...(init.headers || {}),
            Authorization: `Bearer ${accessToken}`,
        }
    }
    return fetch(input, init)
}