#ifndef MANUAL_BINDING_H
#define MANUAL_BINDING_H

typedef struct spSkeletonJson spSkeletonJson;
typedef struct spSkeletonData spSkeletonData;
typedef struct spAtlas spAtlas;
typedef struct spAttachmentLoader spAttachmentLoader;

spSkeletonJson* spSkeletonJson_create(spAtlas* atlas);
spSkeletonJson* spSkeletonJson_createWithLoader(spAttachmentLoader* loader);
void spSkeletonJson_dispose(spSkeletonJson* self);
spSkeletonData* spSkeletonJson_readSkeletonData(spSkeletonJson* self, const char* json);
spSkeletonData* spSkeletonJson_readSkeletonDataFile(spSkeletonJson* self, const char* path);

spAtlas* spAtlas_createFromFile(const char* path, void* rendererObject);
void spAtlas_dispose(spAtlas* atlas);

#endif
