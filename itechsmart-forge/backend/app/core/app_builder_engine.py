"""
iTechSmart Forge - App Builder Engine
Visual app builder with drag-and-drop functionality
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import json
import uuid

from app.models.models import App, Page, Component, User, AppStatus


class AppBuilderEngine:
    """
    Core engine for building applications visually
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_app(
        self,
        owner_id: int,
        name: str,
        description: Optional[str] = None,
        template_id: Optional[int] = None
    ) -> App:
        """
        Create a new application
        """
        # Generate unique slug
        slug = self._generate_slug(name)
        
        # Default theme
        default_theme = {
            "primary_color": "#1976d2",
            "secondary_color": "#dc004e",
            "background_color": "#ffffff",
            "text_color": "#000000",
            "font_family": "Roboto, sans-serif"
        }
        
        # Create app
        app = App(
            owner_id=owner_id,
            name=name,
            slug=slug,
            description=description,
            status=AppStatus.DRAFT.value,
            theme=default_theme,
            layout={"type": "standard", "sidebar": True, "header": True},
            settings={}
        )
        
        self.db.add(app)
        self.db.flush()
        
        # Create default home page
        home_page = Page(
            app_id=app.id,
            name="Home",
            slug="home",
            title="Home",
            is_home=True,
            order=0,
            layout={"type": "grid", "columns": 12},
            components=[],
            styles={},
            scripts={}
        )
        
        self.db.add(home_page)
        self.db.commit()
        self.db.refresh(app)
        
        return app
    
    async def add_page(
        self,
        app_id: int,
        name: str,
        slug: Optional[str] = None,
        title: Optional[str] = None,
        parent_page_id: Optional[int] = None
    ) -> Page:
        """
        Add a new page to an app
        """
        if not slug:
            slug = self._generate_slug(name)
        
        # Get max order
        max_order = self.db.query(Page).filter(
            Page.app_id == app_id
        ).count()
        
        page = Page(
            app_id=app_id,
            name=name,
            slug=slug,
            title=title or name,
            parent_page_id=parent_page_id,
            order=max_order,
            layout={"type": "grid", "columns": 12},
            components=[],
            styles={},
            scripts={}
        )
        
        self.db.add(page)
        self.db.commit()
        self.db.refresh(page)
        
        return page
    
    async def add_component_to_page(
        self,
        page_id: int,
        component_type: str,
        props: Dict[str, Any],
        position: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add a component to a page
        """
        page = self.db.query(Page).filter(Page.id == page_id).first()
        if not page:
            raise ValueError(f"Page {page_id} not found")
        
        # Generate component ID
        component_id = str(uuid.uuid4())
        
        # Create component data
        component_data = {
            "id": component_id,
            "type": component_type,
            "props": props,
            "position": position,
            "styles": {},
            "events": {}
        }
        
        # Add to page components
        components = page.components or []
        components.append(component_data)
        page.components = components
        
        self.db.commit()
        
        return component_data
    
    async def update_component(
        self,
        page_id: int,
        component_id: str,
        props: Optional[Dict[str, Any]] = None,
        position: Optional[Dict[str, Any]] = None,
        styles: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update a component on a page
        """
        page = self.db.query(Page).filter(Page.id == page_id).first()
        if not page:
            raise ValueError(f"Page {page_id} not found")
        
        components = page.components or []
        
        # Find and update component
        for i, comp in enumerate(components):
            if comp.get("id") == component_id:
                if props is not None:
                    comp["props"] = {**comp.get("props", {}), **props}
                if position is not None:
                    comp["position"] = position
                if styles is not None:
                    comp["styles"] = {**comp.get("styles", {}), **styles}
                
                components[i] = comp
                page.components = components
                self.db.commit()
                
                return comp
        
        raise ValueError(f"Component {component_id} not found")
    
    async def delete_component(
        self,
        page_id: int,
        component_id: str
    ) -> bool:
        """
        Delete a component from a page
        """
        page = self.db.query(Page).filter(Page.id == page_id).first()
        if not page:
            raise ValueError(f"Page {page_id} not found")
        
        components = page.components or []
        
        # Filter out the component
        new_components = [c for c in components if c.get("id") != component_id]
        
        if len(new_components) == len(components):
            raise ValueError(f"Component {component_id} not found")
        
        page.components = new_components
        self.db.commit()
        
        return True
    
    async def get_app_structure(
        self,
        app_id: int
    ) -> Dict[str, Any]:
        """
        Get complete app structure
        """
        app = self.db.query(App).filter(App.id == app_id).first()
        if not app:
            raise ValueError(f"App {app_id} not found")
        
        pages = self.db.query(Page).filter(
            Page.app_id == app_id
        ).order_by(Page.order).all()
        
        return {
            "app": {
                "id": app.id,
                "name": app.name,
                "slug": app.slug,
                "description": app.description,
                "status": app.status,
                "theme": app.theme,
                "layout": app.layout,
                "settings": app.settings
            },
            "pages": [
                {
                    "id": page.id,
                    "name": page.name,
                    "slug": page.slug,
                    "title": page.title,
                    "is_home": page.is_home,
                    "order": page.order,
                    "layout": page.layout,
                    "components": page.components,
                    "component_count": len(page.components or [])
                }
                for page in pages
            ]
        }
    
    async def publish_app(
        self,
        app_id: int
    ) -> App:
        """
        Publish an app
        """
        app = self.db.query(App).filter(App.id == app_id).first()
        if not app:
            raise ValueError(f"App {app_id} not found")
        
        app.status = AppStatus.PUBLISHED.value
        app.published_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(app)
        
        return app
    
    async def clone_app(
        self,
        app_id: int,
        new_owner_id: int,
        new_name: Optional[str] = None
    ) -> App:
        """
        Clone an existing app
        """
        original_app = self.db.query(App).filter(App.id == app_id).first()
        if not original_app:
            raise ValueError(f"App {app_id} not found")
        
        # Create new app
        new_app = App(
            owner_id=new_owner_id,
            name=new_name or f"{original_app.name} (Copy)",
            slug=self._generate_slug(new_name or f"{original_app.name}-copy"),
            description=original_app.description,
            status=AppStatus.DRAFT.value,
            theme=original_app.theme,
            layout=original_app.layout,
            settings=original_app.settings
        )
        
        self.db.add(new_app)
        self.db.flush()
        
        # Clone pages
        original_pages = self.db.query(Page).filter(
            Page.app_id == app_id
        ).all()
        
        for original_page in original_pages:
            new_page = Page(
                app_id=new_app.id,
                name=original_page.name,
                slug=original_page.slug,
                title=original_page.title,
                is_home=original_page.is_home,
                order=original_page.order,
                layout=original_page.layout,
                components=original_page.components,
                styles=original_page.styles,
                scripts=original_page.scripts
            )
            self.db.add(new_page)
        
        # Update clone count
        original_app.clone_count += 1
        
        self.db.commit()
        self.db.refresh(new_app)
        
        return new_app
    
    async def get_user_apps(
        self,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get apps owned by a user
        """
        query = self.db.query(App).filter(App.owner_id == user_id)
        
        if status:
            query = query.filter(App.status == status)
        
        apps = query.order_by(desc(App.updated_at)).limit(limit).offset(offset).all()
        
        return [
            {
                "id": app.id,
                "name": app.name,
                "slug": app.slug,
                "description": app.description,
                "status": app.status,
                "version": app.version,
                "created_at": app.created_at.isoformat(),
                "updated_at": app.updated_at.isoformat(),
                "page_count": len(app.pages)
            }
            for app in apps
        ]
    
    def _generate_slug(self, name: str) -> str:
        """
        Generate URL-safe slug from name
        """
        import re
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        
        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while self.db.query(App).filter(App.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    async def export_app(
        self,
        app_id: int
    ) -> Dict[str, Any]:
        """
        Export app as JSON
        """
        structure = await self.get_app_structure(app_id)
        
        # Add data sources
        from app.models.models import DataSource
        data_sources = self.db.query(DataSource).filter(
            DataSource.app_id == app_id
        ).all()
        
        structure["data_sources"] = [
            {
                "name": ds.name,
                "source_type": ds.source_type,
                "connection_config": ds.connection_config
            }
            for ds in data_sources
        ]
        
        return structure