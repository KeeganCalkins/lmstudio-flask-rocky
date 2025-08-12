import { msalInstance } from './msalInstance.js';
import { loginRequest } from './authConfig.js';

export async function authFetch(input, init = {}) {
    const [account] = msalInstance.getAllAccounts()
    
    if (!account) {
        return Promise.reject(new Error('Not authenticated'));
    }
    let response;
    try {
        response = await msalInstance.acquireTokenSilent({
        ...loginRequest,
        account
        });
    } catch (e) {
        return Promise.reject(e);
    }

    const token = response.idToken;
    if (!token) {
        throw new Error("No ID token returned");
    }

    init.headers = {
        ...(init.headers || {}),
        Authorization: `Bearer ${token}`
    };
    return fetch(input, init)
}