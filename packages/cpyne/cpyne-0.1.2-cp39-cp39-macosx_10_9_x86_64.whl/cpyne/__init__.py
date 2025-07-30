"""
Spine Python ctypes binding package init.
"""

from . import spine_bindings as _b

__all__ = []

_export_names = [
    # Atlas
    "spAtlas_createFromFile", "spAtlas_dispose",

    # JSON Skeleton
    "spSkeletonJson_create", "spSkeletonJson_dispose", "spSkeletonJson_readSkeletonDataFile",

    # Binary Skeleton
    "spSkeletonBinary_create", "spSkeletonBinary_dispose", "spSkeletonBinary_readSkeletonDataFile",

    # Skeleton
    "spSkeleton_create", "spSkeleton_dispose", "spSkeleton_update",
    "spSkeleton_setSkinByName", "spSkeleton_setToSetupPose", "spSkeleton_updateWorldTransform",
    "spSkeleton_findSlot", "spSkeleton_findBone",
    "spSkeleton_getAttachmentForSlotName", "spSkeleton_getAttachmentForSlotIndex",

    # AnimationState
    "spAnimationStateData_create", "spAnimationStateData_dispose",
    "spAnimationState_create", "spAnimationState_dispose",
    "spAnimationState_update", "spAnimationState_apply",
    "spAnimationState_setAnimationByName", "spAnimationState_setVertexEffect", "spAnimationState_setListener",

    # Struct Types (optional)
    "spAtlas", "spSkeletonJson", "spSkeletonBinary", "spSkeletonData", "spSkeleton",
    "spSlot", "spBone", "spAnimationState", "spAnimationStateData", "spEvent"
]

for name in _export_names:
    try:
        globals()[name] = getattr(_b, name)
        __all__.append(name)
    except AttributeError:
        pass  
