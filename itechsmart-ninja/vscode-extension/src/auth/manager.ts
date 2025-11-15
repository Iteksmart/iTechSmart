/**
 * Authentication Manager
 * Handles user authentication and token management
 */
import * as vscode from 'vscode';

export class AuthManager {
    private context: vscode.ExtensionContext;
    private static readonly ACCESS_TOKEN_KEY = 'itechsmart.accessToken';
    private static readonly REFRESH_TOKEN_KEY = 'itechsmart.refreshToken';
    private static readonly USER_KEY = 'itechsmart.user';

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    async login(): Promise<boolean> {
        const email = await vscode.window.showInputBox({
            prompt: 'Enter your email',
            placeHolder: 'user@example.com',
            validateInput: (value) => {
                if (!value || !value.includes('@')) {
                    return 'Please enter a valid email address';
                }
                return null;
            }
        });

        if (!email) {
            return false;
        }

        const password = await vscode.window.showInputBox({
            prompt: 'Enter your password',
            password: true,
            validateInput: (value) => {
                if (!value || value.length < 8) {
                    return 'Password must be at least 8 characters';
                }
                return null;
            }
        });

        if (!password) {
            return false;
        }

        try {
            // Import ApiClient here to avoid circular dependency
            const axios = require('axios');
            const config = vscode.workspace.getConfiguration('itechsmart');
            const apiUrl = config.get<string>('apiUrl') || 'http://localhost:8000';

            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const response = await axios.post(
                `${apiUrl}/api/v1/auth/login`,
                formData,
                {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
            );

            const { access_token, refresh_token, user } = response.data;

            // Store tokens securely
            await this.context.secrets.store(AuthManager.ACCESS_TOKEN_KEY, access_token);
            await this.context.secrets.store(AuthManager.REFRESH_TOKEN_KEY, refresh_token);
            await this.context.globalState.update(AuthManager.USER_KEY, user);

            vscode.window.showInformationMessage(`Welcome back, ${user.full_name}!`);
            return true;

        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
            vscode.window.showErrorMessage(`Login failed: ${errorMessage}`);
            return false;
        }
    }

    async register(): Promise<boolean> {
        const email = await vscode.window.showInputBox({
            prompt: 'Enter your email',
            placeHolder: 'user@example.com',
            validateInput: (value) => {
                if (!value || !value.includes('@')) {
                    return 'Please enter a valid email address';
                }
                return null;
            }
        });

        if (!email) {
            return false;
        }

        const fullName = await vscode.window.showInputBox({
            prompt: 'Enter your full name',
            placeHolder: 'John Doe'
        });

        if (!fullName) {
            return false;
        }

        const password = await vscode.window.showInputBox({
            prompt: 'Enter your password (min 8 characters)',
            password: true,
            validateInput: (value) => {
                if (!value || value.length < 8) {
                    return 'Password must be at least 8 characters';
                }
                return null;
            }
        });

        if (!password) {
            return false;
        }

        const confirmPassword = await vscode.window.showInputBox({
            prompt: 'Confirm your password',
            password: true,
            validateInput: (value) => {
                if (value !== password) {
                    return 'Passwords do not match';
                }
                return null;
            }
        });

        if (!confirmPassword) {
            return false;
        }

        try {
            const axios = require('axios');
            const config = vscode.workspace.getConfiguration('itechsmart');
            const apiUrl = config.get<string>('apiUrl') || 'http://localhost:8000';

            const response = await axios.post(
                `${apiUrl}/api/v1/auth/register`,
                {
                    email,
                    password,
                    full_name: fullName
                }
            );

            const { access_token, refresh_token, user } = response.data;

            // Store tokens securely
            await this.context.secrets.store(AuthManager.ACCESS_TOKEN_KEY, access_token);
            await this.context.secrets.store(AuthManager.REFRESH_TOKEN_KEY, refresh_token);
            await this.context.globalState.update(AuthManager.USER_KEY, user);

            vscode.window.showInformationMessage(`Welcome, ${user.full_name}! Your account has been created.`);
            return true;

        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Registration failed';
            vscode.window.showErrorMessage(`Registration failed: ${errorMessage}`);
            return false;
        }
    }

    async logout(): Promise<void> {
        await this.context.secrets.delete(AuthManager.ACCESS_TOKEN_KEY);
        await this.context.secrets.delete(AuthManager.REFRESH_TOKEN_KEY);
        await this.context.globalState.update(AuthManager.USER_KEY, undefined);

        vscode.window.showInformationMessage('Logged out successfully');
    }

    async refreshToken(): Promise<void> {
        const refreshToken = await this.context.secrets.get(AuthManager.REFRESH_TOKEN_KEY);

        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        try {
            const axios = require('axios');
            const config = vscode.workspace.getConfiguration('itechsmart');
            const apiUrl = config.get<string>('apiUrl') || 'http://localhost:8000';

            const response = await axios.post(
                `${apiUrl}/api/v1/auth/refresh`,
                { refresh_token: refreshToken }
            );

            const { access_token, refresh_token: newRefreshToken } = response.data;

            await this.context.secrets.store(AuthManager.ACCESS_TOKEN_KEY, access_token);
            await this.context.secrets.store(AuthManager.REFRESH_TOKEN_KEY, newRefreshToken);

        } catch (error) {
            // If refresh fails, logout
            await this.logout();
            throw error;
        }
    }

    async getAccessToken(): Promise<string | undefined> {
        return await this.context.secrets.get(AuthManager.ACCESS_TOKEN_KEY);
    }

    async getRefreshToken(): Promise<string | undefined> {
        return await this.context.secrets.get(AuthManager.REFRESH_TOKEN_KEY);
    }

    getUser(): any {
        return this.context.globalState.get(AuthManager.USER_KEY);
    }

    isAuthenticated(): boolean {
        const user = this.getUser();
        return user !== undefined;
    }

    async showLoginOrRegister(): Promise<void> {
        const choice = await vscode.window.showQuickPick([
            { label: 'Login', value: 'login' },
            { label: 'Register', value: 'register' }
        ], {
            placeHolder: 'Choose an option'
        });

        if (choice?.value === 'login') {
            await this.login();
        } else if (choice?.value === 'register') {
            await this.register();
        }
    }
}