from __future__ import annotations

from ._api_commons import syncer
from ._image import Image


@syncer.wrap
async def build(image: Image) -> str:
    """
    Build an image. The existing async context will be used.

    Example:
    ```
    import union
    image = union.Image("example_image")
    if __name__ == "__main__":
        asyncio.run(union.build.aio(image))
    ```

    :param image: The image(s) to build.
    :return: The image URI.
    """
    from union._internal.imagebuild.image_builder import ImageBuildEngine

    return await ImageBuildEngine.build(image)
