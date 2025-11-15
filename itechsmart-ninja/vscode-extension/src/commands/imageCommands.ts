/**
 * Image Commands - VS Code commands for AI image generation
 * Provides text-to-image, image editing, and enhancement
 */

import * as vscode from 'vscode';
import { APIClient } from '../api/client';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Register all image generation commands
 */
export function registerImageCommands(context: vscode.ExtensionContext, apiClient: APIClient) {
    // Text-to-image generation
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.generateImage', () => generateImage(apiClient))
    );
    
    // Image-to-image
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.imageToImage', () => imageToImage(apiClient))
    );
    
    // Image editing
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.inpaintImage', () => inpaintImage(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.createVariations', () => createVariations(apiClient))
    );
    
    // Image enhancement
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.upscaleImage', () => upscaleImage(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.removeBackground', () => removeBackground(apiClient))
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.enhanceFace', () => enhanceFace(apiClient))
    );
    
    // List providers
    context.subscriptions.push(
        vscode.commands.registerCommand('itechsmart.listImageProviders', () => listProviders(apiClient))
    );
}

/**
 * Generate image from text prompt
 */
async function generateImage(apiClient: APIClient) {
    try {
        // Get prompt
        const prompt = await vscode.window.showInputBox({
            prompt: 'Enter image description',
            placeHolder: 'A beautiful sunset over mountains...'
        });
        
        if (!prompt) {
            return;
        }
        
        // Get provider
        const providers = await apiClient.get('/images/providers');
        const availableProviders = providers.providers
            .filter((p: any) => p.available)
            .map((p: any) => ({
                label: p.name,
                value: p.name.toLowerCase().replace(' ', '_')
            }));
        
        if (availableProviders.length === 0) {
            vscode.window.showErrorMessage('No image providers configured. Please set API keys.');
            return;
        }
        
        const provider = await vscode.window.showQuickPick(availableProviders, {
            placeHolder: 'Select image provider'
        });
        
        if (!provider) {
            return;
        }
        
        // Get size
        const sizes = await apiClient.get('/images/sizes');
        const sizeItems = sizes.sizes.map((s: any) => ({
            label: s.label,
            value: s.value
        }));
        
        const size = await vscode.window.showQuickPick(sizeItems, {
            placeHolder: 'Select image size'
        });
        
        if (!size) {
            return;
        }
        
        // Get number of images
        const n = await vscode.window.showInputBox({
            prompt: 'Number of images to generate (1-4)',
            value: '1',
            validateInput: (value) => {
                const num = parseInt(value);
                return (isNaN(num) || num < 1 || num > 4) ? 'Please enter a number between 1 and 4' : null;
            }
        });
        
        if (!n) {
            return;
        }
        
        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Generating images...',
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            
            // Generate images
            const response = await apiClient.post('/images/generate', {
                prompt,
                provider: provider.value,
                size: size.value,
                n: parseInt(n),
                quality: 'standard'
            });
            
            progress.report({ increment: 100 });
            
            // Show results
            showImageResults(response.images, 'Generated Images');
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to generate image: ${error.message}`);
    }
}

/**
 * Image-to-image generation
 */
async function imageToImage(apiClient: APIClient) {
    try {
        // Select image file
        const imageUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectMany: false,
            filters: {
                'Images': ['png', 'jpg', 'jpeg', 'webp']
            }
        });
        
        if (!imageUri || imageUri.length === 0) {
            return;
        }
        
        // Get prompt
        const prompt = await vscode.window.showInputBox({
            prompt: 'Describe the desired changes',
            placeHolder: 'Transform into a watercolor painting...'
        });
        
        if (!prompt) {
            return;
        }
        
        // Get strength
        const strength = await vscode.window.showInputBox({
            prompt: 'Transformation strength (0.0-1.0)',
            value: '0.8',
            validateInput: (value) => {
                const num = parseFloat(value);
                return (isNaN(num) || num < 0 || num > 1) ? 'Please enter a number between 0.0 and 1.0' : null;
            }
        });
        
        if (!strength) {
            return;
        }
        
        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Transforming image...',
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            
            // Read image file
            const imageData = fs.readFileSync(imageUri[0].fsPath);
            
            // Create form data
            const formData = new FormData();
            formData.append('image', new Blob([imageData]), path.basename(imageUri[0].fsPath));
            formData.append('prompt', prompt);
            formData.append('strength', strength);
            formData.append('provider', 'stable_diffusion');
            
            // Transform image
            const response = await apiClient.postFormData('/images/image-to-image', formData);
            
            progress.report({ increment: 100 });
            
            // Show results
            showImageResults(response.images, 'Transformed Images');
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to transform image: ${error.message}`);
    }
}

