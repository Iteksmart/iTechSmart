"""
iTechSmart Portal Builder Engine
Headless CMS and No-Code platform for building external-facing enterprise portals
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
import asyncpg
import redis
import yaml
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import jinja2
from pydantic import BaseModel
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortalType(Enum):
    CORPORATE_WEBSITE = "corporate_website"
    CUSTOMER_PORTAL = "customer_portal"
    PARTNER_EXTRANET = "partner_extranet"
    ECOMMERCE = "ecommerce"
    SAAS_PRODUCT = "saas_product"
    EDUCATIONAL = "educational"
    HEALTHCARE = "healthcare"
    GOVERNMENT = "government"
    MICROSITE = "microsite"


class ComponentType(Enum):
    HEADER = "header"
    HERO = "hero"
    NAVIGATION = "navigation"
    CONTENT_BLOCK = "content_block"
    FORM = "form"
    GALLERY = "gallery"
    TESTIMONIALS = "testimonials"
    PRICING = "pricing"
    FOOTER = "footer"
    CUSTOM = "custom"


class DeploymentStatus(Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class Portal:
    portal_id: str
    name: str
    domain: Optional[str] = None
    portal_type: PortalType = PortalType.CORPORATE_WEBSITE
    template_id: Optional[str] = None
    description: Optional[str] = None
    owner_id: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deployment_status: DeploymentStatus = DeploymentStatus.DRAFT
    settings: Dict[str, Any] = None
    seo_settings: Dict[str, Any] = None


@dataclass
class PortalComponent:
    component_id: str
    portal_id: str
    component_type: ComponentType
    name: str
    content: Dict[str, Any]
    styles: Dict[str, Any]
    order_index: int = 0
    is_visible: bool = True
    created_at: Optional[datetime] = None


@dataclass
class PortalPage:
    page_id: str
    portal_id: str
    title: str
    slug: str
    content: Dict[str, Any]
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    is_homepage: bool = False
    is_published: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PortalBuilderEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_pool = None
        self.redis_client = None
        self.s3_client = None
        self.cloudfront_client = None
        self.template_cache = {}
        self.component_registry = {}

    async def initialize(self):
        """Initialize all connections and services"""
        try:
            # Database connections
            self.db_pool = await asyncpg.create_pool(
                self.config["database_url"], min_size=5, max_size=20
            )

            # Redis for caching
            self.redis_client = redis.Redis(
                host=self.config["redis_host"],
                port=self.config["redis_port"],
                decode_responses=True,
            )

            # AWS S3 for static assets
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.config["aws_access_key"],
                aws_secret_access_key=self.config["aws_secret_key"],
                region_name=self.config["aws_region"],
            )

            # CloudFront for CDN
            self.cloudfront_client = boto3.client(
                "cloudfront",
                aws_access_key_id=self.config["aws_access_key"],
                aws_secret_access_key=self.config["aws_secret_key"],
                region_name=self.config["aws_region"],
            )

            # Load component registry
            await self._load_component_registry()

            logger.info("Portal Builder Engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Portal Builder Engine: {e}")
            raise

    async def create_portal(self, portal_data: Dict[str, Any]) -> str:
        """Create a new portal"""
        try:
            portal = Portal(
                portal_id=str(uuid.uuid4()),
                name=portal_data["name"],
                domain=portal_data.get("domain"),
                portal_type=PortalType(
                    portal_data.get("portal_type", "corporate_website")
                ),
                template_id=portal_data.get("template_id"),
                description=portal_data.get("description"),
                owner_id=portal_data["owner_id"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                settings=portal_data.get("settings", {}),
                seo_settings=portal_data.get("seo_settings", {}),
            )

            # Store portal in database
            query = """
                INSERT INTO portals 
                (portal_id, name, domain, portal_type, template_id, description,
                 owner_id, created_at, updated_at, deployment_status, settings, seo_settings)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """

            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    query,
                    portal.portal_id,
                    portal.name,
                    portal.domain,
                    portal.portal_type.value,
                    portal.template_id,
                    portal.description,
                    portal.owner_id,
                    portal.created_at,
                    portal.updated_at,
                    portal.deployment_status.value,
                    json.dumps(portal.settings),
                    json.dumps(portal.seo_settings),
                )

            # If template specified, apply template
            if portal.template_id:
                await self._apply_template(portal.portal_id, portal.template_id)

            # Create default homepage
            await self._create_default_homepage(portal.portal_id)

            logger.info(f"Portal {portal.portal_id} created successfully")
            return portal.portal_id

        except Exception as e:
            logger.error(f"Error creating portal: {e}")
            raise

    async def add_component(
        self, portal_id: str, component_data: Dict[str, Any]
    ) -> str:
        """Add component to portal"""
        try:
            component = PortalComponent(
                component_id=str(uuid.uuid4()),
                portal_id=portal_id,
                component_type=ComponentType(component_data["component_type"]),
                name=component_data["name"],
                content=component_data.get("content", {}),
                styles=component_data.get("styles", {}),
                order_index=component_data.get("order_index", 0),
                is_visible=component_data.get("is_visible", True),
                created_at=datetime.now(),
            )

            # Store component in database
            query = """
                INSERT INTO portal_components 
                (component_id, portal_id, component_type, name, content, 
                 styles, order_index, is_visible, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """

            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    query,
                    component.component_id,
                    component.portal_id,
                    component.component_type.value,
                    component.name,
                    json.dumps(component.content),
                    json.dumps(component.styles),
                    component.order_index,
                    component.is_visible,
                    component.created_at,
                )

            # Update portal cache
            await self._update_portal_cache(portal_id)

            return component.component_id

        except Exception as e:
            logger.error(f"Error adding component to portal {portal_id}: {e}")
            raise

    async def create_page(self, portal_id: str, page_data: Dict[str, Any]) -> str:
        """Create a new page in portal"""
        try:
            page = PortalPage(
                page_id=str(uuid.uuid4()),
                portal_id=portal_id,
                title=page_data["title"],
                slug=page_data["slug"],
                content=page_data.get("content", {}),
                meta_description=page_data.get("meta_description"),
                meta_keywords=page_data.get("meta_keywords"),
                is_homepage=page_data.get("is_homepage", False),
                is_published=page_data.get("is_published", False),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            # Store page in database
            query = """
                INSERT INTO portal_pages 
                (page_id, portal_id, title, slug, content, meta_description,
                 meta_keywords, is_homepage, is_published, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """

            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    query,
                    page.page_id,
                    page.portal_id,
                    page.title,
                    page.slug,
                    json.dumps(page.content),
                    page.meta_description,
                    page.meta_keywords,
                    page.is_homepage,
                    page.is_published,
                    page.created_at,
                    page.updated_at,
                )

            # Update portal cache
            await self._update_portal_cache(portal_id)

            return page.page_id

        except Exception as e:
            logger.error(f"Error creating page for portal {portal_id}: {e}")
            raise

    async def generate_portal(self, portal_id: str) -> Dict[str, Any]:
        """Generate complete portal HTML/CSS/JS"""
        try:
            portal = await self._get_portal(portal_id)
            if not portal:
                raise HTTPException(status_code=404, detail="Portal not found")

            # Get all components and pages
            components = await self._get_portal_components(portal_id)
            pages = await self._get_portal_pages(portal_id)

            # Generate HTML structure
            html_content = await self._generate_html(portal, components, pages)

            # Generate CSS styles
            css_content = await self._generate_css(portal, components)

            # Generate JavaScript
            js_content = await self._generate_js(portal, components)

            # Generate sitemap
            sitemap_content = await self._generate_sitemap(portal, pages)

            # Generate robots.txt
            robots_content = await self._generate_robots(portal)

            return {
                "html": html_content,
                "css": css_content,
                "js": js_content,
                "sitemap": sitemap_content,
                "robots": robots_content,
                "portal": asdict(portal),
            }

        except Exception as e:
            logger.error(f"Error generating portal {portal_id}: {e}")
            raise

    async def deploy_portal(
        self, portal_id: str, environment: str = "production"
    ) -> Dict[str, Any]:
        """Deploy portal to specified environment"""
        try:
            portal = await self._get_portal(portal_id)
            if not portal:
                raise HTTPException(status_code=404, detail="Portal not found")

            # Generate portal assets
            generated = await self.generate_portal(portal_id)

            # Deploy to S3
            deployment_result = await self._deploy_to_s3(portal, generated, environment)

            # Update CloudFront if production
            if environment == "production":
                await self._update_cloudfront(deployment_result["domain"])

            # Update portal deployment status
            await self._update_deployment_status(portal_id, DeploymentStatus.PUBLISHED)

            # Generate SEO audit
            seo_audit = await self._run_seo_audit(deployment_result["url"])

            return {
                "portal_id": portal_id,
                "environment": environment,
                "url": deployment_result["url"],
                "domain": deployment_result["domain"],
                "deployment_time": datetime.now().isoformat(),
                "seo_audit": seo_audit,
            }

        except Exception as e:
            logger.error(f"Error deploying portal {portal_id}: {e}")
            raise

    async def optimize_seo(self, portal_id: str) -> Dict[str, Any]:
        """Optimize portal for SEO"""
        try:
            portal = await self._get_portal(portal_id)
            if not portal:
                raise HTTPException(status_code=404, detail="Portal not found")

            pages = await self._get_portal_pages(portal_id)

            optimizations = []

            for page in pages:
                page_optimizations = []

                # Check meta description
                if not page.meta_description or len(page.meta_description) < 50:
                    page_optimizations.append(
                        {
                            "type": "meta_description",
                            "severity": "high",
                            "message": "Missing or short meta description",
                            "recommendation": "Add compelling meta description (150-160 characters)",
                        }
                    )

                # Check title length
                if len(page.title) < 30 or len(page.title) > 60:
                    page_optimizations.append(
                        {
                            "type": "title_length",
                            "severity": "medium",
                            "message": f"Title length {len(page.title)} characters",
                            "recommendation": "Optimize title to 30-60 characters",
                        }
                    )

                # Check for heading structure
                content = (
                    json.loads(page.content)
                    if isinstance(page.content, str)
                    else page.content
                )
                has_h1 = any(
                    "h1" in str(content).lower() for content in content.values()
                )
                if not has_h1:
                    page_optimizations.append(
                        {
                            "type": "heading_structure",
                            "severity": "high",
                            "message": "Missing H1 tag",
                            "recommendation": "Add H1 tag for better SEO structure",
                        }
                    )

                optimizations.append(
                    {
                        "page_id": page.page_id,
                        "page_title": page.title,
                        "optimizations": page_optimizations,
                    }
                )

            # Generate schema markup
            schema_markup = await self._generate_schema_markup(portal, pages)

            return {
                "portal_id": portal_id,
                "optimizations": optimizations,
                "schema_markup": schema_markup,
                "recommendations": await self._get_seo_recommendations(portal),
            }

        except Exception as e:
            logger.error(f"Error optimizing SEO for portal {portal_id}: {e}")
            raise

    async def _get_portal(self, portal_id: str) -> Optional[Portal]:
        """Get portal by ID"""
        try:
            query = """
                SELECT * FROM portals WHERE portal_id = $1
            """

            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(query, portal_id)

            if row:
                return Portal(
                    portal_id=row["portal_id"],
                    name=row["name"],
                    domain=row["domain"],
                    portal_type=PortalType(row["portal_type"]),
                    template_id=row["template_id"],
                    description=row["description"],
                    owner_id=row["owner_id"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    deployment_status=DeploymentStatus(row["deployment_status"]),
                    settings=json.loads(row["settings"]) if row["settings"] else {},
                    seo_settings=(
                        json.loads(row["seo_settings"]) if row["seo_settings"] else {}
                    ),
                )

            return None

        except Exception as e:
            logger.error(f"Error getting portal {portal_id}: {e}")
            return None

    async def _get_portal_components(self, portal_id: str) -> List[PortalComponent]:
        """Get all components for a portal"""
        try:
            query = """
                SELECT * FROM portal_components 
                WHERE portal_id = $1 
                ORDER BY order_index ASC
            """

            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query, portal_id)

            components = []
            for row in rows:
                components.append(
                    PortalComponent(
                        component_id=row["component_id"],
                        portal_id=row["portal_id"],
                        component_type=ComponentType(row["component_type"]),
                        name=row["name"],
                        content=json.loads(row["content"]) if row["content"] else {},
                        styles=json.loads(row["styles"]) if row["styles"] else {},
                        order_index=row["order_index"],
                        is_visible=row["is_visible"],
                        created_at=row["created_at"],
                    )
                )

            return components

        except Exception as e:
            logger.error(f"Error getting components for portal {portal_id}: {e}")
            return []

    async def _get_portal_pages(self, portal_id: str) -> List[PortalPage]:
        """Get all pages for a portal"""
        try:
            query = """
                SELECT * FROM portal_pages 
                WHERE portal_id = $1 
                ORDER BY created_at ASC
            """

            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query, portal_id)

            pages = []
            for row in rows:
                pages.append(
                    PortalPage(
                        page_id=row["page_id"],
                        portal_id=row["portal_id"],
                        title=row["title"],
                        slug=row["slug"],
                        content=json.loads(row["content"]) if row["content"] else {},
                        meta_description=row["meta_description"],
                        meta_keywords=row["meta_keywords"],
                        is_homepage=row["is_homepage"],
                        is_published=row["is_published"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                )

            return pages

        except Exception as e:
            logger.error(f"Error getting pages for portal {portal_id}: {e}")
            return []

    async def _generate_html(
        self, portal: Portal, components: List[PortalComponent], pages: List[PortalPage]
    ) -> str:
        """Generate HTML structure for portal"""
        try:
            # Load base template
            template = await self._load_template(portal.template_id or "default")

            # Generate components HTML
            components_html = ""
            for component in components:
                if component.is_visible:
                    component_html = await self._render_component(component)
                    components_html += component_html

            # Generate navigation
            navigation_html = await self._generate_navigation(pages)

            # Generate footer
            footer_html = await self._generate_footer(portal)

            # Render main template
            html_content = template.render(
                portal=portal,
                components=components_html,
                navigation=navigation_html,
                footer=footer_html,
                pages=pages,
            )

            return html_content

        except Exception as e:
            logger.error(f"Error generating HTML: {e}")
            raise

    async def _generate_css(
        self, portal: Portal, components: List[PortalComponent]
    ) -> str:
        """Generate CSS styles for portal"""
        try:
            css_rules = []

            # Global styles
            css_rules.append(
                f"""
/* Portal: {portal.name} */
* {{ box-sizing: border-box; }}
body {{ 
    font-family: {portal.settings.get('font_family', 'Inter, sans-serif')};
    color: {portal.settings.get('text_color', '#333333')};
    background-color: {portal.settings.get('bg_color', '#ffffff')};
    margin: 0;
    padding: 0;
}}
.container {{ 
    max-width: 1200px; 
    margin: 0 auto; 
    padding: 0 20px; 
}}
            """
            )

            # Component-specific styles
            for component in components:
                component_css = await self._generate_component_css(component)
                css_rules.append(component_css)

            # Responsive styles
            css_rules.append(
                """
@media (max-width: 768px) {
    .container { padding: 0 15px; }
    .grid { grid-template-columns: 1fr; }
}
            """
            )

            return "\n".join(css_rules)

        except Exception as e:
            logger.error(f"Error generating CSS: {e}")
            return ""

    async def _generate_js(
        self, portal: Portal, components: List[PortalComponent]
    ) -> str:
        """Generate JavaScript for portal"""
        try:
            js_code = []

            # Portal initialization
            js_code.append(
                f"""
// Portal: {portal.name}
document.addEventListener('DOMContentLoaded', function() {{
    console.log('Portal {portal.name} loaded');
    
    // Initialize components
    initializeComponents();
    
    // Initialize analytics
    initializeAnalytics('{portal.portal_id}');
    
    // Initialize forms
    initializeForms();
}});
            """
            )

            # Component-specific JavaScript
            for component in components:
                component_js = await self._generate_component_js(component)
                if component_js:
                    js_code.append(component_js)

            # Utility functions
            js_code.append(
                """
function initializeComponents() {
    // Initialize interactive components
    document.querySelectorAll('.interactive-component').forEach(component => {
        // Component initialization logic
    });
}

function initializeAnalytics(portalId) {
    // Analytics tracking
    if (typeof gtag !== 'undefined') {
        gtag('config', 'GA_MEASUREMENT_ID', {
            'custom_map': {'custom_parameter_1': 'portal_id'}
        });
        gtag('event', 'page_view', {'portal_id': portalId});
    }
}

function initializeForms() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // Form submission logic
        });
    });
}
            """
            )

            return "\n".join(js_code)

        except Exception as e:
            logger.error(f"Error generating JavaScript: {e}")
            return ""

    async def _render_component(self, component: PortalComponent) -> str:
        """Render individual component HTML"""
        try:
            component_template = self.component_registry.get(
                component.component_type.value
            )
            if not component_template:
                return f'<div class="component component-{component.component_type.value}" data-id="{component.component_id}">Component not found</div>'

            # Render component with its data
            html = component_template.render(
                component=component, content=component.content, styles=component.styles
            )

            return html

        except Exception as e:
            logger.error(f"Error rendering component {component.component_id}: {e}")
            return f'<div class="component-error">Error rendering component</div>'

    async def _deploy_to_s3(
        self, portal: Portal, generated: Dict[str, Any], environment: str
    ) -> Dict[str, Any]:
        """Deploy portal assets to S3"""
        try:
            bucket_name = f"itechsmart-portals-{environment}"

            # Deploy HTML files for each page
            pages = await self._get_portal_pages(portal.portal_id)

            for page in pages:
                if page.is_published:
                    # Generate page-specific HTML
                    page_html = await self._generate_page_html(portal, page, generated)

                    # Upload to S3
                    key = f"{portal.portal_id}/{page.slug}.html"
                    self.s3_client.put_object(
                        Bucket=bucket_name,
                        Key=key,
                        Body=page_html,
                        ContentType="text/html",
                        CacheControl="max-age=3600",
                    )

            # Upload CSS and JS
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=f"{portal.portal_id}/styles.css",
                Body=generated["css"],
                ContentType="text/css",
            )

            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=f"{portal.portal_id}/scripts.js",
                Body=generated["js"],
                ContentType="application/javascript",
            )

            # Upload sitemap and robots
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=f"{portal.portal_id}/sitemap.xml",
                Body=generated["sitemap"],
                ContentType="application/xml",
            )

            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=f"{portal.portal_id}/robots.txt",
                Body=generated["robots"],
                ContentType="text/plain",
            )

            # Generate domain URL
            domain = portal.domain or f"{portal.portal_id}.itechsmart-portals.com"
            url = f"https://{domain}"

            return {"domain": domain, "url": url, "bucket": bucket_name}

        except Exception as e:
            logger.error(f"Error deploying to S3: {e}")
            raise

    async def _load_component_registry(self):
        """Load component registry with templates"""
        try:
            # Define component templates
            self.component_registry = {
                "header": jinja2.Template(
                    """
