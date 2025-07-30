#ifndef NVPL_BLAS_F77_BLAS_H
#define NVPL_BLAS_F77_BLAS_H

#include "nvpl_blas_types.h"

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

/* BLAS Auxiliary */

void xerbla_(const char* srname, const nvpl_int_t* info, size_t lsrname) NVPL_BLAS_API;
nvpl_int_t lsame_(const char* ca, const char* cb, size_t lca, size_t lcb) NVPL_BLAS_API;

/* NVPL BLAS Exported API {{{ */


/* BLAS Level 1 */

float sasum_(const nvpl_int_t* n, const float* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void saxpy_(const nvpl_int_t* n, const float* alpha, const float* x, const nvpl_int_t* incx, float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void saxpby_(const nvpl_int_t* n, const float* alpha, const float* x, const nvpl_int_t* incx, const float* beta, float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
float scasum_(const nvpl_int_t* n, const nvpl_scomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
float scnrm2_(const nvpl_int_t* n, const nvpl_scomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void scopy_(const nvpl_int_t* n, const float* x, const nvpl_int_t* incx, float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
float sdot_(const nvpl_int_t* n, const float* x, const nvpl_int_t* incx, const float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
float sdsdot_(const nvpl_int_t* n, const float* sb, const float* x, const nvpl_int_t* incx, const float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
float snrm2_(const nvpl_int_t* n, const float* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void srot_(const nvpl_int_t* n, float* x, const nvpl_int_t* incx, float* y, const nvpl_int_t* incy, const float* c, const float* s) NVPL_BLAS_API;
void srotg_(float* a, float* b, float* c, float* s) NVPL_BLAS_API;
void srotm_(const nvpl_int_t* n, float* x, const nvpl_int_t* incx, float* y, const nvpl_int_t* incy, const float* param) NVPL_BLAS_API;
void srotmg_(float* d1, float* d2, float* x1, const float* y1, float* param) NVPL_BLAS_API;
void sscal_(const nvpl_int_t* n, const float* a, float* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void sswap_(const nvpl_int_t* n, float* x, const nvpl_int_t* incx, float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
nvpl_int_t isamax_(const nvpl_int_t* n, const float* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void caxpy_(const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* x, const nvpl_int_t* incx, nvpl_scomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void caxpby_(const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* beta, nvpl_scomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void ccopy_(const nvpl_int_t* n, const nvpl_scomplex_t* x, const nvpl_int_t* incx, nvpl_scomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
nvpl_scomplex_t cdotc_(const nvpl_int_t* n, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
nvpl_scomplex_t cdotu_(const nvpl_int_t* n, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void crotg_(nvpl_scomplex_t* a, const nvpl_scomplex_t* b, float* c, nvpl_scomplex_t* s) NVPL_BLAS_API;
void cscal_(const nvpl_int_t* n, const nvpl_scomplex_t* a, nvpl_scomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void csrot_(const nvpl_int_t* n, nvpl_scomplex_t* x, const nvpl_int_t* incx, nvpl_scomplex_t* y, const nvpl_int_t* incy, const float* c, const float* s) NVPL_BLAS_API;
void csscal_(const nvpl_int_t* n, const float* a, nvpl_scomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void cswap_(const nvpl_int_t* n, nvpl_scomplex_t* x, const nvpl_int_t* incx, nvpl_scomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
nvpl_int_t icamax_(const nvpl_int_t* n, const nvpl_scomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
double dasum_(const nvpl_int_t* n, const double* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void daxpy_(const nvpl_int_t* n, const double* alpha, const double* x, const nvpl_int_t* incx, double* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void daxpby_(const nvpl_int_t* n, const double* alpha, const double* x, const nvpl_int_t* incx, const double* beta, double* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void dcopy_(const nvpl_int_t* n, const double* x, const nvpl_int_t* incx, double* y, const nvpl_int_t* incy) NVPL_BLAS_API;
double ddot_(const nvpl_int_t* n, const double* x, const nvpl_int_t* incx, const double* y, const nvpl_int_t* incy) NVPL_BLAS_API;
double dsdot_(const nvpl_int_t* n, const float* x, const nvpl_int_t* incx, const float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
double dnrm2_(const nvpl_int_t* n, const double* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void drot_(const nvpl_int_t* n, double* x, const nvpl_int_t* incx, double* y, const nvpl_int_t* incy, const double* c, const double* s) NVPL_BLAS_API;
void drotg_(double* a, double* b, double* c, double* s) NVPL_BLAS_API;
void drotm_(const nvpl_int_t* n, double* x, const nvpl_int_t* incx, double* y, const nvpl_int_t* incy, const double* param) NVPL_BLAS_API;
void drotmg_(double* d1, double* d2, double* x1, const double* y1, double* param) NVPL_BLAS_API;
void dscal_(const nvpl_int_t* n, const double* a, double* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void dswap_(const nvpl_int_t* n, double* x, const nvpl_int_t* incx, double* y, const nvpl_int_t* incy) NVPL_BLAS_API;
double dzasum_(const nvpl_int_t* n, const nvpl_dcomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
double dznrm2_(const nvpl_int_t* n, const nvpl_dcomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
nvpl_int_t idamax_(const nvpl_int_t* n, const double* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void zaxpy_(const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, nvpl_dcomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void zaxpby_(const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void zcopy_(const nvpl_int_t* n, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, nvpl_dcomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
nvpl_dcomplex_t zdotc_(const nvpl_int_t* n, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
nvpl_dcomplex_t zdotu_(const nvpl_int_t* n, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void zdrot_(const nvpl_int_t* n, nvpl_dcomplex_t* x, const nvpl_int_t* incx, nvpl_dcomplex_t* y, const nvpl_int_t* incy, const double* c, const double* s) NVPL_BLAS_API;
void zdscal_(const nvpl_int_t* n, const double* a, nvpl_dcomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void zrotg_(nvpl_dcomplex_t* a, const nvpl_dcomplex_t* b, double* c, nvpl_dcomplex_t* s) NVPL_BLAS_API;
void zscal_(const nvpl_int_t* n, const nvpl_dcomplex_t* a, nvpl_dcomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void zswap_(const nvpl_int_t* n, nvpl_dcomplex_t* x, const nvpl_int_t* incx, nvpl_dcomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
nvpl_int_t izamax_(const nvpl_int_t* n, const nvpl_dcomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;

/* BLAS Level 2 */

void sgbmv_(const char* trans, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* kl, const nvpl_int_t* ku, const float* alpha, const float* a, const nvpl_int_t* lda, const float* x, const nvpl_int_t* incx, const float* beta, float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void sgemv_(const char* trans, const nvpl_int_t* m, const nvpl_int_t* n, const float* alpha, const float* a, const nvpl_int_t* lda, const float* x, const nvpl_int_t* incx, const float* beta, float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void sger_(const nvpl_int_t* m, const nvpl_int_t* n, const float* alpha, const float* x, const nvpl_int_t* incx, const float* y, const nvpl_int_t* incy, float* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void ssbmv_(const char* uplo, const nvpl_int_t* n, const nvpl_int_t* k, const float* alpha, const float* a, const nvpl_int_t* lda, const float* x, const nvpl_int_t* incx, const float* beta, float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void sspmv_(const char* uplo, const nvpl_int_t* n, const float* alpha, const float* ap, const float* x, const nvpl_int_t* incx, const float* beta, float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void sspr_(const char* uplo, const nvpl_int_t* n, const float* alpha, const float* x, const nvpl_int_t* incx, float* ap) NVPL_BLAS_API;
void sspr2_(const char* uplo, const nvpl_int_t* n, const float* alpha, const float* x, const nvpl_int_t* incx, const float* y, const nvpl_int_t* incy, float* ap) NVPL_BLAS_API;
void ssymv_(const char* uplo, const nvpl_int_t* n, const float* alpha, const float* a, const nvpl_int_t* lda, const float* x, const nvpl_int_t* incx, const float* beta, float* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void ssyr_(const char* uplo, const nvpl_int_t* n, const float* alpha, const float* x, const nvpl_int_t* incx, float* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void ssyr2_(const char* uplo, const nvpl_int_t* n, const float* alpha, const float* x, const nvpl_int_t* incx, const float* y, const nvpl_int_t* incy, float* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void stbmv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_int_t* k, const float* a, const nvpl_int_t* lda, float* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void stbsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_int_t* k, const float* a, const nvpl_int_t* lda, float* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void stpmv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const float* ap, float* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void stpsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const float* ap, float* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void strmv_(const char* uplo, const char* transa, const char* diag, const nvpl_int_t* n, const float* a, const nvpl_int_t* lda, float* b, const nvpl_int_t* incx) NVPL_BLAS_API;
void strsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const float* a, const nvpl_int_t* lda, float* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void cgbmv_(const char* trans, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* kl, const nvpl_int_t* ku, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* beta, nvpl_scomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void cgemv_(const char* trans, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* beta, nvpl_scomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void cgerc_(const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* y, const nvpl_int_t* incy, nvpl_scomplex_t* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void cgeru_(const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* y, const nvpl_int_t* incy, nvpl_scomplex_t* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void chbmv_(const char* uplo, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* beta, nvpl_scomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void chemv_(const char* uplo, const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* beta, nvpl_scomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void cher_(const char* uplo, const nvpl_int_t* n, const float* alpha, const nvpl_scomplex_t* x, const nvpl_int_t* incx, nvpl_scomplex_t* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void cher2_(const char* uplo, const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* y, const nvpl_int_t* incy, nvpl_scomplex_t* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void chpmv_(const char* uplo, const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* ap, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* beta, nvpl_scomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void chpr_(const char* uplo, const nvpl_int_t* n, const float* alpha, const nvpl_scomplex_t* x, const nvpl_int_t* incx, nvpl_scomplex_t* ap) NVPL_BLAS_API;
void chpr2_(const char* uplo, const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* x, const nvpl_int_t* incx, const nvpl_scomplex_t* y, const nvpl_int_t* incy, nvpl_scomplex_t* ap) NVPL_BLAS_API;
void ctbmv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_scomplex_t* a, const nvpl_int_t* lda, nvpl_scomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void ctbsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_scomplex_t* a, const nvpl_int_t* lda, nvpl_scomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void ctpmv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_scomplex_t* ap, nvpl_scomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void ctpsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_scomplex_t* ap, nvpl_scomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void ctrmv_(const char* uplo, const char* transa, const char* diag, const nvpl_int_t* n, const nvpl_scomplex_t* a, const nvpl_int_t* lda, nvpl_scomplex_t* b, const nvpl_int_t* incx) NVPL_BLAS_API;
void ctrsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_scomplex_t* a, const nvpl_int_t* lda, nvpl_scomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void dgbmv_(const char* trans, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* kl, const nvpl_int_t* ku, const double* alpha, const double* a, const nvpl_int_t* lda, const double* x, const nvpl_int_t* incx, const double* beta, double* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void dgemv_(const char* trans, const nvpl_int_t* m, const nvpl_int_t* n, const double* alpha, const double* a, const nvpl_int_t* lda, const double* x, const nvpl_int_t* incx, const double* beta, double* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void dger_(const nvpl_int_t* m, const nvpl_int_t* n, const double* alpha, const double* x, const nvpl_int_t* incx, const double* y, const nvpl_int_t* incy, double* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void dsbmv_(const char* uplo, const nvpl_int_t* n, const nvpl_int_t* k, const double* alpha, const double* a, const nvpl_int_t* lda, const double* x, const nvpl_int_t* incx, const double* beta, double* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void dspmv_(const char* uplo, const nvpl_int_t* n, const double* alpha, const double* ap, const double* x, const nvpl_int_t* incx, const double* beta, double* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void dspr_(const char* uplo, const nvpl_int_t* n, const double* alpha, const double* x, const nvpl_int_t* incx, double* ap) NVPL_BLAS_API;
void dspr2_(const char* uplo, const nvpl_int_t* n, const double* alpha, const double* x, const nvpl_int_t* incx, const double* y, const nvpl_int_t* incy, double* ap) NVPL_BLAS_API;
void dsymv_(const char* uplo, const nvpl_int_t* n, const double* alpha, const double* a, const nvpl_int_t* lda, const double* x, const nvpl_int_t* incx, const double* beta, double* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void dsyr_(const char* uplo, const nvpl_int_t* n, const double* alpha, const double* x, const nvpl_int_t* incx, double* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void dsyr2_(const char* uplo, const nvpl_int_t* n, const double* alpha, const double* x, const nvpl_int_t* incx, const double* y, const nvpl_int_t* incy, double* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void dtbmv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_int_t* k, const double* a, const nvpl_int_t* lda, double* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void dtbsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_int_t* k, const double* a, const nvpl_int_t* lda, double* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void dtpmv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const double* ap, double* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void dtpsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const double* ap, double* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void dtrmv_(const char* uplo, const char* transa, const char* diag, const nvpl_int_t* n, const double* a, const nvpl_int_t* lda, double* b, const nvpl_int_t* incx) NVPL_BLAS_API;
void dtrsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const double* a, const nvpl_int_t* lda, double* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void zgbmv_(const char* trans, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* kl, const nvpl_int_t* ku, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void zgemv_(const char* trans, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void zgerc_(const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* y, const nvpl_int_t* incy, nvpl_dcomplex_t* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void zgeru_(const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* y, const nvpl_int_t* incy, nvpl_dcomplex_t* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void zhbmv_(const char* uplo, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void zhemv_(const char* uplo, const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void zher_(const char* uplo, const nvpl_int_t* n, const double* alpha, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, nvpl_dcomplex_t* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void zher2_(const char* uplo, const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* y, const nvpl_int_t* incy, nvpl_dcomplex_t* a, const nvpl_int_t* lda) NVPL_BLAS_API;
void zhpmv_(const char* uplo, const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* ap, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* y, const nvpl_int_t* incy) NVPL_BLAS_API;
void zhpr_(const char* uplo, const nvpl_int_t* n, const double* alpha, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, nvpl_dcomplex_t* ap) NVPL_BLAS_API;
void zhpr2_(const char* uplo, const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* x, const nvpl_int_t* incx, const nvpl_dcomplex_t* y, const nvpl_int_t* incy, nvpl_dcomplex_t* ap) NVPL_BLAS_API;
void ztbmv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, nvpl_dcomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void ztbsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, nvpl_dcomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void ztpmv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_dcomplex_t* ap, nvpl_dcomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void ztpsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_dcomplex_t* ap, nvpl_dcomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;
void ztrmv_(const char* uplo, const char* transa, const char* diag, const nvpl_int_t* n, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, nvpl_dcomplex_t* b, const nvpl_int_t* incx) NVPL_BLAS_API;
void ztrsv_(const char* uplo, const char* trans, const char* diag, const nvpl_int_t* n, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, nvpl_dcomplex_t* x, const nvpl_int_t* incx) NVPL_BLAS_API;

/* BLAS Level 3 */

void sgemm_(const char* transa, const char* transb, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* k, const float* alpha, const float* a, const nvpl_int_t* lda, const float* b, const nvpl_int_t* ldb, const float* beta, float* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void sgemm_batch_(const char* transa_array, const char* transb_array, const nvpl_int_t* m_array, const nvpl_int_t* n_array, const nvpl_int_t* k_array, const float* alpha_array, const float** a_array, const nvpl_int_t* lda_array, const float** b_array, const nvpl_int_t* ldb_array, const float* beta_array, float** c_array, const nvpl_int_t* ldc_array, const nvpl_int_t* group_count, const nvpl_int_t* group_size) NVPL_BLAS_API;
void sgemm_batch_strided_(const char* transa, const char* transb, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* k, const float* alpha, const float* a, const nvpl_int_t* lda, const nvpl_int_t* stridea, const float* b, const nvpl_int_t* ldb, const nvpl_int_t* strideb, const float* beta, float* c, const nvpl_int_t* ldc, const nvpl_int_t* stridec, const nvpl_int_t* batch_size) NVPL_BLAS_API;
void ssymm_(const char* side, const char* uplo, const nvpl_int_t* m, const nvpl_int_t* n, const float* alpha, const float* a, const nvpl_int_t* lda, const float* b, const nvpl_int_t* ldb, const float* beta, float* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void ssyr2k_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const float* alpha, const float* a, const nvpl_int_t* lda, const float* b, const nvpl_int_t* ldb, const float* beta, float* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void ssyrk_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const float* alpha, const float* a, const nvpl_int_t* lda, const float* beta, float* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void strmm_(const char* side, const char* uplo, const char* transa, const char* diag, const nvpl_int_t* m, const nvpl_int_t* n, const float* alpha, const float* a, const nvpl_int_t* lda, float* b, const nvpl_int_t* ldb) NVPL_BLAS_API;
void strsm_(const char* side, const char* uplo, const char* transa, const char* diag, const nvpl_int_t* m, const nvpl_int_t* n, const float* alpha, const float* a, const nvpl_int_t* lda, float* b, const nvpl_int_t* ldb) NVPL_BLAS_API;
void cgemm_(const char* transa, const char* transb, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* b, const nvpl_int_t* ldb, const nvpl_scomplex_t* beta, nvpl_scomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void cgemm3m_(const char* transa, const char* transb, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* b, const nvpl_int_t* ldb, const nvpl_scomplex_t* beta, nvpl_scomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void cgemm_batch_(const char* transa_array, const char* transb_array, const nvpl_int_t* m_array, const nvpl_int_t* n_array, const nvpl_int_t* k_array, const nvpl_scomplex_t* alpha_array, const nvpl_scomplex_t** a_array, const nvpl_int_t* lda_array, const nvpl_scomplex_t** b_array, const nvpl_int_t* ldb_array, const nvpl_scomplex_t* beta_array, nvpl_scomplex_t** c_array, const nvpl_int_t* ldc_array, const nvpl_int_t* group_count, const nvpl_int_t* group_size) NVPL_BLAS_API;
void cgemm_batch_strided_(const char* transa, const char* transb, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_int_t* stridea, const nvpl_scomplex_t* b, const nvpl_int_t* ldb, const nvpl_int_t* strideb, const nvpl_scomplex_t* beta, nvpl_scomplex_t* c, const nvpl_int_t* ldc, const nvpl_int_t* stridec, const nvpl_int_t* batch_size) NVPL_BLAS_API;
void cgemmt_(const char* uplo, const char* transa, const char* transb, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* b, const nvpl_int_t* ldb, const nvpl_scomplex_t* beta, nvpl_scomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void chemm_(const char* side, const char* uplo, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* b, const nvpl_int_t* ldb, const nvpl_scomplex_t* beta, nvpl_scomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void cher2k_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* b, const nvpl_int_t* ldb, const float* beta, nvpl_scomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void cherk_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const float* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const float* beta, nvpl_scomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void csymm_(const char* side, const char* uplo, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* b, const nvpl_int_t* ldb, const nvpl_scomplex_t* beta, nvpl_scomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void csyr2k_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* b, const nvpl_int_t* ldb, const nvpl_scomplex_t* beta, nvpl_scomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void csyrk_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, const nvpl_scomplex_t* beta, nvpl_scomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void ctrmm_(const char* side, const char* uplo, const char* transa, const char* diag, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, nvpl_scomplex_t* b, const nvpl_int_t* ldb) NVPL_BLAS_API;
void ctrsm_(const char* side, const char* uplo, const char* transa, const char* diag, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_scomplex_t* alpha, const nvpl_scomplex_t* a, const nvpl_int_t* lda, nvpl_scomplex_t* b, const nvpl_int_t* ldb) NVPL_BLAS_API;
void dgemm_(const char* transa, const char* transb, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* k, const double* alpha, const double* a, const nvpl_int_t* lda, const double* b, const nvpl_int_t* ldb, const double* beta, double* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void dgemm_batch_(const char* transa_array, const char* transb_array, const nvpl_int_t* m_array, const nvpl_int_t* n_array, const nvpl_int_t* k_array, const double* alpha_array, const double** a_array, const nvpl_int_t* lda_array, const double** b_array, const nvpl_int_t* ldb_array, const double* beta_array, double** c_array, const nvpl_int_t* ldc_array, const nvpl_int_t* group_count, const nvpl_int_t* group_size) NVPL_BLAS_API;
void dgemm_batch_strided_(const char* transa, const char* transb, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* k, const double* alpha, const double* a, const nvpl_int_t* lda, const nvpl_int_t* stridea, const double* b, const nvpl_int_t* ldb, const nvpl_int_t* strideb, const double* beta, double* c, const nvpl_int_t* ldc, const nvpl_int_t* stridec, const nvpl_int_t* batch_size) NVPL_BLAS_API;
void dsymm_(const char* side, const char* uplo, const nvpl_int_t* m, const nvpl_int_t* n, const double* alpha, const double* a, const nvpl_int_t* lda, const double* b, const nvpl_int_t* ldb, const double* beta, double* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void dsyr2k_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const double* alpha, const double* a, const nvpl_int_t* lda, const double* b, const nvpl_int_t* ldb, const double* beta, double* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void dsyrk_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const double* alpha, const double* a, const nvpl_int_t* lda, const double* beta, double* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void dtrmm_(const char* side, const char* uplo, const char* transa, const char* diag, const nvpl_int_t* m, const nvpl_int_t* n, const double* alpha, const double* a, const nvpl_int_t* lda, double* b, const nvpl_int_t* ldb) NVPL_BLAS_API;
void dtrsm_(const char* side, const char* uplo, const char* transa, const char* diag, const nvpl_int_t* m, const nvpl_int_t* n, const double* alpha, const double* a, const nvpl_int_t* lda, double* b, const nvpl_int_t* ldb) NVPL_BLAS_API;
void zgemm_(const char* transa, const char* transb, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* b, const nvpl_int_t* ldb, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void zgemm3m_(const char* transa, const char* transb, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* b, const nvpl_int_t* ldb, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void zgemm_batch_(const char* transa_array, const char* transb_array, const nvpl_int_t* m_array, const nvpl_int_t* n_array, const nvpl_int_t* k_array, const nvpl_dcomplex_t* alpha_array, const nvpl_dcomplex_t** a_array, const nvpl_int_t* lda_array, const nvpl_dcomplex_t** b_array, const nvpl_int_t* ldb_array, const nvpl_dcomplex_t* beta_array, nvpl_dcomplex_t** c_array, const nvpl_int_t* ldc_array, const nvpl_int_t* group_count, const nvpl_int_t* group_size) NVPL_BLAS_API;
void zgemm_batch_strided_(const char* transa, const char* transb, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_int_t* stridea, const nvpl_dcomplex_t* b, const nvpl_int_t* ldb, const nvpl_int_t* strideb, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* c, const nvpl_int_t* ldc, const nvpl_int_t* stridec, const nvpl_int_t* batch_size) NVPL_BLAS_API;
void zgemmt_(const char* uplo, const char* transa, const char* transb, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* b, const nvpl_int_t* ldb, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void zhemm_(const char* side, const char* uplo, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* b, const nvpl_int_t* ldb, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void zher2k_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* b, const nvpl_int_t* ldb, const double* beta, nvpl_dcomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void zherk_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const double* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const double* beta, nvpl_dcomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void zsymm_(const char* side, const char* uplo, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* b, const nvpl_int_t* ldb, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void zsyr2k_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* b, const nvpl_int_t* ldb, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void zsyrk_(const char* uplo, const char* trans, const nvpl_int_t* n, const nvpl_int_t* k, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, const nvpl_dcomplex_t* beta, nvpl_dcomplex_t* c, const nvpl_int_t* ldc) NVPL_BLAS_API;
void ztrmm_(const char* side, const char* uplo, const char* transa, const char* diag, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, nvpl_dcomplex_t* b, const nvpl_int_t* ldb) NVPL_BLAS_API;
void ztrsm_(const char* side, const char* uplo, const char* transa, const char* diag, const nvpl_int_t* m, const nvpl_int_t* n, const nvpl_dcomplex_t* alpha, const nvpl_dcomplex_t* a, const nvpl_int_t* lda, nvpl_dcomplex_t* b, const nvpl_int_t* ldb) NVPL_BLAS_API;

/* }}} NVPL BLAS Exported API */

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif
