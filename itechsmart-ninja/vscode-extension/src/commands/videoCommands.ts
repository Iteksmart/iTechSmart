/**
 * Video Generation Commands
 * AI-powered video generation and editing
 */

import * as vscode from 'vscode';
import axios from 'axios';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

interface VideoGeneration {
    id: number;
    prompt: string;
    provider: string;
    duration?: number;
    resolution?: string;
    video_url: string;
    status: string;
    created_at: string;
}

interface VideoProvider {
    id: string;
    name: string;
    capabilities: string[];
    max_duration: number;
    resolutions: string[];
}

/**
 * Generate video from text
 */
export async function generateVideoFromText() {
    try {
        // Get prompt
        const prompt = await vscode.window.showInputBox({
            prompt: 'Enter video description',
            placeHolder: 'e.g., A serene sunset over the ocean with waves',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Please enter a description';
                }
                return null;
            }
        });

        if (!prompt) return;

        // Get provider
        const providersResponse = await axios.get(`${API_BASE_URL}/api/video/providers`);
        const providers: VideoProvider[] = providersResponse.data.providers;

        const selectedProvider = await vscode.window.showQuickPick(
            providers.map(p => ({
                label: p.name,
                description: `Max ${p.max_duration}s, ${p.resolutions.join(', ')}`,
                value: p.id
            })),
            { placeHolder: 'Select video provider' }
        );

        if (!selectedProvider) return;

        // Get duration
        const duration = await vscode.window.showInputBox({
            prompt: 'Enter video duration in seconds',
            placeHolder: '4',
            value: '4',
            validateInput: (value) => {
                const num = parseInt(value);
                if (isNaN(num) || num < 2 || num > 60) {
                    return 'Duration must be between 2 and 60 seconds';
                }
                return null;
            }
        });

        if (!duration) return;

        // Get resolution
        const resolution = await vscode.window.showQuickPick(
            [
                { label: '720p (HD)', value: '720p' },
                { label: '1080p (Full HD)', value: '1080p' },
                { label: '4K (Ultra HD)', value: '4k' }
            ],
            { placeHolder: 'Select resolution' }
        );

        if (!resolution) return;

        // Get style (optional)
        const style = await vscode.window.showQuickPick(
            [
                { label: 'None', value: null },
                { label: 'Realistic', value: 'realistic' },
                { label: 'Animated', value: 'animated' },
                { label: 'Cinematic', value: 'cinematic' },
                { label: 'Artistic', value: 'artistic' },
                { label: 'Documentary', value: 'documentary' },
                { label: 'Abstract', value: 'abstract' }
            ],
            { placeHolder: 'Select style (optional)' }
        );

        // Generate video
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Generating video...',
            cancellable: false
        }, async (progress) => {
            progress.report({ message: 'This may take 30-60 seconds...' });

            const response = await axios.post(`${API_BASE_URL}/api/video/generate`, {
                prompt,
                provider: selectedProvider.value,
                duration: parseInt(duration),
                resolution: resolution.value,
                style: style?.value,
                motion_strength: 0.5
            });

            if (response.data.success) {
                const video = response.data.video;
                
                vscode.window.showInformationMessage(
                    `✅ Video generated successfully!`,
                    'View Video', 'Copy URL'
                ).then(selection => {
                    if (selection === 'View Video') {
                        vscode.env.openExternal(vscode.Uri.parse(video.video_url));
                    } else if (selection === 'Copy URL') {
                        vscode.env.clipboard.writeText(video.video_url);
                        vscode.window.showInformationMessage('Video URL copied to clipboard');
                    }
                });
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to generate video: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Generate video from image
 */
export async function generateVideoFromImage() {
    try {
        // Select image file
        const imageUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            filters: {
                'Images': ['png', 'jpg', 'jpeg', 'gif', 'webp']
            },
            title: 'Select image file'
        });

        if (!imageUri || imageUri.length === 0) return;

        const imagePath = imageUri[0].fsPath;

        // Get prompt (optional)
        const prompt = await vscode.window.showInputBox({
            prompt: 'Enter motion description (optional)',
            placeHolder: 'e.g., Make the clouds move'
        });

        // Get provider
        const providersResponse = await axios.get(`${API_BASE_URL}/api/video/providers`);
        const providers: VideoProvider[] = providersResponse.data.providers;

        const selectedProvider = await vscode.window.showQuickPick(
            providers.map(p => ({
                label: p.name,
                description: `Max ${p.max_duration}s`,
                value: p.id
            })),
            { placeHolder: 'Select video provider' }
        );

        if (!selectedProvider) return;

        // Generate video
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Generating video from image...',
            cancellable: false
        }, async (progress) => {
            progress.report({ message: 'This may take 30-60 seconds...' });

            const response = await axios.post(`${API_BASE_URL}/api/video/generate-from-image`, {
                image_path: imagePath,
                prompt: prompt || undefined,
                provider: selectedProvider.value,
                duration: 4,
                motion_strength: 0.5
            });

            if (response.data.success) {
                const video = response.data.video;
                
                vscode.window.showInformationMessage(
                    `✅ Video generated from image!`,
                    'View Video', 'Copy URL'
                ).then(selection => {
                    if (selection === 'View Video') {
                        vscode.env.openExternal(vscode.Uri.parse(video.video_url));
                    } else if (selection === 'Copy URL') {
                        vscode.env.clipboard.writeText(video.video_url);
                    }
                });
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to generate video: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Transform video
 */
export async function transformVideo() {
    try {
        // Select video file
        const videoUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            filters: {
                'Videos': ['mp4', 'mov', 'avi', 'mkv']
            },
            title: 'Select video file'
        });

        if (!videoUri || videoUri.length === 0) return;

        const videoPath = videoUri[0].fsPath;

        // Get transformation prompt
        const prompt = await vscode.window.showInputBox({
            prompt: 'Enter transformation description',
            placeHolder: 'e.g., Make it look like a watercolor painting',
            validateInput: (value) => {
                if (!value || value.trim().length === 0) {
                    return 'Please enter a transformation description';
                }
                return null;
            }
        });

        if (!prompt) return;

        // Get provider
        const providersResponse = await axios.get(`${API_BASE_URL}/api/video/providers`);
        const providers: VideoProvider[] = providersResponse.data.providers;

        const selectedProvider = await vscode.window.showQuickPick(
            providers.filter(p => p.capabilities.includes('video-to-video')).map(p => ({
                label: p.name,
                value: p.id
            })),
            { placeHolder: 'Select video provider' }
        );

        if (!selectedProvider) return;

        // Transform video
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Transforming video...',
            cancellable: false
        }, async (progress) => {
            progress.report({ message: 'This may take 1-2 minutes...' });

            const response = await axios.post(`${API_BASE_URL}/api/video/transform`, {
                video_path: videoPath,
                prompt,
                provider: selectedProvider.value,
                strength: 0.7
            });

            if (response.data.success) {
                const video = response.data.video;
                
                vscode.window.showInformationMessage(
                    `✅ Video transformed successfully!`,
                    'View Video', 'Copy URL'
                ).then(selection => {
                    if (selection === 'View Video') {
                        vscode.env.openExternal(vscode.Uri.parse(video.video_url));
                    } else if (selection === 'Copy URL') {
                        vscode.env.clipboard.writeText(video.video_url);
                    }
                });
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to transform video: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Upscale video
 */
export async function upscaleVideo() {
    try {
        // Select video file
        const videoUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            filters: {
                'Videos': ['mp4', 'mov', 'avi', 'mkv']
            },
            title: 'Select video file'
        });

        if (!videoUri || videoUri.length === 0) return;

        const videoPath = videoUri[0].fsPath;

        // Get target resolution
        const resolution = await vscode.window.showQuickPick(
            [
                { label: '720p (HD)', value: '720p' },
                { label: '1080p (Full HD)', value: '1080p' },
                { label: '4K (Ultra HD)', value: '4k' }
            ],
            { placeHolder: 'Select target resolution' }
        );

        if (!resolution) return;

        // Ask about quality enhancement
        const enhance = await vscode.window.showQuickPick(
            [
                { label: 'Yes - Apply quality enhancement', value: true },
                { label: 'No - Simple upscaling', value: false }
            ],
            { placeHolder: 'Apply quality enhancement?' }
        );

        if (!enhance) return;

        // Upscale video
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Upscaling video...',
            cancellable: false
        }, async (progress) => {
            progress.report({ message: 'This may take several minutes...' });

            const response = await axios.post(`${API_BASE_URL}/api/video/upscale`, {
                video_path: videoPath,
                target_resolution: resolution.value,
                enhance_quality: enhance.value
            });

            if (response.data.success) {
                const video = response.data.video;
                
                vscode.window.showInformationMessage(
                    `✅ Video upscaled to ${resolution.label}!`,
                    'Open File'
                ).then(selection => {
                    if (selection === 'Open File') {
                        vscode.env.openExternal(vscode.Uri.file(video.video_path));
                    }
                });
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to upscale video: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * Edit video
 */
export async function editVideo() {
    try {
        // Select video file
        const videoUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            filters: {
                'Videos': ['mp4', 'mov', 'avi', 'mkv']
            },
            title: 'Select video file'
        });

        if (!videoUri || videoUri.length === 0) return;

        const videoPath = videoUri[0].fsPath;

        // Select operation
        const operation = await vscode.window.showQuickPick(
            [
                { label: 'Trim', description: 'Cut video to specific duration', value: 'trim' },
                { label: 'Merge', description: 'Combine multiple videos', value: 'merge' },
                { label: 'Speed', description: 'Change playback speed', value: 'effect' },
                { label: 'Reverse', description: 'Play video backwards', value: 'effect' },
                { label: 'Fade', description: 'Add fade in/out', value: 'effect' }
            ],
            { placeHolder: 'Select edit operation' }
        );

        if (!operation) return;

        let parameters: any = {};

        if (operation.value === 'trim') {
            const startTime = await vscode.window.showInputBox({
                prompt: 'Enter start time in seconds',
                placeHolder: '0',
                value: '0'
            });
            const endTime = await vscode.window.showInputBox({
                prompt: 'Enter end time in seconds',
                placeHolder: '10'
            });
            
            if (!startTime || !endTime) return;
            
            parameters = {
                start_time: parseFloat(startTime),
                end_time: parseFloat(endTime)
            };
        } else if (operation.value === 'merge') {
            const additionalVideos = await vscode.window.showOpenDialog({
                canSelectFiles: true,
                canSelectFolders: false,
                canSelectMany: true,
                filters: {
                    'Videos': ['mp4', 'mov', 'avi', 'mkv']
                },
                title: 'Select videos to merge'
            });
            
            if (!additionalVideos || additionalVideos.length === 0) return;
            
            parameters = {
                additional_videos: additionalVideos.map(uri => uri.fsPath)
            };
        } else if (operation.label === 'Speed') {
            const factor = await vscode.window.showInputBox({
                prompt: 'Enter speed factor (0.5 = half speed, 2.0 = double speed)',
                placeHolder: '1.0',
                value: '1.0'
            });
            
            if (!factor) return;
            
            parameters = {
                effect: 'speed',
                factor: parseFloat(factor)
            };
        } else if (operation.label === 'Reverse') {
            parameters = {
                effect: 'reverse'
            };
        } else if (operation.label === 'Fade') {
            const duration = await vscode.window.showInputBox({
                prompt: 'Enter fade duration in seconds',
                placeHolder: '1.0',
                value: '1.0'
            });
            
            if (!duration) return;
            
            parameters = {
                effect: 'fade',
                duration: parseFloat(duration)
            };
        }

        // Edit video
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Editing video (${operation.label})...`,
            cancellable: false
        }, async () => {
            const response = await axios.post(`${API_BASE_URL}/api/video/edit`, {
                video_path: videoPath,
                operation: operation.value,
                parameters
            });

            if (response.data.success) {
                const video = response.data.video;
                
                vscode.window.showInformationMessage(
                    `✅ Video edited successfully!`,
                    'Open File'
                ).then(selection => {
                    if (selection === 'Open File') {
                        vscode.env.openExternal(vscode.Uri.file(video.video_path));
                    }
                });
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to edit video: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * List video providers
 */
export async function listVideoProviders() {
    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Loading video providers...',
            cancellable: false
        }, async () => {
            const response = await axios.get(`${API_BASE_URL}/api/video/providers`);

            if (response.data.success) {
                const providers: VideoProvider[] = response.data.providers;

                // Create webview to display providers
                const panel = vscode.window.createWebviewPanel(
                    'videoProviders',
                    'Video Generation Providers',
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = generateProvidersHTML(providers);
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to load providers: ${error.response?.data?.detail || error.message}`
        );
    }
}

/**
 * View video generations
 */
export async function viewVideoGenerations() {
    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Loading video generations...',
            cancellable: false
        }, async () => {
            const response = await axios.get(`${API_BASE_URL}/api/video/generations`);

            if (response.data.success) {
                const videos: VideoGeneration[] = response.data.videos;

                if (videos.length === 0) {
                    vscode.window.showInformationMessage('No video generations yet.');
                    return;
                }

                // Create webview to display generations
                const panel = vscode.window.createWebviewPanel(
                    'videoGenerations',
                    'Video Generations',
                    vscode.ViewColumn.One,
                    { enableScripts: true }
                );

                panel.webview.html = generateVideosHTML(videos);
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(
            `Failed to load generations: ${error.response?.data?.detail || error.message}`
        );
    }
}

// Helper functions

function generateProvidersHTML(providers: VideoProvider[]): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .provider {
                    border: 1px solid #ddd;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 5px;
                }
                .provider-name { font-size: 18px; font-weight: bold; color: #007acc; }
                .capabilities { margin-top: 10px; }
                .capability {
                    display: inline-block;
                    padding: 4px 8px;
                    margin: 2px;
                    background: #e7f3ff;
                    border-radius: 3px;
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <h1>Video Generation Providers</h1>
            ${providers.map(p => `
                <div class="provider">
                    <div class="provider-name">${p.name}</div>
                    <div><strong>Max Duration:</strong> ${p.max_duration}s</div>
                    <div><strong>Resolutions:</strong> ${p.resolutions.join(', ')}</div>
                    <div class="capabilities">
                        <strong>Capabilities:</strong>
                        ${p.capabilities.map(c => `<span class="capability">${c}</span>`).join('')}
                    </div>
                </div>
            `).join('')}
        </body>
        </html>
    `;
}

function generateVideosHTML(videos: VideoGeneration[]): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #007acc; color: white; }
                .status-completed { color: green; }
                .status-pending { color: orange; }
                .status-failed { color: red; }
            </style>
        </head>
        <body>
            <h1>Video Generations</h1>
            <p>Total: ${videos.length}</p>
            <table>
                <tr>
                    <th>Prompt</th>
                    <th>Provider</th>
                    <th>Duration</th>
                    <th>Resolution</th>
                    <th>Status</th>
                    <th>Created</th>
                </tr>
                ${videos.map(v => `
                    <tr>
                        <td>${v.prompt}</td>
                        <td>${v.provider}</td>
                        <td>${v.duration || 'N/A'}s</td>
                        <td>${v.resolution || 'N/A'}</td>
                        <td class="status-${v.status}">${v.status}</td>
                        <td>${new Date(v.created_at).toLocaleString()}</td>
                    </tr>
                `).join('')}
            </table>
        </body>
        </html>
    `;
}

/**
 * Register all video commands
 */
export function registerVideoCommands(context: vscode.ExtensionContext, apiClient: any) {
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.generateVideoFromText', generateVideoFromText),
        vscode.commands.registerCommand('itechsmart.generateVideoFromImage', generateVideoFromImage),
        vscode.commands.registerCommand('itechsmart.transformVideo', transformVideo),
        vscode.commands.registerCommand('itechsmart.upscaleVideo', upscaleVideo),
        vscode.commands.registerCommand('itechsmart.editVideo', editVideo),
        vscode.commands.registerCommand('itechsmart.listVideoProviders', listVideoProviders),
        vscode.commands.registerCommand('itechsmart.viewVideoGenerations', viewVideoGenerations)
    );
}