/**
 * Inpaint image
 */
async function inpaintImage(apiClient: APIClient) {
    try {
        // Select image file
        const imageUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectMany: false,
            filters: {
                'Images': ['png', 'jpg', 'jpeg']
            },
            title: 'Select image to edit'
        });
        
        if (!imageUri || imageUri.length === 0) {
            return;
        }
        
        // Select mask file
        const maskUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectMany: false,
            filters: {
                'Images': ['png', 'jpg', 'jpeg']
            },
            title: 'Select mask (white = fill, black = keep)'
        });
        
        if (!maskUri || maskUri.length === 0) {
            return;
        }
        
        // Get prompt
        const prompt = await vscode.window.showInputBox({
            prompt: 'Describe what to fill in the masked area',
            placeHolder: 'A red apple...'
        });
        
        if (!prompt) {
            return;
        }
        
        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Inpainting image...',
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            
            // Read files
            const imageData = fs.readFileSync(imageUri[0].fsPath);
            const maskData = fs.readFileSync(maskUri[0].fsPath);
            
            // Create form data
            const formData = new FormData();
            formData.append('image', new Blob([imageData]), path.basename(imageUri[0].fsPath));
            formData.append('mask', new Blob([maskData]), path.basename(maskUri[0].fsPath));
            formData.append('prompt', prompt);
            formData.append('provider', 'dalle');
            
            // Inpaint
            const response = await apiClient.postFormData('/images/inpaint', formData);
            
            progress.report({ increment: 100 });
            
            // Show results
            showImageResults(response.images, 'Inpainted Images');
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to inpaint image: ${error.message}`);
    }
}

/**
 * Create image variations
 */
async function createVariations(apiClient: APIClient) {
    try {
        // Select image file
        const imageUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectMany: false,
            filters: {
                'Images': ['png', 'jpg', 'jpeg']
            }
        });
        
        if (!imageUri || imageUri.length === 0) {
            return;
        }
        
        // Get number of variations
        const n = await vscode.window.showInputBox({
            prompt: 'Number of variations (1-4)',
            value: '2',
            validateInput: (value) => {
                const num = parseInt(value);
                return (isNaN(num) || num < 1 || num > 4) ? 'Please enter a number between 1 and 4' : null;
            }
        });
        
        if (!n) {
            return;
        }
        
        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Creating variations...',
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            
            // Read image file
            const imageData = fs.readFileSync(imageUri[0].fsPath);
            
            // Create form data
            const formData = new FormData();
            formData.append('image', new Blob([imageData]), path.basename(imageUri[0].fsPath));
            formData.append('n', n);
            formData.append('provider', 'dalle');
            
            // Create variations
            const response = await apiClient.postFormData('/images/variations', formData);
            
            progress.report({ increment: 100 });
            
            // Show results
            showImageResults(response.images, 'Image Variations');
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to create variations: ${error.message}`);
    }
}

/**
 * Upscale image
 */