<div class="component-header" style="{{ styles.container|default('') }}">
    <div class="container">
        <div class="header-content">
            <div class="logo">
                <h1>{{ content.logo_text|default('Company Name') }}</h1>
            </div>
            <nav class="navigation">
                <ul>
                    {% for item in content.nav_items|default([]) %}
                    <li><a href="{{ item.url }}">{{ item.label }}</a></li>
                    {% endfor %}
                </ul>
            </nav>
        </div>
    </div>
</div>
                """
                ),
                "hero": jinja2.Template(
                    """
<section class="component-hero" style="{{ styles.container|default('') }}">
    <div class="container">
        <div class="hero-content">
            <h2>{{ content.title|default('Welcome to Our Portal') }}</h2>
            <p>{{ content.subtitle|default('Discover amazing experiences') }}</p>
            {% if content.cta_button %}
            <a href="{{ content.cta_button.url|default('#') }}" class="cta-button">
                {{ content.cta_button.text|default('Get Started') }}
            </a>
            {% endif %}
        </div>
        {% if content.background_image %}
        <div class="hero-image">
            <img src="{{ content.background_image }}" alt="{{ content.title }}">
        </div>
        {% endif %}
    </div>
</section>
                """
                ),
                "content_block": jinja2.Template(
                    """
<section class="component-content-block" style="{{ styles.container|default('') }}">
    <div class="container">
        <div class="content-wrapper">
            <h3>{{ content.title|default('Content Title') }}</h3>
            <div class="content-body">
                {{ content.content|default('Content goes here...')|safe }}
            </div>
        </div>
    </div>
