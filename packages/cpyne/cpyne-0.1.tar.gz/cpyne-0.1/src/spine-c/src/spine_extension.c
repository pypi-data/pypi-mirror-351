#include <spine/extension.h>
#include <stdio.h>
#include <stdlib.h>

void _spAtlasPage_createTexture(spAtlasPage* self, const char* path) {
    // 简单实现：仅存储路径
    self->rendererObject = path ? malloc(strlen(path) + 1) : NULL;
    if (path) strcpy(self->rendererObject, path);
    self->width = 1024; // 默认纹理大小
    self->height = 1024;
}

void _spAtlasPage_disposeTexture(spAtlasPage* self) {
    // 释放存储的路径
    if (self->rendererObject) {
        free(self->rendererObject);
        self->rendererObject = NULL;
    }
}

char* _spUtil_readFile(const char* path, int* length) {
    FILE* file = fopen(path, "rb");
    if (!file) return NULL;

    fseek(file, 0, SEEK_END);
    *length = (int)ftell(file);
    fseek(file, 0, SEEK_SET);

    char* data = (char*)malloc(*length + 1);
    size_t result = fread(data, 1, *length, file);
    fclose(file);

    if (result != *length) {
        free(data);
        return NULL;
    }

    data[*length] = '\0';
    return data;
}