async function upscaleImage(apiClient: APIClient) {
    try {
        // Select image file
        const imageUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectMany: false,
            filters: {
                'Images': ['png', 'jpg', 'jpeg']
            }
        });
        
        if (!imageUri || imageUri.length === 0) {
            return;
        }
        
        // Get scale factor
        const scale = await vscode.window.showQuickPick(
            [
                { label: '2x', value: '2' },
                { label: '4x', value: '4' }
            ],
            { placeHolder: 'Select upscale factor' }
        );
        
        if (!scale) {
            return;
        }
        
        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Upscaling image...',
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            
            // Read image file
            const imageData = fs.readFileSync(imageUri[0].fsPath);
            
            // Create form data
            const formData = new FormData();
            formData.append('image', new Blob([imageData]), path.basename(imageUri[0].fsPath));
            formData.append('scale', scale.value);
            
            // Upscale
            const response = await apiClient.postFormData('/images/upscale', formData);
            
            progress.report({ increment: 100 });
            
            // Show result
            showImageResults([response], 'Upscaled Image');
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to upscale image: ${error.message}`);
    }
}

/**
 * Remove background
 */
async function removeBackground(apiClient: APIClient) {
    try {
        // Select image file
        const imageUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectMany: false,
            filters: {
                'Images': ['png', 'jpg', 'jpeg']
            }
        });
        
        if (!imageUri || imageUri.length === 0) {
            return;
        }
        
        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Removing background...',
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            
            // Read image file
            const imageData = fs.readFileSync(imageUri[0].fsPath);
            
            // Create form data
            const formData = new FormData();
            formData.append('image', new Blob([imageData]), path.basename(imageUri[0].fsPath));
            
            // Remove background
            const response = await apiClient.postFormData('/images/remove-background', formData);
            
            progress.report({ increment: 100 });
            
            // Show result
            showImageResults([response], 'Background Removed');
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to remove background: ${error.message}`);
    }
}

/**
 * Enhance face
 */
async function enhanceFace(apiClient: APIClient) {
    try {
        // Select image file
        const imageUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectMany: false,
            filters: {
                'Images': ['png', 'jpg', 'jpeg']
            }
        });
        
        if (!imageUri || imageUri.length === 0) {
            return;
        }
        
        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Enhancing face...',
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            
            // Read image file
            const imageData = fs.readFileSync(imageUri[0].fsPath);
            
            // Create form data
            const formData = new FormData();
            formData.append('image', new Blob([imageData]), path.basename(imageUri[0].fsPath));
            
            // Enhance face
            const response = await apiClient.postFormData('/images/enhance-face', formData);
            
            progress.report({ increment: 100 });
            
            // Show result
            showImageResults([response], 'Face Enhanced');
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to enhance face: ${error.message}`);
    }
}

/**
 * List image providers
 */
async function listProviders(apiClient: APIClient) {
    try {
        const response = await apiClient.get('/images/providers');
        
        const items = response.providers.map((provider: any) => ({
            label: provider.name,
            description: provider.available ? '✓ Available' : '✗ Not configured',
            detail: `Capabilities: ${provider.capabilities.join(', ')}`,
            provider: provider
        }));
        
        await vscode.window.showQuickPick(items, {
            placeHolder: 'Image Generation Providers'
        });
        
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list providers: ${error.message}`);
    }
}

/**
 * Show image results in webview
 */
function showImageResults(images: any[], title: string) {
    const panel = vscode.window.createWebviewPanel(
        'imageResults',
        title,
        vscode.ViewColumn.One,
        { enableScripts: true }
    );
    
    panel.webview.html = getImageResultsHTML(images, title);
}

/**
 * Generate HTML for image results
 */
function getImageResultsHTML(images: any[], title: string): string {
    const imageElements = images.map((img, i) => `
        <div class="image-container">
            <img src="${img.url}" alt="Generated image ${i + 1}">
            <div class="image-info">
                <p><strong>Provider:</strong> ${img.provider}</p>
                ${img.size ? `<p><strong>Size:</strong> ${img.size}</p>` : ''}
                <a href="${img.url}" target="_blank">Open in Browser</a>
            </div>
        </div>
    `).join('');
    
    return `<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>${title}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 20px;
                background: #1e1e1e;
                color: #d4d4d4;
            }
            h1 { color: #4ec9b0; }
            .image-container {
                margin: 20px 0;
                padding: 20px;
                background: #2d2d2d;
                border-radius: 8px;
            }
            img {
                max-width: 100%;
                border-radius: 4px;
            }
            .image-info {
                margin-top: 10px;
            }
            .image-info p {
                margin: 5px 0;
            }
            a {
                color: #4ec9b0;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>${title}</h1>
        ${imageElements}
    </body>
    </html>`;
}