#ifndef NVPL_BLAS_TYPES_H
#define NVPL_BLAS_TYPES_H

#include <stddef.h>
#include <stdint.h>

#ifndef NVPL_BLAS_CONFIG_H_FILE
#define NVPL_BLAS_CONFIG_H_FILE "nvpl_blas_config.h"
#endif
#include NVPL_BLAS_CONFIG_H_FILE

#if defined(_WIN32)
#define NVPL_BLAS_DLL_EXPORT __declspec(dllexport)
#elif defined(__GNUC__) && __GNUC__ >= 4
#define NVPL_BLAS_DLL_EXPORT __attribute__((visibility("default")))
#else
#define NVPL_BLAS_DLL_EXPORT
#endif

#if defined(NVPL_BLAS_DLL)
#define NVPL_BLAS_API NVPL_BLAS_DLL_EXPORT
#else
#define NVPL_BLAS_API
#endif

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

#ifndef nvpl_scomplex_t
typedef struct {
    float real;
    float imag;
} nvpl_scomplex_t;
#endif /* nvpl_scomplex_t */

#ifndef nvpl_dcomplex_t
typedef struct {
    double real;
    double imag;
} nvpl_dcomplex_t;
#endif /* nvpl_dcomplex_t */

typedef int64_t nvpl_int64_t;
typedef int32_t nvpl_int32_t;

#ifdef NVPL_ILP64
typedef nvpl_int64_t nvpl_int_t;
#else
typedef nvpl_int32_t nvpl_int_t;
#endif

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif
