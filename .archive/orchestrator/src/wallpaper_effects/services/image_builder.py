"""Image builder service for building container images."""


from container_manager import BuildContext, ContainerEngine

from wallpaper_effects.config import OrchestratorConfig
from wallpaper_effects.utils.passthrough import get_backend_dockerfile


class ImageBuilder:
    """Builds container images for wallpaper effects backends."""

    def __init__(
        self,
        config: OrchestratorConfig,
        engine: ContainerEngine,
    ):
        """
        Initialize the image builder.

        Args:
            config: Orchestrator configuration
            engine: Container engine instance
        """
        self.config = config
        self.engine = engine

    def build_backend_image(
        self,
        backend: str,
        tag: str | None = None,
        force: bool = False,
    ) -> str:
        """
        Build container image for a backend.

        Args:
            backend: Backend name (imagemagick, pil)
            tag: Optional custom tag for the image
            force: Force rebuild even if image exists

        Returns:
            Image ID of the built image

        Raises:
            ValueError: If backend is not recognized
            ImageBuildError: If build fails
        """
        image_tag = tag or f"wallpaper-effects-{backend}:latest"

        # Check if image already exists
        if not force:
            if self.engine.images.exists(image_tag):
                if self.config.verbose:
                    print(f"Image {image_tag} already exists, skipping")
                info = self.engine.images.inspect(image_tag)
                return info.id

        # Get Dockerfile path
        dockerfile = get_backend_dockerfile(backend)

        # Get project root (parent of orchestrator directory)
        project_root = dockerfile.parent.parent.parent

        # Create build context
        context = BuildContext(
            dockerfile=dockerfile,
            context_path=project_root,
            no_cache=force,
        )

        if self.config.verbose:
            print(f"Building image {image_tag} from {dockerfile}")

        # Build the image
        image_id = self.engine.images.build(context, image_tag)

        if self.config.verbose:
            print(f"Successfully built image: {image_id}")

        return image_id

    def image_exists(self, backend: str) -> bool:
        """
        Check if image for backend exists.

        Args:
            backend: Backend name

        Returns:
            True if image exists
        """
        image_tag = f"wallpaper-effects-{backend}:latest"
        return self.engine.images.exists(image_tag)

    def get_image_info(self, backend: str) -> dict | None:
        """
        Get information about backend image.

        Args:
            backend: Backend name

        Returns:
            Image info dict or None if not found
        """
        image_tag = f"wallpaper-effects-{backend}:latest"
        try:
            if self.engine.images.exists(image_tag):
                info = self.engine.images.inspect(image_tag)
                return {
                    "id": info.id,
                    "tags": info.tags,
                    "size": info.size,
                    "created": info.created,
                }
        except Exception:
            pass
        return None