</section>
                """
                ),
                "form": jinja2.Template(
                    """
<section class="component-form" style="{{ styles.container|default('') }}">
    <div class="container">
        <div class="form-wrapper">
            <h3>{{ content.title|default('Contact Form') }}</h3>
            <form class="portal-form" data-form-id="{{ component.component_id }}">
                {% for field in content.fields|default([]) %}
                <div class="form-field">
                    <label for="{{ field.name }}">{{ field.label }}</label>
                    {% if field.type == 'textarea' %}
                    <textarea id="{{ field.name }}" name="{{ field.name }}" {% if field.required %}required{% endif %}></textarea>
                    {% else %}
                    <input type="{{ field.type|default('text') }}" id="{{ field.name }}" name="{{ field.name }}" {% if field.required %}required{% endif %}>
                    {% endif %}
                </div>
                {% endfor %}
                <button type="submit" class="submit-button">{{ content.submit_text|default('Submit') }}</button>
            </form>
        </div>
    </div>
</section>
                """
                ),
                "footer": jinja2.Template(
                    """
<footer class="component-footer" style="{{ styles.container|default('') }}">
    <div class="container">
        <div class="footer-content">
            <div class="footer-section">
                <h4>{{ content.company_name|default('Company Name') }}</h4>
                <p>{{ content.description|default('Company description') }}</p>
            </div>
            <div class="footer-section">
                <h4>Quick Links</h4>
                <ul>
                    {% for link in content.quick_links|default([]) %}
                    <li><a href="{{ link.url }}">{{ link.text }}</a></li>
                    {% endfor %}
                </ul>
            </div>
            <div class="footer-section">
                <h4>Contact</h4>
                <p>{{ content.contact_info|default('Contact information') }}</p>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; {{ 'now'|year }} {{ content.company_name|default('Company Name') }}. All rights reserved.</p>
        </div>
    </div>
