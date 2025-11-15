# Feature 5: Image Generation - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
1. iTechSmart Ninja backend running
2. VS Code with iTechSmart extension installed
3. At least one image generation API key configured

---

## Step 1: Configure API Keys

Add to your `backend/.env` file:

```bash
# For FLUX (Recommended - Best Quality)
REPLICATE_API_KEY=your_replicate_api_key_here

# For DALL-E (Alternative)
OPENAI_API_KEY=your_openai_api_key_here

# For Stable Diffusion (Budget Option)
STABILITY_API_KEY=your_stability_api_key_here
```

**Get API Keys:**
- FLUX/Replicate: https://replicate.com/account/api-tokens
- DALL-E/OpenAI: https://platform.openai.com/api-keys
- Stable Diffusion: https://platform.stability.ai/account/keys

---

## Step 2: Start the Backend

```bash
cd itechsmart-ninja/backend
python -m uvicorn app.main:app --reload
```

Backend will start at `http://localhost:8000`

---

## Step 3: Generate Your First Image

### Option A: Using VS Code Command Palette

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "iTechSmart: Generate Image"
3. Enter your prompt: `"A serene mountain landscape at sunset"`
4. Select provider: `FLUX`
5. Choose size: `1024x1024`
6. Select style: `Photorealistic`
7. Wait 8-12 seconds
8. Image opens automatically! 🎨

### Option B: Using Terminal

1. Press `Ctrl+Shift+I` to open iTechSmart terminal
2. Type: `img-generate`
3. Follow the prompts
4. Done!

### Option C: Using API

```bash
curl -X POST http://localhost:8000/api/image-generation/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "prompt": "A serene mountain landscape at sunset",
    "provider": "flux",
    "size": "1024x1024",
    "style": "photorealistic"
  }'
```

---

## Common Use Cases

### 1. Marketing Material
```
Prompt: "Professional product photography of a smartwatch on marble surface, studio lighting, 4K"
Provider: FLUX Pro
Size: 1024x1024
Style: Photorealistic
```

### 2. Social Media Post
```
Prompt: "Vibrant abstract art with geometric shapes, modern design, colorful"
Provider: DALL-E 3
Size: 1024x1024
Style: Artistic
```

### 3. Website Hero Image
```
Prompt: "Modern tech office space, natural lighting, minimalist design, wide angle"
Provider: FLUX Dev
Size: 1792x1024
Style: Photorealistic
```

### 4. Concept Art
```
Prompt: "Futuristic city skyline at night, cyberpunk style, neon lights, detailed"
Provider: DALL-E 3
Size: 1024x1792
Style: Artistic
```

### 5. Product Mockup
```
Prompt: "iPhone mockup on wooden desk with coffee cup, top view, soft shadows"
Provider: FLUX Pro
Size: 1024x1024
Style: Photorealistic
```

---

## Advanced Operations

### Upscale an Image
1. Command: `iTechSmart: Upscale Image`
2. Select image file
3. Choose scale: `4x`
4. Wait 8-12 seconds
5. High-res image ready!

### Remove Background
1. Command: `iTechSmart: Remove Image Background`
2. Select image
3. Wait 2-4 seconds
4. PNG with transparency downloaded!

### Transform Image
1. Command: `iTechSmart: Transform Image`
2. Select source image
3. Enter prompt: `"Transform into watercolor painting"`
4. Adjust strength: `0.8`
5. View result!

---

## Terminal Commands Reference

```bash
# Generate image
img-generate
generate-image

# Transform image
img-transform
transform-image

# Upscale image
img-upscale
upscale-image

# Remove background
img-remove-bg
remove-background

# List providers
img-providers
list-image-providers

# Help
help
```

---

## Provider Comparison

### When to Use Each Provider

**FLUX Pro** - Best for:
- Professional photography
- Marketing materials
- High-quality product images
- When quality matters most
- Cost: $0.055/image

**FLUX Dev** - Best for:
- General purpose images
- Good balance of quality and cost
- Fast generation needed
- Cost: $0.025/image

**FLUX Schnell** - Best for:
- Quick iterations
- Testing prompts
- Budget-conscious projects
- Cost: $0.003/image

**DALL-E 3** - Best for:
- Creative and artistic images
- Concept art
- When prompt understanding is critical
- Cost: $0.040/image

**DALL-E 2** - Best for:
- Good quality at lower cost
- Variations and editing
- General purpose
- Cost: $0.020/image

**Stable Diffusion SDXL** - Best for:
- Batch generation
- Lowest cost option
- Experimentation
- Cost: $0.0025/image

---

## Troubleshooting

### Issue: "Provider not available"
**Solution:** Check API key is configured in `.env` file

### Issue: "Generation failed"
**Solution:** 
1. Check API key is valid
2. Verify you have credits/quota
3. Try a different provider
4. Check prompt doesn't violate content policy

### Issue: "Image not opening"
**Solution:**
1. Check file was saved successfully
2. Verify file path in response
3. Try opening manually from file system

### Issue: "Slow generation"
**Solution:**
1. This is normal (8-15 seconds typical)
2. Try FLUX Schnell for faster results
3. Check your internet connection

### Issue: "Cost too high"
**Solution:**
1. Use Stable Diffusion SDXL ($0.0025/image)
2. Use FLUX Schnell ($0.003/image)
3. Batch similar requests
4. Test prompts with cheaper models first

---

## Tips for Better Results

### Prompt Engineering

**Good Prompts:**
- Be specific and detailed
- Include style, lighting, mood
- Mention quality (4K, HD, detailed)
- Specify composition (close-up, wide angle)

**Example:**
```
❌ Bad: "A cat"
✅ Good: "Professional photograph of a fluffy orange cat sitting on a windowsill, natural lighting, shallow depth of field, 4K quality"
```

### Style Keywords

**Photorealistic:**
- "professional photography"
- "studio lighting"
- "4K quality"
- "sharp focus"
- "detailed"

**Artistic:**
- "oil painting"
- "watercolor"
- "digital art"
- "concept art"
- "illustration"

**Specific Styles:**
- "cyberpunk"
- "steampunk"
- "minimalist"
- "vintage"
- "modern"

### Negative Prompts

Use negative prompts to avoid unwanted elements:
```json
{
  "prompt": "Beautiful landscape",
  "negative_prompt": "people, text, watermark, blurry, low quality"
}
```

---

## Cost Tracking

### View Your Usage
```bash
# In terminal
status

# Or via API
curl http://localhost:8000/api/image-generation/usage
```

### Set Budget Alerts
```python
# In backend configuration
IMAGE_GENERATION_DAILY_BUDGET=10.00  # $10/day
IMAGE_GENERATION_MONTHLY_BUDGET=200.00  # $200/month
```

---

## Next Steps

1. ✅ Generate your first image
2. ✅ Try different providers
3. ✅ Experiment with styles
4. ✅ Test upscaling
5. ✅ Try background removal
6. ✅ Create variations
7. ✅ Build a workflow

---

## Resources

- **API Documentation**: http://localhost:8000/docs
- **Provider Docs**:
  - FLUX: https://replicate.com/black-forest-labs/flux-pro
  - DALL-E: https://platform.openai.com/docs/guides/images
  - Stable Diffusion: https://platform.stability.ai/docs

---

## Support

Having issues? Check:
1. Backend logs: `backend/logs/`
2. VS Code console: `Help > Toggle Developer Tools`
3. API health: http://localhost:8000/health

---

**You're ready to generate amazing images! 🎨✨**