</footer>
                """
                ),
            }

        except Exception as e:
            logger.error(f"Error loading component registry: {e}")

    async def _load_template(self, template_id: str) -> jinja2.Template:
        """Load portal template"""
        try:
            # Default template
            template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ portal.name }}{% if page and page.title %} - {{ page.title }}{% endif %}</title>
    <meta name="description" content="{{ page.meta_description or portal.seo_settings.get('description', '') }}">
    <meta name="keywords" content="{{ page.meta_keywords or portal.seo_settings.get('keywords', '') }}">
    <link rel="stylesheet" href="/styles.css">
    {% if portal.seo_settings.favicon %}
    <link rel="icon" href="{{ portal.seo_settings.favicon }}">
    {% endif %}
</head>
<body>
    {{ navigation|safe }}
    <main>
        {{ components|safe }}
    </main>
    {{ footer|safe }}
    <script src="/scripts.js"></script>
</body>
</html>
            """

            return jinja2.Template(template_content)

        except Exception as e:
            logger.error(f"Error loading template {template_id}: {e}")
            raise

    async def close(self):
        """Close all connections"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            self.redis_client.close()


# Configuration and initialization
async def main():
    config = {
        "database_url": "postgresql://user:pass@localhost/itechsmart_portals",
        "redis_host": "localhost",
        "redis_port": 6379,
        "aws_access_key": "your_access_key",
        "aws_secret_key": "your_secret_key",
        "aws_region": "us-east-1",
    }

    portal_engine = PortalBuilderEngine(config)
    await portal_engine.initialize()

    try:
        # Keep the service running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down Portal Builder Engine...")
    finally:
        await portal_engine.close()


if __name__ == "__main__":
    asyncio.run(main())
